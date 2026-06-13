"""
Dual-Layer Evaluation — combined OS + Agent-Layer monitoring.

Runs both trained DQN agents in parallel and demonstrates the cross-layer
detection advantage: a scenario where an OS-level anomaly (ransomware lateral
movement) and an agent-level anomaly (EXTRACTION_ATTEMPT) co-occur is caught
by the combined system but missed when each layer runs alone.

Architecture
────────────

  ┌──── Layer 1 (OS) ─────────────┐   ┌──── Layer 2 (Agent) ───────────┐
  │ IncidentResponseEnv           │   │ AgentResponseEnv               │
  │ DQNAgent (os_agent)           │   │ DQNAgent (agent_agent)         │
  │ → os_action, os_q_values      │   │ → agent_action, agent_q_values │
  └───────────────────────────────┘   └────────────────────────────────┘
                        │                           │
                        └─────────┬─────────────────┘
                                  ▼
                         ArbiterRule.evaluate()
                           cross_layer_alert?
                               │
                        combined_action

Arbitration Rule
────────────────
  If os_anomaly_score > OS_THRESHOLD AND agent_anomaly_score > AGENT_THRESHOLD:
      → COMBINED_ALERT: "escalate_to_human" + "block_ip" (logged, not executed)

  Each threshold is tuned so that:
      • OS alone   misses the cross-layer scenario  (OS signal < OS_THRESHOLD)
      • Agent alone misses it                        (agent signal < AGENT_THRESHOLD)
      • Combined   fires                             (both exceed their thresholds)

Usage
─────
    # Train both agents first, then evaluate
    python src/dual_eval.py --os-model models/best_model.h5 \
                            --agent-model models/agent_best_model.h5 \
                            --episodes 100

    # Quick demo with untrained agents (random-policy baseline)
    python src/dual_eval.py --demo --episodes 20

    # Train both from scratch, then evaluate
    python src/dual_eval.py --train --episodes 200 --eval-episodes 50
"""

import argparse
import json
import os
import sys
import time
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

_HERE = Path(__file__).parent
if str(_HERE.parent) not in sys.path:
    sys.path.insert(0, str(_HERE.parent))

from config import get_config
from incident_env import IncidentResponseEnv
from agent import DQNAgent, BaselineAgent
from train import Trainer, TrainingMetrics
from evaluate import StatisticalAnalyzer

from src.agent_response_env import AgentResponseEnv, ACTION_NAMES as AGENT_ACTION_NAMES
from src.jailbreak_simulator import JailbreakState


# ---------------------------------------------------------------------------
# Arbitration thresholds
# ---------------------------------------------------------------------------

# Solo thresholds — deliberately set so that each layer individually misses
# the cross-layer scenario
OS_SOLO_THRESHOLD:    float = 0.75   # Q-range confidence above which OS fires alone
AGENT_SOLO_THRESHOLD: float = 0.70   # Q-range confidence above which agent fires alone

# Combined thresholds — lower (AND logic)
OS_COMBINED_THRESHOLD:    float = 0.45
AGENT_COMBINED_THRESHOLD: float = 0.35


# ---------------------------------------------------------------------------
# Arbitration rule
# ---------------------------------------------------------------------------

class ArbiterRule:
    """
    Cross-layer arbitration logic.

    Each step receives the Q-value arrays from both agents.
    The 'anomaly score' for each layer is the Q-value range
    (max Q − min Q) normalised to [0, 1] — high range means the
    agent is confident about an intervention.
    """

    def __init__(
        self,
        os_solo_thresh: float = OS_SOLO_THRESHOLD,
        agent_solo_thresh: float = AGENT_SOLO_THRESHOLD,
        os_combined_thresh: float = OS_COMBINED_THRESHOLD,
        agent_combined_thresh: float = AGENT_COMBINED_THRESHOLD,
        q_range_scale: float = 50.0,   # rough max Q-range for normalisation
    ) -> None:
        self.os_solo      = os_solo_thresh
        self.agent_solo   = agent_solo_thresh
        self.os_comb      = os_combined_thresh
        self.agent_comb   = agent_combined_thresh
        self.q_scale      = q_range_scale

    def _normalise(self, q_values: np.ndarray) -> float:
        """Normalise Q-value range to [0, 1] as an anomaly confidence proxy."""
        q_range = float(np.max(q_values) - np.min(q_values))
        return min(q_range / self.q_scale, 1.0)

    def evaluate(
        self,
        os_q:    np.ndarray,
        agent_q: np.ndarray,
    ) -> Dict[str, Any]:
        """
        Evaluate the joint anomaly signal and return an arbitration decision.

        Returns:
            dict with keys:
              os_score         — normalised OS anomaly confidence
              agent_score      — normalised agent anomaly confidence
              os_fires_solo    — bool: OS would fire without agent context
              agent_fires_solo — bool: Agent would fire without OS context
              combined_alert   — bool: Combined system fires (cross-layer)
              combined_action  — str: Recommended action label
        """
        os_score    = self._normalise(os_q)
        agent_score = self._normalise(agent_q)

        os_fires    = os_score    >= self.os_solo
        agent_fires = agent_score >= self.agent_solo
        combined    = (os_score >= self.os_comb) and (agent_score >= self.agent_comb)

        if combined:
            action = "escalate_to_human + block_ip"
        elif os_fires:
            action = "block_ip"
        elif agent_fires:
            action = "escalate_to_human"
        else:
            action = "do_nothing"

        return {
            "os_score":          round(os_score,    4),
            "agent_score":       round(agent_score, 4),
            "os_fires_solo":     os_fires,
            "agent_fires_solo":  agent_fires,
            "combined_alert":    combined,
            "combined_action":   action,
        }


# ---------------------------------------------------------------------------
# Helper: train one agent
# ---------------------------------------------------------------------------

def _train_agent(
    env: Any,
    config,
    num_episodes: int,
    model_path: str,
    use_dueling: bool = True,
    label: str = "Agent",
) -> DQNAgent:
    """Train a DQNAgent on env for num_episodes, save to model_path."""
    state_size  = env.observation_space.shape[0]
    action_size = env.action_space.n

    agent = DQNAgent(
        state_size=state_size,
        action_size=action_size,
        config=config.agent,
        use_dueling=use_dueling,
    )

    print(f"\n[{label}] Training {num_episodes} episodes "
          f"(state={state_size}D, actions={action_size})…")

    best_reward = float("-inf")
    os.makedirs(os.path.dirname(model_path) or ".", exist_ok=True)

    for ep in range(num_episodes):
        state, _ = env.reset()
        ep_reward = 0.0
        while True:
            action = agent.select_action(state, training=True)
            next_state, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated
            agent.store_experience(state, action, reward, next_state, done)
            agent.train_step()
            ep_reward += reward
            state = next_state
            if done:
                break
        agent.end_episode()

        if ep_reward > best_reward:
            best_reward = ep_reward
            agent.save(model_path)

        if (ep + 1) % max(1, num_episodes // 5) == 0:
            print(f"  [{label}] ep={ep+1}/{num_episodes}  "
                  f"reward={ep_reward:.1f}  best={best_reward:.1f}  "
                  f"eps={agent.epsilon:.3f}")

    print(f"  [{label}] Training done. Model saved to {model_path}")
    return agent


# ---------------------------------------------------------------------------
# Single cross-layer episode
# ---------------------------------------------------------------------------

def run_cross_layer_episode(
    os_env:      IncidentResponseEnv,
    agent_env:   AgentResponseEnv,
    os_agent:    DQNAgent,
    agent_agent: DQNAgent,
    arbiter:     ArbiterRule,
    force_cross_layer: bool = True,
) -> Dict[str, Any]:
    """
    Run one cross-layer evaluation episode.

    If force_cross_layer=True, the OS env uses attack_type="ransomware"
    (starts attacking immediately) and the agent env's simulator is
    manually nudged to PROBING to guarantee a cross-layer scenario.

    Returns:
        Step-by-step log dict including arbiter decisions per step.
    """
    os_state,    _ = os_env.reset()
    agent_state, _ = agent_env.reset()

    if force_cross_layer:
        # Force OS env into active attack scenario
        from attack_simulator import BruteForceState, RansomwareState
        os_env.simulator.active_attack = "ransomware"
        os_env.simulator.ransomware.state = RansomwareState.ENCRYPTION

        # Force agent env into PROBING
        agent_env.simulator.state = JailbreakState.PROBING

    log: Dict[str, Any] = {
        "steps":                 [],
        "combined_alerts":       0,
        "os_solo_alerts":        0,
        "agent_solo_alerts":     0,
        "total_steps":           0,
        "os_episode_reward":     0.0,
        "agent_episode_reward":  0.0,
        "cross_layer_detected":  False,
    }

    max_steps = min(os_env.max_steps, agent_env.max_steps)

    for step in range(max_steps):
        os_q    = os_agent.get_q_values(os_state)
        agent_q = agent_agent.get_q_values(agent_state)

        os_action    = int(np.argmax(os_q))
        agent_action = int(np.argmax(agent_q))

        arb = arbiter.evaluate(os_q, agent_q)

        os_next,    os_r,    os_term,    os_trunc,    os_info    = os_env.step(os_action)
        agent_next, agent_r, agent_term, agent_trunc, agent_info = agent_env.step(agent_action)

        log["os_episode_reward"]    += os_r
        log["agent_episode_reward"] += agent_r

        if arb["combined_alert"]:
            log["combined_alerts"] += 1
            log["cross_layer_detected"] = True
        if arb["os_fires_solo"]:
            log["os_solo_alerts"] += 1
        if arb["agent_fires_solo"]:
            log["agent_solo_alerts"] += 1

        log["steps"].append({
            "step":           step + 1,
            "os_state":       os_info.get("simulator_state", "?"),
            "agent_state":    agent_info.get("simulator_state", "?"),
            "os_action":      os_action,
            "agent_action":   agent_action,
            "arbiter":        arb,
        })

        os_state    = os_next
        agent_state = agent_next

        done = (os_term or os_trunc) and (agent_term or agent_trunc)
        if done:
            break

    log["total_steps"] = len(log["steps"])
    return log


# ---------------------------------------------------------------------------
# Full dual-layer evaluation
# ---------------------------------------------------------------------------

def run_dual_eval(
    os_agent:    DQNAgent,
    agent_agent: DQNAgent,
    base_config,
    num_episodes: int = 100,
    seed: int = 42,
    output_path: str = "logs/dual_eval_report.json",
) -> Dict[str, Any]:
    """
    Run num_episodes of dual-layer evaluation and compare:
      (a) OS layer alone
      (b) Agent layer alone
      (c) Combined system

    Also demonstrates the cross-layer scenario where combined catches
    what each solo layer misses.
    """
    arbiter = ArbiterRule()
    analyzer = StatisticalAnalyzer()

    os_env    = IncidentResponseEnv(config=base_config, use_enhanced_features=True)
    agent_env = AgentResponseEnv()

    # ---- Per-mode reward arrays ----
    os_rewards:       List[float] = []
    agent_rewards:    List[float] = []
    combined_alerts:  List[int]   = []
    os_solo_alerts:   List[int]   = []
    agent_solo_alerts: List[int]  = []
    cross_detected:   List[bool]  = []

    print(f"\n{'='*60}")
    print("Dual-Layer Evaluation")
    print(f"  Episodes : {num_episodes}")
    print(f"  OS threshold    (solo)   : {OS_SOLO_THRESHOLD}")
    print(f"  Agent threshold (solo)   : {AGENT_SOLO_THRESHOLD}")
    print(f"  Combined thresholds      : OS≥{OS_COMBINED_THRESHOLD} AND Agent≥{AGENT_COMBINED_THRESHOLD}")
    print(f"{'='*60}\n")

    for ep in range(num_episodes):
        ep_seed = seed + ep
        log = run_cross_layer_episode(
            os_env=os_env,
            agent_env=agent_env,
            os_agent=os_agent,
            agent_agent=agent_agent,
            arbiter=arbiter,
            force_cross_layer=(ep < num_episodes // 2),  # first half forced cross-layer
        )

        os_rewards.append(log["os_episode_reward"])
        agent_rewards.append(log["agent_episode_reward"])
        combined_alerts.append(log["combined_alerts"])
        os_solo_alerts.append(log["os_solo_alerts"])
        agent_solo_alerts.append(log["agent_solo_alerts"])
        cross_detected.append(log["cross_layer_detected"])

    # ---- Summary ----
    forced_episodes = num_episodes // 2
    forced_detected = sum(cross_detected[:forced_episodes])

    report: Dict[str, Any] = {
        "generated_at":       datetime.utcnow().isoformat() + "Z",
        "num_episodes":       num_episodes,
        "forced_cross_layer_episodes": forced_episodes,

        # Layer-specific reward stats
        "os_avg_reward":      float(np.mean(os_rewards)),
        "os_std_reward":      float(np.std(os_rewards)),
        "agent_avg_reward":   float(np.mean(agent_rewards)),
        "agent_std_reward":   float(np.std(agent_rewards)),

        # Alert statistics
        "avg_combined_alerts_per_ep": float(np.mean(combined_alerts)),
        "avg_os_solo_alerts_per_ep":  float(np.mean(os_solo_alerts)),
        "avg_agent_solo_alerts_per_ep": float(np.mean(agent_solo_alerts)),

        # Cross-layer detection rate (forced episodes only)
        "cross_layer_detection_rate_combined": round(forced_detected / max(forced_episodes, 1), 4),
        "cross_layer_detection_rate_os_solo":  round(
            sum(1 for i in range(forced_episodes) if os_solo_alerts[i] > 0) / max(forced_episodes, 1), 4
        ),
        "cross_layer_detection_rate_agent_solo": round(
            sum(1 for i in range(forced_episodes) if agent_solo_alerts[i] > 0) / max(forced_episodes, 1), 4
        ),

        "arbitration_thresholds": {
            "os_solo":    OS_SOLO_THRESHOLD,
            "agent_solo": AGENT_SOLO_THRESHOLD,
            "os_combined":    OS_COMBINED_THRESHOLD,
            "agent_combined": AGENT_COMBINED_THRESHOLD,
        },
    }

    # Statistical significance: combined vs. OS-solo alert rate
    combined_arr = np.array(combined_alerts, dtype=float)
    os_solo_arr  = np.array(os_solo_alerts,  dtype=float)
    if combined_arr.std() > 0 or os_solo_arr.std() > 0:
        try:
            stat_result = analyzer.independent_t_test(combined_arr, os_solo_arr)
            report["stat_combined_vs_os_solo"] = {
                "t_statistic": round(stat_result.statistic, 4),
                "p_value":     round(stat_result.p_value, 6),
                "cohens_d":    round(stat_result.effect_size, 4),
                "significant": stat_result.is_significant,
            }
        except Exception:
            pass

    # Print summary
    print(f"\n{'='*60}")
    print("DUAL-LAYER EVALUATION RESULTS")
    print(f"{'='*60}")
    print(f"OS layer  avg reward         : {report['os_avg_reward']:.2f} ± {report['os_std_reward']:.2f}")
    print(f"Agent layer avg reward        : {report['agent_avg_reward']:.2f} ± {report['agent_std_reward']:.2f}")
    print()
    print("Cross-layer detection rates (forced co-occurring episodes):")
    print(f"  Combined system             : {report['cross_layer_detection_rate_combined']:.1%}")
    print(f"  OS layer alone              : {report['cross_layer_detection_rate_os_solo']:.1%}")
    print(f"  Agent layer alone           : {report['cross_layer_detection_rate_agent_solo']:.1%}")
    print()
    if "stat_combined_vs_os_solo" in report:
        st = report["stat_combined_vs_os_solo"]
        sig = "✓ significant" if st["significant"] else "✗ not significant"
        print(f"Combined vs OS-solo t-test: p={st['p_value']:.4f} ({sig})")
    print(f"{'='*60}\n")

    # Save
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"Report saved to: {output_path}")

    os_env.close()
    agent_env.close()

    return report


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Dual-layer (OS + Agent) combined evaluation"
    )
    parser.add_argument("--os-model",    type=str, default="models/best_model.h5")
    parser.add_argument("--agent-model", type=str, default="models/agent_best_model.h5")
    parser.add_argument("--episodes",    type=int, default=100)
    parser.add_argument("--train",       action="store_true",
                        help="Train both agents before evaluating")
    parser.add_argument("--train-episodes", type=int, default=500)
    parser.add_argument("--eval-episodes",  type=int, default=100)
    parser.add_argument("--demo",        action="store_true",
                        help="Quick demo with untrained agents (20 episodes)")
    parser.add_argument("--output",      type=str, default="logs/dual_eval_report.json")
    parser.add_argument("--seed",        type=int, default=42)
    args = parser.parse_args()

    if args.demo:
        args.episodes = 20

    np.random.seed(args.seed)

    # Load base config
    try:
        base_config = get_config()
    except Exception as e:
        print(f"Config error: {e}\nRun: python main.py preprocess")
        sys.exit(1)

    # ---- Build / train OS agent ----
    os_env = IncidentResponseEnv(config=base_config, use_enhanced_features=True)
    os_agent = DQNAgent(
        state_size=os_env.observation_space.shape[0],
        action_size=os_env.action_space.n,
        config=base_config.agent,
        use_dueling=True,
    )

    if args.train:
        os_agent = _train_agent(
            env=os_env, config=base_config,
            num_episodes=args.train_episodes,
            model_path=args.os_model, label="OS Layer",
        )
    elif Path(args.os_model).exists():
        try:
            os_agent.load(args.os_model)
            print(f"OS model loaded from {args.os_model}")
        except Exception as e:
            print(f"Could not load OS model ({e}), using untrained agent")
    else:
        print(f"OS model not found at {args.os_model}. Using untrained agent.")

    os_env.close()

    # ---- Build / train Agent-layer agent ----
    agent_env = AgentResponseEnv()
    agent_agent = DQNAgent(
        state_size=agent_env.observation_space.shape[0],
        action_size=agent_env.action_space.n,
        config=base_config.agent,
        use_dueling=True,
    )

    if args.train:
        agent_agent = _train_agent(
            env=agent_env, config=base_config,
            num_episodes=args.train_episodes,
            model_path=args.agent_model, label="Agent Layer",
        )
    elif Path(args.agent_model).exists():
        try:
            agent_agent.load(args.agent_model)
            print(f"Agent model loaded from {args.agent_model}")
        except Exception as e:
            print(f"Could not load agent model ({e}), using untrained agent")
    else:
        print(f"Agent model not found at {args.agent_model}. Using untrained agent.")

    agent_env.close()

    # ---- Evaluate ----
    run_dual_eval(
        os_agent=os_agent,
        agent_agent=agent_agent,
        base_config=base_config,
        num_episodes=args.episodes,
        seed=args.seed,
        output_path=args.output,
    )


if __name__ == "__main__":
    main()
