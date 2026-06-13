"""
Ablation Framework for Kaisen Incident Response RL Agent.

Systematically sweeps:
  - Reward weights: early_containment, false_positive, data_loss
  - Observation noise levels: obs_noise_std

For each configuration:
  1. Builds a fresh DQNAgent + IncidentResponseEnv
  2. Trains for `num_episodes` episodes
  3. Evaluates for `eval_episodes` episodes
  4. Logs per-config metrics to logs/ablation_results.json

Usage:
    python src/ablation.py                  # full sweep (~hours)
    python src/ablation.py --quick          # 5 episodes per config (~minutes)
    python src/ablation.py --noise-only     # noise sweep only
    python src/ablation.py --reward-only    # reward sweep only

Research contribution:
    Produces Table N in the paper demonstrating reward-shaping sensitivity
    and observation noise robustness of the DQN policy.
"""

import argparse
import copy
import json
import os
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

import numpy as np

# Adjust sys.path so this can be run from the project root
import sys
_HERE = Path(__file__).parent
if str(_HERE.parent) not in sys.path:
    sys.path.insert(0, str(_HERE.parent))

from config import get_config, Config, EnvironmentConfig
from incident_env import IncidentResponseEnv
from agent import DQNAgent


# ---------------------------------------------------------------------------
# Ablation Configuration
# ---------------------------------------------------------------------------

@dataclass
class AblationConfig:
    """
    Defines one ablation experiment cell.

    Fields:
        name:           Human-readable label (used as JSON key)
        reward_overrides: Partial dict of reward weights to override.
                          Keys must match EnvironmentConfig.rewards keys.
        noise_std:      Observation noise standard deviation (overrides default)
        attack_type:    Attack type passed to IncidentResponseEnv
    """
    name: str
    reward_overrides: Dict[str, float] = field(default_factory=dict)
    noise_std: Optional[float] = None
    attack_type: str = "random"


# ---------------------------------------------------------------------------
# Default sweep definitions
# ---------------------------------------------------------------------------

def _reward_sweep() -> List[AblationConfig]:
    """
    Sweep over early_containment, false_positive, and data_loss reward weights.
    All other reward values remain at their defaults.
    """
    configs: List[AblationConfig] = []

    for ec in [20.0, 50.0, 100.0]:
        configs.append(AblationConfig(
            name=f"early_containment={ec:.0f}",
            reward_overrides={"early_containment": ec},
        ))

    for fp in [-5.0, -10.0, -20.0]:
        configs.append(AblationConfig(
            name=f"false_positive={fp:.0f}",
            reward_overrides={"false_positive": fp},
        ))

    for dl in [-15.0, -30.0, -60.0]:
        configs.append(AblationConfig(
            name=f"data_loss={dl:.0f}",
            reward_overrides={"missed_attack": dl},
        ))

    return configs


def _noise_sweep() -> List[AblationConfig]:
    """Sweep over observation noise levels."""
    configs: List[AblationConfig] = []
    for std in [0.0, 0.5, 2.0, 5.0, 10.0]:
        configs.append(AblationConfig(
            name=f"noise_std={std}",
            noise_std=std,
        ))
    return configs


def _full_sweep() -> List[AblationConfig]:
    """Combined reward + noise sweep."""
    return _reward_sweep() + _noise_sweep()


# ---------------------------------------------------------------------------
# Build environment for a given AblationConfig
# ---------------------------------------------------------------------------

def _build_env(base_config: Config, ab_cfg: AblationConfig) -> IncidentResponseEnv:
    """
    Construct an IncidentResponseEnv with rewards and noise overridden
    by the given AblationConfig.

    We deep-copy base_config so each ablation cell is independent.
    """
    cfg = copy.deepcopy(base_config)

    # Apply reward overrides
    for key, val in ab_cfg.reward_overrides.items():
        if key in cfg.env.rewards:
            cfg.env.rewards[key] = val
        else:
            raise KeyError(
                f"Reward key '{key}' not found in EnvironmentConfig.rewards. "
                f"Valid keys: {list(cfg.env.rewards.keys())}"
            )

    # Apply noise override
    if ab_cfg.noise_std is not None:
        cfg.env.observation_noise_std = ab_cfg.noise_std

    env = IncidentResponseEnv(
        config=cfg,
        attack_type=ab_cfg.attack_type,
        use_enhanced_features=True,
    )
    return env


# ---------------------------------------------------------------------------
# Run a single ablation cell
# ---------------------------------------------------------------------------

def run_single(
    base_config: Config,
    ab_cfg: AblationConfig,
    num_episodes: int = 500,
    eval_episodes: int = 100,
    seed: int = 42,
    verbose: bool = False,
) -> Dict[str, Any]:
    """
    Train and evaluate a DQNAgent for one AblationConfig.

    Returns:
        Dict containing training and evaluation metrics for this cell.
    """
    np.random.seed(seed)

    env = _build_env(base_config, ab_cfg)
    state_size = env.observation_space.shape[0]
    action_size = env.action_space.n

    agent = DQNAgent(
        state_size=state_size,
        action_size=action_size,
        config=base_config.agent,
        use_dueling=True,
        use_n_step=False,
    )

    # ---- Training loop ----
    train_rewards: List[float] = []
    train_losses: List[float] = []

    t_start = time.time()
    for ep in range(num_episodes):
        state, _ = env.reset(seed=seed + ep)
        ep_reward = 0.0
        ep_losses: List[float] = []

        while True:
            action = agent.select_action(state, training=True)
            next_state, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated

            agent.store_experience(state, action, reward, next_state, done)
            loss = agent.train_step()
            if loss is not None:
                ep_losses.append(loss)

            ep_reward += reward
            state = next_state
            if done:
                break

        agent.end_episode()
        train_rewards.append(ep_reward)
        if ep_losses:
            train_losses.append(float(np.mean(ep_losses)))

        if verbose and (ep + 1) % max(1, num_episodes // 10) == 0:
            avg_r = float(np.mean(train_rewards[-50:]))
            print(f"  [{ab_cfg.name}] ep={ep+1}/{num_episodes}  "
                  f"avg_reward={avg_r:.2f}  eps={agent.epsilon:.3f}")

    train_time = time.time() - t_start

    # ---- Evaluation loop ----
    eval_rewards: List[float] = []
    eval_fp: List[int] = []
    eval_contained: List[int] = []
    eval_data_loss: List[int] = []
    successes = 0

    for ep in range(eval_episodes):
        state, _ = env.reset(seed=seed + num_episodes + ep)
        ep_reward = 0.0

        while True:
            action = agent.select_action(state, training=False)
            next_state, reward, terminated, truncated, info = env.step(action)
            ep_reward += reward
            state = next_state
            if terminated or truncated:
                break

        ep_stats = info.get("episode_stats", {})
        eval_rewards.append(ep_reward)
        eval_fp.append(ep_stats.get("false_positives", 0))
        eval_contained.append(ep_stats.get("attacks_contained", 0))
        eval_data_loss.append(ep_stats.get("data_loss_events", 0))

        if (ep_stats.get("attacks_contained", 0) > 0 or
                (ep_stats.get("missed_attacks", 0) == 0 and
                 ep_stats.get("false_positives", 0) == 0)):
            successes += 1

    env.close()

    return {
        "config_name":          ab_cfg.name,
        "reward_overrides":     ab_cfg.reward_overrides,
        "noise_std":            ab_cfg.noise_std,
        "num_train_episodes":   num_episodes,
        "num_eval_episodes":    eval_episodes,
        "train_time_s":         round(train_time, 2),
        # Training metrics
        "train_avg_reward_last50": float(np.mean(train_rewards[-50:])),
        "train_avg_reward_all":    float(np.mean(train_rewards)),
        "train_avg_loss":          float(np.mean(train_losses)) if train_losses else 0.0,
        "final_epsilon":           float(agent.epsilon),
        # Evaluation metrics
        "eval_avg_reward":      float(np.mean(eval_rewards)),
        "eval_std_reward":      float(np.std(eval_rewards)),
        "eval_min_reward":      float(np.min(eval_rewards)),
        "eval_max_reward":      float(np.max(eval_rewards)),
        "eval_success_rate":    float(successes / eval_episodes),
        "eval_avg_fp":          float(np.mean(eval_fp)),
        "eval_avg_contained":   float(np.mean(eval_contained)),
        "eval_avg_data_loss":   float(np.mean(eval_data_loss)),
    }


# ---------------------------------------------------------------------------
# Full ablation sweep
# ---------------------------------------------------------------------------

def run_ablation_sweep(
    configs: List[AblationConfig],
    base_config: Config,
    num_episodes: int = 500,
    eval_episodes: int = 100,
    output_path: str = "logs/ablation_results.json",
    seed: int = 42,
    verbose: bool = True,
) -> List[Dict[str, Any]]:
    """
    Run the full ablation sweep over the given list of AblationConfigs.

    Args:
        configs:       List of AblationConfig objects to sweep.
        base_config:   Master Config to derive each cell from.
        num_episodes:  Training episodes per cell.
        eval_episodes: Evaluation episodes per cell.
        output_path:   Where to write the JSON results.
        seed:          Base random seed (offset per config).
        verbose:       Print progress.

    Returns:
        List of result dicts (one per ablation cell).
    """
    results: List[Dict[str, Any]] = []

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    total = len(configs)
    print(f"\n{'='*60}")
    print(f"Ablation sweep: {total} configurations")
    print(f"  train_episodes = {num_episodes}  |  eval_episodes = {eval_episodes}")
    print(f"  output → {output_path}")
    print(f"{'='*60}\n")

    for i, ab_cfg in enumerate(configs):
        print(f"[{i+1}/{total}] {ab_cfg.name}")
        cell_seed = seed + i * 1000

        try:
            result = run_single(
                base_config=base_config,
                ab_cfg=ab_cfg,
                num_episodes=num_episodes,
                eval_episodes=eval_episodes,
                seed=cell_seed,
                verbose=verbose,
            )
            results.append(result)

            if verbose:
                print(f"  ✓  eval_avg_reward={result['eval_avg_reward']:.2f}"
                      f"  success_rate={result['eval_success_rate']:.2%}"
                      f"  fp={result['eval_avg_fp']:.2f}")

        except Exception as e:
            print(f"  ✗  FAILED: {e}")
            results.append({
                "config_name":    ab_cfg.name,
                "reward_overrides": ab_cfg.reward_overrides,
                "noise_std":      ab_cfg.noise_std,
                "error":          str(e),
            })

    # Persist results
    metadata = {
        "generated_at":  datetime.utcnow().isoformat() + "Z",
        "num_episodes":  num_episodes,
        "eval_episodes": eval_episodes,
        "results":       results,
    }
    with open(output_path, "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"\n{'='*60}")
    print(f"Ablation complete. Results saved to: {output_path}")
    print(f"{'='*60}\n")

    return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Ablation sweep for Kaisen DQN incident response agent"
    )
    parser.add_argument(
        "--quick", action="store_true",
        help="Run 5 train + 10 eval episodes per config (for smoke testing)"
    )
    parser.add_argument(
        "--episodes", type=int, default=500,
        help="Training episodes per ablation cell (default: 500)"
    )
    parser.add_argument(
        "--eval-episodes", type=int, default=100,
        help="Evaluation episodes per ablation cell (default: 100)"
    )
    parser.add_argument(
        "--noise-only", action="store_true",
        help="Run noise sweep only (skip reward sweep)"
    )
    parser.add_argument(
        "--reward-only", action="store_true",
        help="Run reward sweep only (skip noise sweep)"
    )
    parser.add_argument(
        "--output", type=str, default="logs/ablation_results.json",
        help="Output JSON file path"
    )
    parser.add_argument(
        "--seed", type=int, default=42,
        help="Base random seed"
    )
    parser.add_argument(
        "--verbose", action="store_true", default=True,
        help="Print per-episode progress"
    )
    args = parser.parse_args()

    num_episodes  = 5   if args.quick else args.episodes
    eval_episodes = 10  if args.quick else args.eval_episodes

    # Build sweep list
    if args.noise_only:
        configs = _noise_sweep()
    elif args.reward_only:
        configs = _reward_sweep()
    else:
        configs = _full_sweep()

    # Load base config (requires extracted_params.json)
    try:
        base_config = get_config()
    except Exception as e:
        print(f"ERROR loading config: {e}")
        print("Run:  python main.py preprocess  first.")
        sys.exit(1)

    run_ablation_sweep(
        configs=configs,
        base_config=base_config,
        num_episodes=num_episodes,
        eval_episodes=eval_episodes,
        output_path=args.output,
        seed=args.seed,
        verbose=args.verbose,
    )


if __name__ == "__main__":
    main()
