"""
Configuration Module for Kaisen Research Paper Evaluation

This module defines:
1. Random seeds for 5-seed reproducible experiments
2. Feature space constants (13-feature full set, 5-feature network subset)
3. Hyperparameters extracted from adversarial_eval_simple.py and agent.py
4. File paths to all data directories
5. Evaluation constants

Feature Schema (Full 13-feature set):
  1. cpu_usage (0.0-100.0)
  2. memory_usage (0.0-100.0)
  3. process_count (0.0-500.0)
  4. network_connections (0.0-1000.0)
  5. unique_ips (0.0-50.0)
  6. failed_logins (0.0-100.0)
  7. lateral_movement (0.0-1.0)
  8. port_scan_score (0.0-1.0)
  9. resource_exhaustion (0.0-1.0)
  10. entropy_spike (0.0-1.0)
  11. connection_rate (0.0-100.0)
  12. anomaly_score (0.0-1.0)
  13. previous_anomaly_score (0.0-1.0)

Network Subset (5 features):
  - cpu_usage
  - memory_usage
  - network_connections
  - unique_ips
  - connection_rate
"""

import os
from pathlib import Path
from typing import Dict, List, Tuple

# ============================================================================
# PROJECT PATHS
# ============================================================================

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
EVAL_ROOT = Path(__file__).parent.resolve()

# Data directories
DATA_DIR = EVAL_ROOT / "data"
RESULTS_DIR = EVAL_ROOT / "results"
FIGURES_DIR = EVAL_ROOT / "figures"
RESEARCH_DOCS_DIR = PROJECT_ROOT / "ResearchDocs"
RESEARCH_IMAGES_DIR = RESEARCH_DOCS_DIR / "images"

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)
RESEARCH_IMAGES_DIR.mkdir(parents=True, exist_ok=True)

# Data file paths
SYNTHETIC_DATA_PATH = DATA_DIR / "synthetic_full.json"
REPRODUCIBILITY_REPORT_PATH = DATA_DIR / "reproducibility_report.json"

# ============================================================================
# RANDOM SEEDS (5-seed experiments for statistical significance)
# ============================================================================

RANDOM_SEEDS: List[int] = [42, 123, 456, 789, 999]
"""
Five random seeds for reproducible experiments.
Used in:
  - Data generation randomization
  - Neural network weight initialization
  - Training/validation/test splits
  - Adversarial attack perturbations
"""

# ============================================================================
# FEATURE SPACE CONFIGURATION
# ============================================================================

# Feature count constant: use 13 as full OS-layer feature set
FEATURE_COUNT_FULL: int = 13
FEATURE_COUNT_NETWORK: int = 5

# Full 13-feature OS-layer space (from adversarial_eval_simple.py)
FEATURES_FULL_SCHEMA: Dict[str, Tuple[float, float]] = {
    "cpu_usage": (0.0, 100.0),
    "memory_usage": (0.0, 100.0),
    "process_count": (0.0, 500.0),
    "network_connections": (0.0, 1000.0),
    "unique_ips": (0.0, 50.0),
    "failed_logins": (0.0, 100.0),
    "lateral_movement": (0.0, 1.0),
    "port_scan_score": (0.0, 1.0),
    "resource_exhaustion": (0.0, 1.0),
    "entropy_spike": (0.0, 1.0),
    "connection_rate": (0.0, 100.0),
    "anomaly_score": (0.0, 1.0),
    "previous_anomaly_score": (0.0, 1.0),
}

# Network subset (5 features, public CICIDS2017/2018 compatible)
FEATURES_NETWORK_SUBSET: Dict[str, Tuple[float, float]] = {
    "cpu_usage": (0.0, 100.0),
    "memory_usage": (0.0, 100.0),
    "network_connections": (0.0, 1000.0),
    "unique_ips": (0.0, 50.0),
    "connection_rate": (0.0, 100.0),
}

# Feature descriptions for paper
FEATURE_DESCRIPTIONS: Dict[str, str] = {
    "cpu_usage": "CPU utilization percentage",
    "memory_usage": "Memory utilization percentage",
    "process_count": "Number of active processes",
    "network_connections": "Total network connections",
    "unique_ips": "Number of unique IPs connected",
    "failed_logins": "Failed login attempts",
    "lateral_movement": "Lateral movement score (0-1)",
    "port_scan_score": "Port scanning activity score (0-1)",
    "resource_exhaustion": "Resource exhaustion score (0-1)",
    "entropy_spike": "Entropy spike score (0-1)",
    "connection_rate": "Connection rate per second",
    "anomaly_score": "Current anomaly score (0-1)",
    "previous_anomaly_score": "Previous timestep anomaly score (0-1)",
}

# ============================================================================
# DQN AGENT HYPERPARAMETERS (from agent.py config.py)
# ============================================================================

HYPERPARAMETERS: Dict = {
    # Network architecture
    "hidden_layers": [128, 64, 32],
    "activation": "relu",
    "use_dueling": False,
    
    # Learning parameters
    "learning_rate": 1e-3,
    "gamma": 0.99,  # Discount factor
    
    # Exploration
    "epsilon_start": 1.0,
    "epsilon_end": 0.01,
    "epsilon_decay": 0.995,
    
    # Replay buffer
    "buffer_size": 10000,
    "batch_size": 64,
    
    # Training
    "target_update_freq": 10,
    "num_episodes": 1000,
    "max_steps_per_episode": 100,
    
    # Model saving
    "save_freq": 100,
}

# ============================================================================
# ADVERSARIAL ATTACK PARAMETERS (from adversarial_eval_simple.py)
# ============================================================================

ADVERSARIAL_PARAMS: Dict = {
    # Attack hyperparameters
    "epsilon": 0.15,  # Maximum perturbation magnitude
    "fgsm_step_size": 0.01,  # FGSM step size
    "pgd_num_steps": 20,  # PGD iterations
    "pgd_step_size": 0.01,  # PGD step size
    
    # Attack methods to test
    "attack_methods": ["fgsm", "pgd", "feature_clipping", "random"],
}

# ============================================================================
# AGENT ACTIONS (from agent.py, LLM-agent layer)
# ============================================================================

AGENT_ACTIONS: List[str] = [
    "do_nothing",      # 0: No intervention
    "block_ip",        # 1: Block suspicious IP
    "lock_account",    # 2: Lock user account
    "terminate_process",  # 3: Terminate suspicious process
    "isolate_host"     # 4: Isolate host from network
]

AGENT_ACTION_COUNT: int = len(AGENT_ACTIONS)

# ============================================================================
# LLM-AGENT LAYER FEATURES (12D state space)
# ============================================================================

AGENT_LAYER_FEATURES: Dict[str, Tuple[float, float]] = {
    "tool_call_rate": (0.0, 100.0),              # Tools/minute
    "tool_refusal_rate": (0.0, 1.0),              # Fraction of refusals
    "session_entropy": (0.0, 5.0),                # Shannon entropy of action distribution
    "repeated_prompts": (0, 50),                  # Count of identical prompts
    "jailbreak_pattern_score": (0.0, 1.0),        # Pattern match score
    "memory_access_rate": (0.0, 100.0),           # Memory operations/minute
    "file_access_depth": (0, 10),                 # Directory depth accessed
    "api_call_rate": (0.0, 100.0),                # External API calls/minute
    "privilege_escalation_attempts": (0, 10),     # PE attempts
    "lateral_movement_score": (0.0, 1.0),         # Lateral movement likelihood
    "data_exfiltration_rate": (0.0, 100.0),       # Data volume/minute
    "previous_agent_anomaly": (0.0, 1.0),         # Previous timestep score
}

AGENT_LAYER_FEATURE_COUNT: int = len(AGENT_LAYER_FEATURES)

# ============================================================================
# EVALUATION CONSTANTS
# ============================================================================

# Attack scenarios for evaluation
ATTACK_SCENARIOS = [
    "os_attack_only",          # Scenario 1: OS-layer attack alone
    "agent_attack_only",       # Scenario 2: Agent-layer attack alone
    "synchronized_attack"      # Scenario 3: Coordinated OS + agent attack
]

# Baseline comparison methods
BASELINES_OS_LAYER = [
    "isolation_forest",
    "one_class_svm",
    "threshold_rule",
    "lstm_autoencoder"
]

BASELINES_AGENT_LAYER = [
    "entropy_threshold",
    "logistic_regression",
    "perplexity_threshold"
]

BASELINES_JOINT = [
    "max_score_fusion",  # naive baseline for arbitration
]

# Metrics to compute
METRICS_NAMES = [
    "accuracy",
    "precision",
    "recall",
    "f1_score",
    "auc_roc",
    "false_positive_rate",
    "false_negative_rate",
    "detection_latency_ms"
]

# ============================================================================
# REPRODUCIBILITY CONFIGURATION
# ============================================================================

# Test sizes (for train/val/test splits)
TRAIN_SIZE = 0.7
VAL_SIZE = 0.15
TEST_SIZE = 0.15

# Synchronized attack construction
# These are trigger conditions for detecting attacks that need BOTH layers
SYNCHRONIZED_ATTACK_TRIGGERS = {
    "temporal_window_seconds": 5.0,  # Window for temporal co-occurrence
    "os_layer_anomaly_threshold": 0.6,
    "agent_layer_anomaly_threshold": 0.6,
    "correlation_weight": 0.3,  # Weight for correlation term in arbitration
}

# ============================================================================
# OUTPUT PATHS (for paper generation)
# ============================================================================

# CSV result files
CSV_PATHS = {
    "os_layer_results": RESULTS_DIR / "os_layer_results.csv",
    "agent_layer_results": RESULTS_DIR / "agent_layer_results.csv",
    "joint_results": RESULTS_DIR / "joint_results.csv",
    "ablation_results": RESULTS_DIR / "ablation_results.csv",
    "statistical_tests": RESULTS_DIR / "statistical_tests.csv",
}

# Figure output paths
FIGURE_PATHS = {
    "roc_curves_os": FIGURES_DIR / "01_roc_os_layer.pdf",
    "roc_curves_agent": FIGURES_DIR / "02_roc_agent_layer.pdf",
    "roc_curves_joint": FIGURES_DIR / "03_roc_joint_layer.pdf",
    "pr_curves_joint": FIGURES_DIR / "04_pr_curves_joint.pdf",
    "confusion_matrix": FIGURES_DIR / "05_confusion_matrices.pdf",
    "detection_latency": FIGURES_DIR / "06_detection_latency_dist.pdf",
    "training_curves": FIGURES_DIR / "07_training_curves.pdf",
    "ablation_chart": FIGURES_DIR / "08_ablation_f1_chart.pdf",
    "shap_summary": FIGURES_DIR / "09_shap_feature_importance.pdf",
    "sim_to_real_gap": FIGURES_DIR / "10_sim_to_real_kl_divergence.pdf",
    "scalability_plot": FIGURES_DIR / "11_scalability_latency.pdf",
}

# ============================================================================
# VERIFICATION HELPER FUNCTIONS
# ============================================================================

def verify_feature_schema() -> bool:
    """Verify that feature schema is complete and consistent."""
    assert len(FEATURES_FULL_SCHEMA) == FEATURE_COUNT_FULL, \
        f"Full feature schema has {len(FEATURES_FULL_SCHEMA)} features, expected {FEATURE_COUNT_FULL}"
    
    assert len(FEATURES_NETWORK_SUBSET) == FEATURE_COUNT_NETWORK, \
        f"Network subset has {len(FEATURES_NETWORK_SUBSET)} features, expected {FEATURE_COUNT_NETWORK}"
    
    assert all(name in FEATURES_FULL_SCHEMA for name in FEATURES_NETWORK_SUBSET.keys()), \
        "Network subset contains features not in full schema"
    
    return True


def verify_seeds() -> bool:
    """Verify that we have exactly 5 seeds."""
    assert len(RANDOM_SEEDS) == 5, f"Expected 5 seeds, got {len(RANDOM_SEEDS)}"
    assert all(isinstance(s, int) and s > 0 for s in RANDOM_SEEDS), "All seeds must be positive integers"
    return True


if __name__ == "__main__":
    print("=" * 70)
    print("KAISEN EVALUATION CONFIG VERIFICATION")
    print("=" * 70)
    
    print("\n✓ Feature Schema:")
    print(f"  - Full (OS-layer): {FEATURE_COUNT_FULL} features")
    verify_feature_schema()
    print(f"  - Network subset: {FEATURE_COUNT_NETWORK} features")
    
    print("\n✓ Random Seeds (5-seed experiments):")
    verify_seeds()
    print(f"  - {RANDOM_SEEDS}")
    
    print("\n✓ Hyperparameters:")
    print(f"  - Learning rate: {HYPERPARAMETERS['learning_rate']}")
    print(f"  - Discount factor (gamma): {HYPERPARAMETERS['gamma']}")
    print(f"  - Hidden layers: {HYPERPARAMETERS['hidden_layers']}")
    
    print("\n✓ Directory Structure:")
    print(f"  - Data: {DATA_DIR}")
    print(f"  - Results: {RESULTS_DIR}")
    print(f"  - Figures: {FIGURES_DIR}")
    
    print("\n✓ Attack Scenarios: {0}".format(", ".join(ATTACK_SCENARIOS)))
    print(f"\n✓ Agent Actions ({AGENT_ACTION_COUNT}): {', '.join(AGENT_ACTIONS)}")
    
    print("\n" + "=" * 70)
    print("All configuration checks passed!")
    print("=" * 70)
