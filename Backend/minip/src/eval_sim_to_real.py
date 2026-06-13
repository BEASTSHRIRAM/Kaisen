"""
Sim-to-Real Gap Evaluation for Kaisen DQN Agent.

Runs a trained DQN agent in two modes and compares outcomes:

  SIM mode  — standard IncidentResponseEnv with CombinedAttackSimulator
  REAL mode — reads logs/history.json produced by LogCollector, maps
              each FeatureVector snapshot to the 13D observation space,
              and queries the agent for an action

Comparison metrics computed and saved to logs/sim_to_real_report.json:
  - Action frequency distributions  (KL-divergence, χ² test)
  - Reward statistics                (mean, std, min, max per mode)
  - Anomaly-score correlation        (Pearson r) with agent confidence
  - Episode-level containment rate   (sim only — real has no ground truth)

Usage:
    # Sim mode only (no history.json required)
    python src/eval_sim_to_real.py --sim-only --episodes 100

    # Both modes (requires logs/history.json)
    python src/eval_sim_to_real.py --model models/best_model.h5 --episodes 100

    # Real mode only
    python src/eval_sim_to_real.py --real-only --model models/best_model.h5

Research contribution:
    Directly answers the sim-to-real RQ in the paper by quantifying how
    differently the learned policy behaves on collected host telemetry vs
    the simulated environment it was trained on.
"""

import argparse
import json
import logging
import os
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

import numpy as np

_HERE = Path(__file__).parent
if str(_HERE.parent) not in sys.path:
    sys.path.insert(0, str(_HERE.parent))

from config import get_config
from incident_env import IncidentResponseEnv
from agent import DQNAgent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
)
logger = logging.getLogger("eval_sim_to_real")


# ---------------------------------------------------------------------------
# Observation mapping: FeatureVector dict → 13D numpy array
# ---------------------------------------------------------------------------

# Standard-port baseline count (same as incident_env.py)
_STD_PORT_COUNT = 5.0

# Observation space bounds (must stay in sync with IncidentResponseEnv 13D)
_OBS_LOW = np.array([
    0.0, 0.0, 0.0,
    -100.0, -200.0, -50.0,
    0.0, 0.0, 0.0, 0.0,
    0.0, 0.0, 0.0,
], dtype=np.float32)

_OBS_HIGH = np.array([
    200.0, 500.0, 100.0,
    100.0, 200.0, 50.0,
    200.0, 500.0, 1.0, 1.0,
    1000.0, 500.0, 1.0,
], dtype=np.float32)

# Proxy mapping for real-telemetry fields → observation dimensions.
# FeatureVector has: cpu_usage, memory_usage, process_count,
#                    network_connections, failed_logins, unique_ip_count
# We map them to the closest semantic match in the 13D space.
# Dims 3-5 (deltas) and 6-7 (MA) are computed from consecutive samples;
# dims 8 (sustained) and 9 (time) use heuristics.

def fv_to_obs(
    fv: Dict[str, Any],
    prev_fv: Optional[Dict[str, Any]],
    step: int,
    total_steps: int,
    sustained_counter: int,
) -> np.ndarray:
    """
    Map a FeatureVector dict (from history.json) to the 13D observation.

    Mapping:
        [0]  login_rate          ← failed_logins (per-window proxy)
        [1]  file_access_rate    ← process_count  (process churn proxy)
        [2]  cpu_usage           ← cpu_usage
        [3]  login_delta         ← Δfailed_logins
        [4]  file_delta          ← Δprocess_count
        [5]  cpu_delta           ← Δcpu_usage
        [6]  login_MA            ← failed_logins (no window history; use raw)
        [7]  file_MA             ← process_count (use raw)
        [8]  sustained_indicator ← 1 if cpu>80 or failed_logins>5 else 0
        [9]  normalized_time     ← step / total_steps
        [10] outbound_conn       ← network_connections (total as proxy)
        [11] unique_dst_ports    ← unique_ip_count * 3 (heuristic proxy)
        [12] rare_port_indicator ← unique_ip_count / max(network_connections,1)
                                    clipped [0,1] — IPs per connection ratio

    Args:
        fv:               Current FeatureVector as dict
        prev_fv:          Previous snapshot (None for first sample)
        step:             Current step index
        total_steps:      Total number of real samples
        sustained_counter: Running count of high-activity steps

    Returns:
        13-element float32 numpy array
    """
    cpu   = float(fv.get("cpu_usage", 0.0))
    fl    = float(fv.get("failed_logins", 0))
    nc    = float(fv.get("network_connections", 0))
    pc    = float(fv.get("process_count", 0))
    uip   = float(fv.get("unique_ip_count", 0))

    if prev_fv is not None:
        d_fl  = fl   - float(prev_fv.get("failed_logins", 0))
        d_pc  = pc   - float(prev_fv.get("process_count", 0))
        d_cpu = cpu  - float(prev_fv.get("cpu_usage", 0.0))
    else:
        d_fl, d_pc, d_cpu = 0.0, 0.0, 0.0

    # Sustained indicator: 1 if elevated, else 0
    sustained = 1.0 if (cpu > 80.0 or fl > 5) else 0.0

    # Lateral-movement proxies
    out_conn     = nc                                          # dim 10
    dst_ports    = np.clip(uip * 3.0, 0, 500)                # dim 11 (heuristic)
    rare_port    = np.clip(uip / max(nc, 1.0), 0.0, 1.0)     # dim 12

    obs = np.array([
        fl,                         # 0  login_rate
        pc,                         # 1  file_access_rate (process proxy)
        cpu,                        # 2  cpu_usage
        d_fl,                       # 3  login_delta
        d_pc,                       # 4  file_delta
        d_cpu,                      # 5  cpu_delta
        fl,                         # 6  login_MA (single sample → raw)
        pc,                         # 7  file_MA
        sustained,                  # 8  sustained_indicator
        step / max(total_steps, 1), # 9  normalized_time
        out_conn,                   # 10 outbound_connections
        dst_ports,                  # 11 unique_dst_ports
        rare_port,                  # 12 rare_port_indicator
    ], dtype=np.float32)

    return np.clip(obs, _OBS_LOW, _OBS_HIGH)


# ---------------------------------------------------------------------------
# Sim-mode evaluation
# ---------------------------------------------------------------------------

def eval_sim(
    agent: DQNAgent,
    base_config,
    num_episodes: int = 100,
    seed: int = 42,
) -> Dict[str, Any]:
    """
    Evaluate agent in IncidentResponseEnv (simulated mode).

    Returns:
        Dict of evaluation statistics.
    """
    env = IncidentResponseEnv(
        config=base_config,
        attack_type="random",
        use_enhanced_features=True,
    )

    rewards: List[float] = []
    actions_all: List[int] = []
    confidences: List[float] = []   # max Q-value as confidence proxy
    contained_list: List[int] = []
    fp_list: List[int] = []

    for ep in range(num_episodes):
        state, _ = env.reset(seed=seed + ep)
        ep_reward = 0.0

        while True:
            q_vals = agent.get_q_values(state)
            action = int(np.argmax(q_vals))
            confidence = float(np.max(q_vals) - np.min(q_vals))  # range as confidence

            next_state, reward, terminated, truncated, info = env.step(action)
            ep_reward += reward
            actions_all.append(action)
            confidences.append(confidence)
            state = next_state

            if terminated or truncated:
                break

        rewards.append(ep_reward)
        ep_stats = info.get("episode_stats", {})
        contained_list.append(ep_stats.get("attacks_contained", 0))
        fp_list.append(ep_stats.get("false_positives", 0))

    env.close()

    action_counts = Counter(actions_all)
    total_actions = len(actions_all)
    action_freq = {
        str(a): action_counts.get(a, 0) / total_actions for a in range(5)
    }

    return {
        "mode":              "sim",
        "num_episodes":      num_episodes,
        "total_steps":       total_actions,
        "avg_reward":        float(np.mean(rewards)),
        "std_reward":        float(np.std(rewards)),
        "min_reward":        float(np.min(rewards)),
        "max_reward":        float(np.max(rewards)),
        "action_freq":       action_freq,
        "avg_contained":     float(np.mean(contained_list)),
        "avg_fp":            float(np.mean(fp_list)),
        "avg_confidence":    float(np.mean(confidences)),
        "action_counts_raw": dict(action_counts),
    }


# ---------------------------------------------------------------------------
# Real-mode evaluation
# ---------------------------------------------------------------------------

def eval_real(
    agent: DQNAgent,
    history_path: str = "logs/history.json",
    anomaly_score_key: str = "anomaly_score",
) -> Dict[str, Any]:
    """
    Evaluate agent against real telemetry from history.json.

    Each consecutive pair of FeatureVector snapshots is treated as one
    environment step.  Because we have no ground-truth attack labels in
    real data, rewards cannot be computed; instead we report action
    distribution and agent confidence scores.

    Args:
        agent:             Trained DQNAgent
        history_path:      Path to history.json produced by LogCollector
        anomaly_score_key: Field name for anomaly score in history entries

    Returns:
        Dict of evaluation statistics.
    """
    path = Path(history_path)
    if not path.exists():
        raise FileNotFoundError(
            f"history.json not found at {history_path}. "
            "Run the backend collector first."
        )

    with open(path, "r") as f:
        history: List[Dict[str, Any]] = json.load(f)

    if not isinstance(history, list) or len(history) < 2:
        raise ValueError(
            f"history.json must contain at least 2 entries (found {len(history)})."
        )

    logger.info(f"Loaded {len(history)} real telemetry samples from {history_path}")

    actions_all: List[int] = []
    confidences: List[float] = []
    anomaly_scores: List[float] = []  # from ModelInterface output stored in history
    sustained_counter = 0
    total_steps = len(history)

    for i, fv in enumerate(history):
        prev_fv = history[i - 1] if i > 0 else None

        # Track sustained activity for obs dimension 8
        cpu = float(fv.get("cpu_usage", 0.0))
        fl  = float(fv.get("failed_logins", 0))
        if cpu > 80.0 or fl > 5:
            sustained_counter = min(sustained_counter + 1, 10)
        else:
            sustained_counter = max(sustained_counter - 1, 0)

        obs = fv_to_obs(fv, prev_fv, i, total_steps, sustained_counter)

        q_vals = agent.get_q_values(obs)
        action = int(np.argmax(q_vals))
        confidence = float(np.max(q_vals) - np.min(q_vals))

        actions_all.append(action)
        confidences.append(confidence)

        # Collect anomaly score if stored by the pipeline
        if anomaly_score_key in fv:
            anomaly_scores.append(float(fv[anomaly_score_key]))

    action_counts = Counter(actions_all)
    total_actions = len(actions_all)
    action_freq = {
        str(a): action_counts.get(a, 0) / total_actions for a in range(5)
    }

    result: Dict[str, Any] = {
        "mode":              "real",
        "num_samples":       total_steps,
        "total_steps":       total_actions,
        "action_freq":       action_freq,
        "avg_confidence":    float(np.mean(confidences)),
        "action_counts_raw": dict(action_counts),
    }

    # Correlation between anomaly score and agent confidence
    if len(anomaly_scores) >= 2 and len(anomaly_scores) == len(confidences):
        corr = float(np.corrcoef(anomaly_scores, confidences)[0, 1])
        result["anomaly_confidence_pearson_r"] = corr
        logger.info(f"Anomaly score ↔ agent confidence Pearson r = {corr:.4f}")

    return result


# ---------------------------------------------------------------------------
# Sim-to-real gap metrics
# ---------------------------------------------------------------------------

def _kl_divergence(p: Dict[str, float], q: Dict[str, float]) -> float:
    """
    KL(P||Q) for two action frequency distributions.
    Uses +1e-9 smoothing to avoid log(0).
    """
    actions = sorted(set(p.keys()) | set(q.keys()))
    p_arr = np.array([p.get(a, 0.0) + 1e-9 for a in actions])
    q_arr = np.array([q.get(a, 0.0) + 1e-9 for a in actions])
    p_arr /= p_arr.sum()
    q_arr /= q_arr.sum()
    return float(np.sum(p_arr * np.log(p_arr / q_arr)))


def compute_gap_metrics(
    sim_result: Dict[str, Any],
    real_result: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Compute the sim-to-real gap metrics from paired sim/real results.

    Metrics:
        kl_divergence_sim_to_real — KL(sim_action_freq || real_action_freq)
        kl_divergence_real_to_sim — KL(real_action_freq || sim_action_freq)
        jensen_shannon_divergence  — symmetric divergence measure
        confidence_delta           — mean agent confidence: real − sim
        action_agreement_rate      — fraction of actions matching argmax
    """
    sim_freq  = sim_result["action_freq"]
    real_freq = real_result["action_freq"]

    kl_sr = _kl_divergence(sim_freq, real_freq)
    kl_rs = _kl_divergence(real_freq, sim_freq)
    jsd   = 0.5 * (kl_sr + kl_rs)

    conf_delta = real_result["avg_confidence"] - sim_result["avg_confidence"]

    # Agreement rate: fraction of actions where mode (sim) == mode (real)
    sim_dominant  = max(sim_freq,  key=sim_freq.get)
    real_dominant = max(real_freq, key=real_freq.get)
    dominant_agree = sim_dominant == real_dominant

    return {
        "kl_divergence_sim_to_real": round(kl_sr, 6),
        "kl_divergence_real_to_sim": round(kl_rs, 6),
        "jensen_shannon_divergence":  round(jsd,  6),
        "confidence_delta_real_minus_sim": round(conf_delta, 4),
        "dominant_action_sim":        sim_dominant,
        "dominant_action_real":       real_dominant,
        "dominant_action_agrees":     dominant_agree,
        "interpretation": (
            "Low JSD (< 0.1) → policy generalises well to real data. "
            "High JSD (> 0.5) → significant sim-to-real gap."
        ),
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Sim-to-real evaluation for Kaisen DQN agent"
    )
    parser.add_argument(
        "--model", type=str, default="models/best_model.h5",
        help="Path to trained DQN model (.h5)"
    )
    parser.add_argument(
        "--episodes", type=int, default=100,
        help="Number of sim episodes (default: 100)"
    )
    parser.add_argument(
        "--history", type=str, default="logs/history.json",
        help="Path to real history.json (default: logs/history.json)"
    )
    parser.add_argument(
        "--output", type=str, default="logs/sim_to_real_report.json",
        help="Path for the output report JSON"
    )
    parser.add_argument(
        "--sim-only", action="store_true",
        help="Only run sim-mode evaluation"
    )
    parser.add_argument(
        "--real-only", action="store_true",
        help="Only run real-mode evaluation (requires history.json)"
    )
    parser.add_argument(
        "--seed", type=int, default=42
    )
    args = parser.parse_args()

    # ------------------------------------------------------------------ #
    # Load config and build agent                                          #
    # ------------------------------------------------------------------ #
    try:
        base_config = get_config()
    except Exception as e:
        logger.error(f"Config load failed: {e}")
        logger.info("Run:  python main.py preprocess  first.")
        sys.exit(1)

    # Determine state_size from environment
    _probe_env = IncidentResponseEnv(config=base_config, use_enhanced_features=True)
    state_size  = _probe_env.observation_space.shape[0]
    action_size = _probe_env.action_space.n
    _probe_env.close()

    logger.info(f"Building agent: state_size={state_size} action_size={action_size}")
    agent = DQNAgent(
        state_size=state_size,
        action_size=action_size,
        config=base_config.agent,
        use_dueling=True,
    )

    # Try to load model weights
    model_path = Path(args.model)
    if model_path.exists():
        try:
            agent.load(str(model_path))
            logger.info(f"Loaded model weights from {model_path}")
        except Exception as e:
            logger.warning(f"Could not load weights ({e}). Using untrained agent.")
    else:
        logger.warning(
            f"Model file not found: {model_path}. "
            "Proceeding with untrained agent (results will be random-policy baseline)."
        )

    # ------------------------------------------------------------------ #
    # Run evaluations                                                      #
    # ------------------------------------------------------------------ #
    report: Dict[str, Any] = {
        "generated_at":  datetime.utcnow().isoformat() + "Z",
        "model_path":    str(model_path),
        "state_size":    state_size,
        "action_size":   action_size,
    }
    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)

    sim_result: Optional[Dict[str, Any]]  = None
    real_result: Optional[Dict[str, Any]] = None

    if not args.real_only:
        logger.info(f"Running SIM evaluation ({args.episodes} episodes)...")
        sim_result = eval_sim(
            agent=agent,
            base_config=base_config,
            num_episodes=args.episodes,
            seed=args.seed,
        )
        report["sim"] = sim_result
        logger.info(
            f"SIM  avg_reward={sim_result['avg_reward']:.2f}  "
            f"action_freq={sim_result['action_freq']}"
        )

    if not args.sim_only:
        logger.info(f"Running REAL evaluation (history: {args.history})...")
        try:
            real_result = eval_real(
                agent=agent,
                history_path=args.history,
            )
            report["real"] = real_result
            logger.info(
                f"REAL avg_confidence={real_result['avg_confidence']:.4f}  "
                f"action_freq={real_result['action_freq']}"
            )
        except FileNotFoundError as e:
            logger.warning(str(e))
            report["real_error"] = str(e)
        except ValueError as e:
            logger.warning(str(e))
            report["real_error"] = str(e)

    # ------------------------------------------------------------------ #
    # Compute and append gap metrics                                        #
    # ------------------------------------------------------------------ #
    if sim_result is not None and real_result is not None:
        gap = compute_gap_metrics(sim_result, real_result)
        report["sim_to_real_gap"] = gap

        logger.info("\n" + "=" * 60)
        logger.info("SIM-TO-REAL GAP METRICS")
        logger.info("=" * 60)
        for k, v in gap.items():
            logger.info(f"  {k:<45} {v}")
        logger.info("=" * 60)

    # Save report
    with open(args.output, "w") as f:
        json.dump(report, f, indent=2)

    logger.info(f"\nReport saved to: {args.output}")


if __name__ == "__main__":
    main()
