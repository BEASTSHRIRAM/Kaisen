"""
Agent Response Gymnasium Environment — Layer 2 of the Kaisen monitoring system.

Mirrors incident_env.py (Layer 1) in structure, contract, and reward-shaping
conventions. The existing DQNAgent and BaselineAgent are used without any
modification.

Key differences vs. incident_env.py
────────────────────────────────────
  • Observation space: 12D (vs. 13D OS space) — defined in agent_telemetry.py
  • Action space:  5 defender interventions scoped to LLM session control
  • False-positive penalty: −20 (vs. −10 in OS env) — reflecting the high
    operational cost of disrupting a legitimate agent workflow
  • Terminal state: SUCCESSFUL_LEAK (irreversible, like DATA_LOSS)
  • Simulator: JailbreakSimulator (vs. CombinedAttackSimulator)

Action Space
────────────
  0  do_nothing              Observe only
  1  rate_limit_session      Throttle API call rate for this session
  2  inject_clarifying_prompt Insert system-level clarification turn
  3  escalate_to_human       Flag to human reviewer queue (soft intervention)
  4  terminate_session       End session immediately (hard intervention)

Reward Table
────────────
  early_containment:   +50   (PROBING stopped before EXTRACTION_ATTEMPT)
  late_containment:    +20   (EXTRACTION_ATTEMPT stopped before LEAK)
  correct_no_action:   +1    (NORMAL state, no intervention taken)
  false_positive:      −20   (intervention on NORMAL session) ← heavier weight
  leak_occurred:       −50   (SUCCESSFUL_LEAK reached)
  unnecessary_action:  −5    (intervention that didn't help)
  step_penalty:        −0.1  (efficiency incentive)
"""

import sys
from collections import deque
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import numpy as np
import gymnasium as gym
from gymnasium import spaces

_HERE = Path(__file__).parent
if str(_HERE.parent) not in sys.path:
    sys.path.insert(0, str(_HERE.parent))

from src.agent_telemetry import (
    AgentSessionObservation,
    AgentSessionSnapshot,
    OBS_DIM,
    OBS_LOW,
    OBS_HIGH,
    OBS_NAMES,
)
from src.jailbreak_simulator import JailbreakSimulator, JailbreakState


# ---------------------------------------------------------------------------
# Action labels (for logging and SHAP explanations)
# ---------------------------------------------------------------------------

ACTION_NAMES = [
    "do_nothing",
    "rate_limit_session",
    "inject_clarifying_prompt",
    "escalate_to_human",
    "terminate_session",
]


# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------

class AgentResponseEnv(gym.Env):
    """
    Gymnasium environment for automated LLM-session incident response.

    The DQNAgent from agent.py is used without modification — it reads
    state_size = env.observation_space.shape[0] = 12 at construction time.

    Episode lifecycle:
      reset()  → returns (12D obs, info)
      step(a)  → returns (12D obs, reward, terminated, truncated, info)

    terminated = True when:
      • Defender terminates the session (action 4)
      • Simulator reaches SUCCESSFUL_LEAK state
      • max_steps is reached

    Attributes:
        simulator:          JailbreakSimulator FSM
        observation_space:  Box(12,) float32
        action_space:       Discrete(5)
    """

    metadata = {"render_modes": ["human", "ansi"]}

    def __init__(
        self,
        max_steps: int = 100,
        obs_noise_std: float = 0.5,
        moving_avg_window: int = 5,
        high_activity_threshold: int = 3,
        rewards: Optional[Dict[str, float]] = None,
        seed: Optional[int] = None,
    ) -> None:
        """
        Args:
            max_steps:               Steps per episode.
            obs_noise_std:           Gaussian noise σ added to raw observations
                                     (dims 0-9 only; binary/time dims untouched).
            moving_avg_window:       Window for MA dims 8-9.
            high_activity_threshold: Steps above threshold before sustained_indicator=1.
            rewards:                 Override reward table (partial dict accepted).
            seed:                    RNG seed.
        """
        super().__init__()

        self.max_steps = max_steps
        self.obs_noise_std = obs_noise_std
        self.moving_avg_window = moving_avg_window
        self.high_activity_threshold = high_activity_threshold

        # Default reward table — FP penalty deliberately heavier than OS env
        self.rewards: Dict[str, float] = {
            "early_containment":   50.0,
            "late_containment":    20.0,
            "correct_no_action":    1.0,
            "false_positive":     -20.0,   # heavier than OS env's -10
            "leak_occurred":      -50.0,
            "unnecessary_action":  -5.0,
            "step_penalty":        -0.1,
        }
        if rewards:
            self.rewards.update(rewards)

        # Gymnasium spaces
        self.observation_space = spaces.Box(
            low=OBS_LOW, high=OBS_HIGH, dtype=np.float32
        )
        self.action_space = spaces.Discrete(5)

        # Simulator
        self.simulator = JailbreakSimulator()

        # History buffers for moving averages
        self._tcr_history: deque = deque(maxlen=moving_avg_window)
        self._rr_history:  deque = deque(maxlen=moving_avg_window)

        # Episode state
        self.current_step: int = 0
        self._high_activity_counter: int = 0
        self._last_snapshot: Optional[AgentSessionSnapshot] = None
        self._episode_stats: Dict[str, int] = {}

        # Seed RNG
        if seed is not None:
            np.random.seed(seed)

    # ------------------------------------------------------------------ #
    # Gymnasium API                                                        #
    # ------------------------------------------------------------------ #

    def reset(
        self,
        *,
        seed: Optional[int] = None,
        options: Optional[Dict] = None,
    ) -> Tuple[np.ndarray, Dict]:
        super().reset(seed=seed)
        if seed is not None:
            np.random.seed(seed)

        self.simulator.reset()
        self.current_step = 0
        self._high_activity_counter = 0
        self._tcr_history.clear()
        self._rr_history.clear()
        self._episode_stats = {
            "attacks_contained":  0,
            "false_positives":    0,
            "leak_events":        0,
            "missed_attacks":     0,
            "interventions":      0,
        }

        # Warm-start history buffers with one simulator step (no action)
        snapshot, _ = self.simulator.step(None)
        self._last_snapshot = snapshot
        self._tcr_history.append(snapshot.tool_call_rate)
        self._rr_history.append(snapshot.refusal_rate)

        obs = self._build_obs()
        return obs, {"episode_stats": dict(self._episode_stats)}

    def step(
        self, action: int
    ) -> Tuple[np.ndarray, float, bool, bool, Dict]:
        """
        Apply defender action and advance the simulator one step.

        Returns:
            (obs, reward, terminated, truncated, info)
        """
        self.current_step += 1

        # Pass action to simulator
        snapshot, contained = self.simulator.step(action)
        self._last_snapshot = snapshot

        # Update history buffers
        self._tcr_history.append(snapshot.tool_call_rate)
        self._rr_history.append(snapshot.refusal_rate)

        # Update sustained-activity counter
        self._update_sustained_counter(snapshot)

        # Compute reward
        reward = self._calculate_reward(action, contained)

        # Update episode stats
        self._update_stats(action, contained)

        # Build next observation
        obs = self._build_obs()

        # Termination conditions
        terminated = (
            self.simulator.is_leaked
            or action == 4            # terminate_session hard-stops episode
        )
        truncated = self.current_step >= self.max_steps

        info: Dict[str, Any] = {
            "simulator_state": self.simulator.state.name,
            "is_attacking":    self.simulator.is_attacking,
            "is_leaked":       self.simulator.is_leaked,
            "action_name":     ACTION_NAMES[action],
            "episode_stats":   dict(self._episode_stats),
        }

        return obs, reward, terminated, truncated, info

    def render(self, mode: str = "human") -> Optional[str]:
        if self._last_snapshot is None:
            return None
        s = self.simulator.state.name
        tcr = self._last_snapshot.tool_call_rate
        rr  = self._last_snapshot.refusal_rate
        msg = (
            f"Step {self.current_step:3d} | State={s:<22} | "
            f"tool_call_rate={tcr:5.1f} | refusal_rate={rr:.2f}"
        )
        if mode == "human":
            print(msg)
        return msg

    def close(self) -> None:
        pass

    # ------------------------------------------------------------------ #
    # Internal helpers                                                     #
    # ------------------------------------------------------------------ #

    def _build_obs(self) -> np.ndarray:
        """
        Construct the 12D observation vector from the last snapshot and
        running moving-average / sustained buffers.
        """
        if self._last_snapshot is None:
            return np.zeros(OBS_DIM, dtype=np.float32)

        snap = self._last_snapshot
        tcr_ma = float(np.mean(list(self._tcr_history))) if self._tcr_history else snap.tool_call_rate
        rr_ma  = float(np.mean(list(self._rr_history)))  if self._rr_history  else snap.refusal_rate
        sustained = min(self._high_activity_counter / max(self.high_activity_threshold, 1), 1.0)
        norm_time = self.current_step / self.max_steps

        obs_struct = AgentSessionObservation.from_snapshot(
            snapshot=snap,
            tool_call_rate_ma=tcr_ma,
            refusal_rate_ma=rr_ma,
            sustained_indicator=sustained,
            normalized_time=norm_time,
        )
        obs = obs_struct.to_vector()

        # Add Gaussian noise to raw dims 0-9 (not binary/time dims 10-11)
        noise = np.random.normal(0, self.obs_noise_std, 10)
        obs[:10] += noise.astype(np.float32)

        return np.clip(obs, OBS_LOW, OBS_HIGH)

    def _update_sustained_counter(self, snap: AgentSessionSnapshot) -> None:
        """Increment or decay the sustained high-activity counter."""
        elevated = (
            snap.tool_call_rate > 10.0
            or snap.refusal_rate > 0.3
            or snap.system_prompt_mention_rate > 0.2
        )
        if elevated:
            self._high_activity_counter = min(
                self._high_activity_counter + 1, self.high_activity_threshold * 2
            )
        else:
            self._high_activity_counter = max(self._high_activity_counter - 1, 0)

    def _calculate_reward(self, action: int, contained: bool) -> float:
        """
        Compute step reward.

        Logic mirrors incident_env.py._calculate_reward() exactly,
        adapted for the jailbreak state machine and new action semantics.
        """
        r = self.rewards
        reward = r["step_penalty"]

        is_attacking = self.simulator.is_attacking
        is_leaked    = self.simulator.is_leaked

        if is_leaked:
            reward += r["leak_occurred"]
            return reward

        if action == 0:  # do_nothing
            if not is_attacking:
                reward += r["correct_no_action"]
            else:
                # Missed attack — penalise proportional to stage
                stage = self.simulator.state.value
                reward += r["step_penalty"] * stage * 2
            return reward

        # Intervention taken (actions 1-4)
        if contained:
            # Determine early vs. late containment
            stage_before = self.simulator.steps_in_state
            if self.simulator.state == JailbreakState.NORMAL:
                # Contained at PROBING → early
                reward += r["early_containment"]
            else:
                reward += r["late_containment"]
        elif not is_attacking:
            # Intervened on a NORMAL session → false positive
            reward += r["false_positive"]
        else:
            # Intervention didn't contain attack
            reward += r["unnecessary_action"]

        return reward

    def _update_stats(self, action: int, contained: bool) -> None:
        """Update episode-level counters."""
        is_attacking = self.simulator.is_attacking

        if action != 0:
            self._episode_stats["interventions"] += 1

        if contained:
            self._episode_stats["attacks_contained"] += 1

        if action != 0 and not is_attacking and not contained:
            self._episode_stats["false_positives"] += 1

        if self.simulator.is_leaked:
            self._episode_stats["leak_events"] += 1

        if action == 0 and is_attacking:
            self._episode_stats["missed_attacks"] += 1


# ---------------------------------------------------------------------------
# Baseline agents adapted for the agent-layer action space
# ---------------------------------------------------------------------------

class AgentLayerBaseline:
    """
    Baseline defenders for AgentResponseEnv, mirroring BaselineAgent
    from agent.py in structure.

    These baselines are used by dual_eval.py for comparison and reuse the
    same statistical evaluation infrastructure from evaluate.py.
    """

    @staticmethod
    def random_agent(n_actions: int = 5) -> int:
        return int(np.random.randint(0, n_actions))

    @staticmethod
    def threshold_agent(obs: np.ndarray) -> int:
        """
        Rule-based baseline using obs vector thresholds.

        Dim mapping (see OBS_NAMES):
          0  tool_call_rate
          1  refusal_rate
          6  system_prompt_mention_rate
          3  repeated_failed_tool_calls
        """
        tcr   = obs[0]
        rr    = obs[1]
        sp    = obs[6]
        fails = obs[3]

        if sp > 0.4 or (rr > 0.5 and tcr > 15):
            return 4  # terminate_session
        if rr > 0.3 or fails > 5:
            return 3  # escalate_to_human
        if tcr > 12:
            return 1  # rate_limit_session
        if sp > 0.15:
            return 2  # inject_clarifying_prompt
        return 0      # do_nothing

    @staticmethod
    def escalate_always_agent() -> int:
        """Always escalates to human — maximally cautious baseline."""
        return 3

    @staticmethod
    def do_nothing_agent() -> int:
        return 0


# ---------------------------------------------------------------------------
# Smoke test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import time

    print("AgentResponseEnv smoke test")
    print("=" * 50)

    env = AgentResponseEnv(max_steps=50, obs_noise_std=0.3)
    obs, _ = env.reset(seed=42)
    print(f"obs shape : {obs.shape}")
    print(f"obs sample: {obs}")
    print(f"obs space : low={env.observation_space.low}")
    print(f"            high={env.observation_space.high}")

    total_reward = 0.0
    for step in range(50):
        action = env.action_space.sample()
        obs, reward, terminated, truncated, info = env.step(action)
        total_reward += reward
        env.render()
        if terminated or truncated:
            break

    print(f"\nEpisode reward: {total_reward:.2f}")
    print(f"Episode stats : {info['episode_stats']}")
    env.close()
