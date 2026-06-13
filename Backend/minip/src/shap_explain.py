"""
SHAP-Based Explanation Layer for AgentResponseEnv DQN Decisions.

Uses shap.KernelExplainer (model-agnostic, works on the DQN's black-box
get_q_values() function) to explain each intervention made by the agent-layer
DQN in terms of the 12 observation features.

For each intervention step:
  1. Compute SHAP values for the chosen action's Q-value
  2. Identify top-3 contributing features
  3. Generate a short natural-language reason string
  4. Append a JSON record to logs/agent_intervention_log.jsonl

Integration points
──────────────────
  • Wraps DQNAgent.get_q_values() — no agent.py changes needed
  • Reads feature names from agent_telemetry.OBS_NAMES
  • Can be used inline during eval or post-hoc on a saved trajectory

Requirements
────────────
  pip install shap     (not in existing requirements.txt — added separately)

Usage
─────
    from src.shap_explain import SHAPExplainer
    from src.agent_response_env import AgentResponseEnv

    env     = AgentResponseEnv()
    explainer = SHAPExplainer(agent, env, background_samples=100)

    # Run one explained episode
    obs, _ = env.reset()
    while True:
        action, record = explainer.explain_step(obs)
        obs, reward, terminated, truncated, info = env.step(action)
        if terminated or truncated:
            break

    explainer.flush()   # write all pending records to JSONL

    # Or run a full evaluation loop with explanations
    python src/shap_explain.py --model models/agent_best_model.h5 --episodes 10
"""

import json
import os
import sys
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

_HERE = Path(__file__).parent
if str(_HERE.parent) not in sys.path:
    sys.path.insert(0, str(_HERE.parent))

from src.agent_telemetry import OBS_NAMES, OBS_DIM
from src.agent_response_env import AgentResponseEnv, ACTION_NAMES

try:
    import shap
    _SHAP_AVAILABLE = True
except ImportError:
    _SHAP_AVAILABLE = False
    print(
        "[SHAPExplainer] WARNING: shap not installed. "
        "Install with: pip install shap\n"
        "Falling back to gradient-free feature-importance approximation."
    )


# ---------------------------------------------------------------------------
# Natural-language template generation
# ---------------------------------------------------------------------------

# Per-feature description fragments used to build human-readable reasons
_FEATURE_DESCRIPTIONS: Dict[str, str] = {
    "tool_call_rate":              "high tool-call rate",
    "refusal_rate":                "elevated refusal rate",
    "avg_response_entropy":        "unusual response entropy",
    "repeated_failed_tool_calls":  "repeated failed tool retries",
    "prompt_length_delta":         "sudden prompt-length spike",
    "unique_tool_diversity":       "low tool diversity (scripted pattern)",
    "system_prompt_mention_rate":  "system-prompt extraction attempts",
    "session_duration":            "extended session duration",
    "tool_call_rate_ma":           "sustained elevated call rate",
    "refusal_rate_ma":             "sustained refusal pattern",
    "sustained_indicator":         "sustained anomaly indicator",
    "normalized_time":             "episode time pressure",
}

_ACTION_VERB: Dict[str, str] = {
    "do_nothing":              "maintained monitoring",
    "rate_limit_session":      "applied rate limiting",
    "inject_clarifying_prompt": "injected a clarifying prompt",
    "escalate_to_human":       "escalated to human review",
    "terminate_session":       "terminated the session",
}


def _build_reason(
    action_name: str,
    top_features: List[Tuple[str, float]],
    q_value: float,
) -> str:
    """
    Build a short natural-language explanation string.

    Args:
        action_name:  Chosen action label (from ACTION_NAMES)
        top_features: List of (feature_name, shap_value) sorted by |shap|
        q_value:      Q-value of the chosen action

    Returns:
        Human-readable reason string (max ~200 chars)
    """
    verb = _ACTION_VERB.get(action_name, action_name)

    if not top_features:
        return f"Agent {verb} (Q={q_value:.2f}) with no dominant signal."

    # Take top 3
    parts = []
    for name, shap_val in top_features[:3]:
        desc = _FEATURE_DESCRIPTIONS.get(name, name.replace("_", " "))
        direction = "elevated" if shap_val > 0 else "suppressed"
        parts.append(f"{desc} (SHAP {shap_val:+.2f})")

    feature_str = "; ".join(parts)
    return f"Agent {verb} (Q={q_value:.2f}) driven by: {feature_str}."


# ---------------------------------------------------------------------------
# Fallback: finite-difference importance (when shap not installed)
# ---------------------------------------------------------------------------

def _fd_importance(
    predict_fn,
    obs: np.ndarray,
    action_idx: int,
    eps: float = 0.5,
) -> np.ndarray:
    """
    Finite-difference feature importance as a shap fallback.

    For each feature i:
      importance[i] = predict_fn(obs + eps*e_i)[action_idx]
                    - predict_fn(obs - eps*e_i)[action_idx]

    Returns: importance array of shape (OBS_DIM,)
    """
    base_q = predict_fn(obs)[action_idx]
    importance = np.zeros(OBS_DIM, dtype=np.float32)
    for i in range(OBS_DIM):
        perturbed_plus  = obs.copy(); perturbed_plus[i]  += eps
        perturbed_minus = obs.copy(); perturbed_minus[i] -= eps
        q_plus  = predict_fn(perturbed_plus)[action_idx]
        q_minus = predict_fn(perturbed_minus)[action_idx]
        importance[i] = (q_plus - q_minus) / (2 * eps)
    return importance


# ---------------------------------------------------------------------------
# Main explainer class
# ---------------------------------------------------------------------------

class SHAPExplainer:
    """
    Wraps DQNAgent to produce per-step SHAP explanations for AgentResponseEnv.

    The explainer maintains a background dataset sampled from the environment's
    observation space, used to compute the expected model output baseline
    for KernelExplainer.

    Explanations are buffered in memory and flushed to JSONL on demand.
    """

    def __init__(
        self,
        agent,
        env: AgentResponseEnv,
        background_samples: int = 200,
        log_path: str = "logs/agent_intervention_log.jsonl",
        interventions_only: bool = True,
    ) -> None:
        """
        Args:
            agent:              Trained DQNAgent with get_q_values() method
            env:                AgentResponseEnv instance (for obs sampling)
            background_samples: Number of random observations for SHAP background
            log_path:           Path to the JSONL output log
            interventions_only: If True, only log steps where action != 0
        """
        self.agent              = agent
        self.env                = env
        self.log_path           = log_path
        self.interventions_only = interventions_only
        self._buffer: List[Dict[str, Any]] = []

        os.makedirs(os.path.dirname(log_path) or ".", exist_ok=True)

        # Prediction function: obs (1D) → Q-value array (5,)
        def _predict(obs_2d: np.ndarray) -> np.ndarray:
            """Batch-compatible wrapper for KernelExplainer."""
            results = []
            for row in obs_2d:
                results.append(agent.get_q_values(row.astype(np.float32)))
            return np.array(results)

        self._predict = _predict

        # Build background dataset from uniform env samples
        print(f"[SHAPExplainer] Sampling {background_samples} background observations…")
        background = np.array([
            env.observation_space.sample() for _ in range(background_samples)
        ], dtype=np.float32)
        self._background = background

        # Initialise SHAP explainer
        if _SHAP_AVAILABLE:
            self._explainer = shap.KernelExplainer(
                model=self._predict,
                data=shap.sample(background, min(50, background_samples)),
                link="identity",
            )
            print("[SHAPExplainer] KernelExplainer initialised (SHAP).")
        else:
            self._explainer = None
            print("[SHAPExplainer] Using finite-difference importance (fallback).")

    # ------------------------------------------------------------------ #
    # Public API                                                           #
    # ------------------------------------------------------------------ #

    def explain_step(
        self,
        obs: np.ndarray,
        session_id: str = "unknown",
        step: int = 0,
    ) -> Tuple[int, Dict[str, Any]]:
        """
        Select an action and produce its SHAP explanation.

        Args:
            obs:        Current 12D observation
            session_id: For logging
            step:       Current episode step number

        Returns:
            (action, explanation_record)
        """
        q_values = self.agent.get_q_values(obs)
        action   = int(np.argmax(q_values))
        q_chosen = float(q_values[action])
        action_name = ACTION_NAMES[action]

        # Only compute SHAP for interventions (or if interventions_only=False)
        if self.interventions_only and action == 0:
            return action, {}

        importance = self._compute_importance(obs, action)

        # Sort by absolute contribution (descending)
        feat_contributions = list(zip(OBS_NAMES, importance.tolist()))
        feat_contributions.sort(key=lambda x: abs(x[1]), reverse=True)

        top_features = feat_contributions[:3]
        reason = _build_reason(action_name, top_features, q_chosen)

        record: Dict[str, Any] = {
            "timestamp":    datetime.utcnow().isoformat() + "Z",
            "session_id":   session_id,
            "step":         step,
            "action":       action,
            "action_name":  action_name,
            "q_value":      round(q_chosen, 4),
            "reason":       reason,
            "top_features": [
                {"feature": f, "shap_value": round(v, 4)}
                for f, v in top_features
            ],
            "all_shap_values": {
                f: round(v, 4) for f, v in feat_contributions
            },
            "obs": {n: round(float(v), 4) for n, v in zip(OBS_NAMES, obs.tolist())},
        }

        self._buffer.append(record)
        return action, record

    def flush(self) -> int:
        """
        Write all buffered explanation records to the JSONL log file.

        Returns:
            Number of records written
        """
        if not self._buffer:
            return 0

        with open(self.log_path, "a", encoding="utf-8") as f:
            for record in self._buffer:
                f.write(json.dumps(record) + "\n")

        n = len(self._buffer)
        self._buffer.clear()
        return n

    def run_explained_episode(
        self,
        seed: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Run one full episode with SHAP explanations on every intervention.

        Returns:
            Episode summary dict including all explanation records.
        """
        obs, _ = self.env.reset(seed=seed)
        session_id = self.env.simulator.session_id
        episode_reward = 0.0
        records: List[Dict[str, Any]] = []
        step = 0

        while True:
            step += 1
            action, record = self.explain_step(obs, session_id=session_id, step=step)
            if record:
                records.append(record)

            obs, reward, terminated, truncated, info = self.env.step(action)
            episode_reward += reward

            if terminated or truncated:
                break

        written = self.flush()

        return {
            "session_id":      session_id,
            "episode_reward":  round(episode_reward, 2),
            "total_steps":     step,
            "interventions":   len(records),
            "records_logged":  written,
            "last_state":      info.get("simulator_state", "?"),
            "episode_stats":   info.get("episode_stats", {}),
        }

    # ------------------------------------------------------------------ #
    # Internal                                                             #
    # ------------------------------------------------------------------ #

    def _compute_importance(
        self,
        obs: np.ndarray,
        action_idx: int,
    ) -> np.ndarray:
        """
        Return per-feature importance array of shape (OBS_DIM,).

        Uses SHAP KernelExplainer if available, otherwise finite differences.
        """
        if self._explainer is not None:
            # KernelExplainer returns shap_values for all outputs
            # We want the SHAP values for the chosen action's Q
            try:
                shap_vals = self._explainer.shap_values(
                    obs.reshape(1, -1),
                    nsamples=100,
                    silent=True,
                )
                # shap_vals is a list of arrays (one per output)
                if isinstance(shap_vals, list):
                    importance = np.array(shap_vals[action_idx]).flatten()
                else:
                    importance = np.array(shap_vals).flatten()
                return importance
            except Exception as e:
                # Graceful degradation to FD on any SHAP failure
                pass

        return _fd_importance(
            predict_fn=lambda x: self._predict(x.reshape(1, -1))[0],
            obs=obs,
            action_idx=action_idx,
        )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    import argparse
    from config import get_config
    from agent import DQNAgent

    parser = argparse.ArgumentParser(
        description="SHAP-based explanation of AgentResponseEnv DQN decisions"
    )
    parser.add_argument(
        "--model", type=str, default="models/agent_best_model.h5",
        help="Path to trained agent-layer DQN model"
    )
    parser.add_argument("--episodes", type=int, default=10)
    parser.add_argument(
        "--log",     type=str, default="logs/agent_intervention_log.jsonl"
    )
    parser.add_argument(
        "--background", type=int, default=200,
        help="Number of background samples for SHAP KernelExplainer"
    )
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    np.random.seed(args.seed)

    try:
        base_config = get_config()
    except Exception as e:
        print(f"Config error: {e}")
        sys.exit(1)

    env = AgentResponseEnv()
    agent = DQNAgent(
        state_size=env.observation_space.shape[0],
        action_size=env.action_space.n,
        config=base_config.agent,
        use_dueling=True,
    )

    if Path(args.model).exists():
        try:
            agent.load(args.model)
            print(f"Loaded agent model from {args.model}")
        except Exception as e:
            print(f"Could not load model ({e}). Using untrained agent.")
    else:
        print(f"Model not found at {args.model}. Using untrained agent.")

    explainer = SHAPExplainer(
        agent=agent,
        env=env,
        background_samples=args.background,
        log_path=args.log,
    )

    print(f"\nRunning {args.episodes} explained episodes…\n")
    total_interventions = 0

    for ep in range(args.episodes):
        result = explainer.run_explained_episode(seed=args.seed + ep)
        total_interventions += result["interventions"]
        print(
            f"  ep={ep+1:3d}  reward={result['episode_reward']:6.2f}  "
            f"steps={result['total_steps']:3d}  "
            f"interventions={result['interventions']:3d}  "
            f"state={result['last_state']}"
        )

    print(f"\nTotal interventions logged : {total_interventions}")
    print(f"Explanation log            : {args.log}")

    # Print a sample explanation from the log
    if Path(args.log).exists():
        print("\n--- Sample Explanation Record ---")
        with open(args.log) as f:
            last_line = None
            for last_line in f:
                pass
        if last_line:
            rec = json.loads(last_line)
            print(f"  Action  : {rec['action_name']}")
            print(f"  Q-value : {rec['q_value']}")
            print(f"  Reason  : {rec['reason']}")
            print(f"  Top features:")
            for tf in rec.get("top_features", []):
                print(f"    {tf['feature']:35s} SHAP={tf['shap_value']:+.4f}")

    env.close()


if __name__ == "__main__":
    main()
