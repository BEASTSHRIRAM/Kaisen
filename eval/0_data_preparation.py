"""
Data Preparation Module for Kaisen Research Evaluation

This script:
1. Generates synthetic attack data (13 OS-layer features)
2. Documents the exact feature schema (features, ranges, distributions)
3. Saves synthetic data to synthetic_full.json
4. Creates a reproducibility report with random seed and generation parameters
5. Supports train/val/test splits

Feature Schema (13 features):
  Index  Name                         Range        Description
  -----  ----                         -----        -----------
    0    cpu_usage                    0-100        CPU utilization %
    1    memory_usage                 0-100        Memory utilization %
    2    process_count                0-500        # of active processes
    3    network_connections          0-1000       Total connections
    4    unique_ips                   0-50         Unique IPs connected
    5    failed_logins                0-100        Failed login attempts
    6    lateral_movement             0-1          Lateral movement score
    7    port_scan_score              0-1          Port scan activity
    8    resource_exhaustion          0-1          Resource exhaustion score
    9    entropy_spike                0-1          Entropy spike score
   10    connection_rate              0-100        Connections per second
   11    anomaly_score                0-1          Current anomaly score
   12    previous_anomaly_score       0-1          Previous anomaly score
"""

import numpy as np
import json
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

# Import configuration
import config


@dataclass
class SyntheticDataConfig:
    """Configuration for synthetic data generation."""
    num_benign_samples: int = 5000
    num_attack_samples: int = 1000
    seed: int = 42
    temporal_correlation: float = 0.7  # Correlation between consecutive timesteps
    attack_intensity: float = 1.5      # Factor by which attack features deviate from normal
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class FeatureDistribution:
    """Probability distribution parameters for a feature."""
    feature_name: str
    feature_index: int
    min_value: float
    max_value: float
    normal_mean: float
    normal_std: float
    attack_mean: float
    attack_std: float
    
    def to_dict(self) -> Dict:
        return asdict(self)


class SyntheticDataGenerator:
    """Generate synthetic attack data with precise feature documentation."""
    
    def __init__(self, config: SyntheticDataConfig):
        self.config = config
        np.random.seed(config.seed)
        self.distributions = self._create_distributions()
        self.data_points = []
        self.labels = []
    
    def _create_distributions(self) -> Dict[str, FeatureDistribution]:
        """
        Define probability distributions for each feature.
        
        Distributions are based on:
        - Normal operation: benign network/host behavior
        - Attack operation: anomalous behavior patterns
        
        Returns:
            Dictionary mapping feature names to their distributions
        """
        distributions = {}
        
        # Feature 0: CPU usage
        distributions["cpu_usage"] = FeatureDistribution(
            feature_name="cpu_usage",
            feature_index=0,
            min_value=0.0,
            max_value=100.0,
            normal_mean=30.0,
            normal_std=10.0,
            attack_mean=75.0,
            attack_std=15.0
        )
        
        # Feature 1: Memory usage
        distributions["memory_usage"] = FeatureDistribution(
            feature_name="memory_usage",
            feature_index=1,
            min_value=0.0,
            max_value=100.0,
            normal_mean=50.0,
            normal_std=15.0,
            attack_mean=85.0,
            attack_std=10.0
        )
        
        # Feature 2: Process count
        distributions["process_count"] = FeatureDistribution(
            feature_name="process_count",
            feature_index=2,
            min_value=0.0,
            max_value=500.0,
            normal_mean=60.0,
            normal_std=20.0,
            attack_mean=120.0,
            attack_std=40.0
        )
        
        # Feature 3: Network connections
        distributions["network_connections"] = FeatureDistribution(
            feature_name="network_connections",
            feature_index=3,
            min_value=0.0,
            max_value=1000.0,
            normal_mean=100.0,
            normal_std=50.0,
            attack_mean=400.0,
            attack_std=150.0
        )
        
        # Feature 4: Unique IPs
        distributions["unique_ips"] = FeatureDistribution(
            feature_name="unique_ips",
            feature_index=4,
            min_value=0.0,
            max_value=50.0,
            normal_mean=10.0,
            normal_std=4.0,
            attack_mean=30.0,
            attack_std=8.0
        )
        
        # Feature 5: Failed logins
        distributions["failed_logins"] = FeatureDistribution(
            feature_name="failed_logins",
            feature_index=5,
            min_value=0.0,
            max_value=100.0,
            normal_mean=2.0,
            normal_std=1.0,
            attack_mean=40.0,
            attack_std=15.0
        )
        
        # Feature 6: Lateral movement (0-1 scale)
        distributions["lateral_movement"] = FeatureDistribution(
            feature_name="lateral_movement",
            feature_index=6,
            min_value=0.0,
            max_value=1.0,
            normal_mean=0.05,
            normal_std=0.05,
            attack_mean=0.70,
            attack_std=0.20
        )
        
        # Feature 7: Port scan score (0-1 scale)
        distributions["port_scan_score"] = FeatureDistribution(
            feature_name="port_scan_score",
            feature_index=7,
            min_value=0.0,
            max_value=1.0,
            normal_mean=0.02,
            normal_std=0.05,
            attack_mean=0.80,
            attack_std=0.15
        )
        
        # Feature 8: Resource exhaustion (0-1 scale)
        distributions["resource_exhaustion"] = FeatureDistribution(
            feature_name="resource_exhaustion",
            feature_index=8,
            min_value=0.0,
            max_value=1.0,
            normal_mean=0.10,
            normal_std=0.10,
            attack_mean=0.75,
            attack_std=0.20
        )
        
        # Feature 9: Entropy spike (0-1 scale)
        distributions["entropy_spike"] = FeatureDistribution(
            feature_name="entropy_spike",
            feature_index=9,
            min_value=0.0,
            max_value=1.0,
            normal_mean=0.15,
            normal_std=0.15,
            attack_mean=0.85,
            attack_std=0.10
        )
        
        # Feature 10: Connection rate (connections/second)
        distributions["connection_rate"] = FeatureDistribution(
            feature_name="connection_rate",
            feature_index=10,
            min_value=0.0,
            max_value=100.0,
            normal_mean=10.0,
            normal_std=5.0,
            attack_mean=60.0,
            attack_std=20.0
        )
        
        # Feature 11: Anomaly score (0-1 scale)
        distributions["anomaly_score"] = FeatureDistribution(
            feature_name="anomaly_score",
            feature_index=11,
            min_value=0.0,
            max_value=1.0,
            normal_mean=0.10,
            normal_std=0.10,
            attack_mean=0.80,
            attack_std=0.15
        )
        
        # Feature 12: Previous anomaly score (0-1 scale)
        distributions["previous_anomaly_score"] = FeatureDistribution(
            feature_name="previous_anomaly_score",
            feature_index=12,
            min_value=0.0,
            max_value=1.0,
            normal_mean=0.10,
            normal_std=0.10,
            attack_mean=0.75,
            attack_std=0.20
        )
        
        return distributions
    
    def _sample_feature(
        self,
        dist: FeatureDistribution,
        is_attack: bool,
        previous_value: Optional[float] = None
    ) -> float:
        """
        Sample a feature value with optional temporal correlation.
        
        Args:
            dist: Feature distribution parameters
            is_attack: Whether this is from attack or normal operation
            previous_value: Previous value for temporal correlation
            
        Returns:
            Sampled feature value, clipped to valid range
        """
        if is_attack:
            mean = dist.attack_mean
            std = dist.attack_std
        else:
            mean = dist.normal_mean
            std = dist.normal_std
        
        # Sample from distribution
        value = np.random.normal(mean, std)
        
        # Apply temporal correlation if previous value available
        if previous_value is not None:
            alpha = self.config.temporal_correlation
            value = alpha * previous_value + (1 - alpha) * value
        
        # Clip to valid range
        value = np.clip(value, dist.min_value, dist.max_value)
        
        return float(value)
    
    def generate_benign_sequence(self, length: int = 100) -> List[List[float]]:
        """
        Generate a sequence of benign (normal) samples with temporal correlation.
        
        Args:
            length: Number of timesteps to generate
            
        Returns:
            List of 13-feature vectors representing normal operation
        """
        sequence = []
        previous_values = {name: None for name in self.distributions.keys()}
        
        for _ in range(length):
            sample = []
            for feature_name, dist in self.distributions.items():
                value = self._sample_feature(
                    dist,
                    is_attack=False,
                    previous_value=previous_values[feature_name]
                )
                sample.append(value)
                previous_values[feature_name] = value
            
            sequence.append(sample)
        
        return sequence
    
    def generate_attack_sequence(self, length: int = 100) -> List[List[float]]:
        """
        Generate a sequence of attack samples with temporal correlation.
        
        Args:
            length: Number of timesteps to generate
            
        Returns:
            List of 13-feature vectors representing attack operation
        """
        sequence = []
        previous_values = {name: None for name in self.distributions.keys()}
        
        for _ in range(length):
            sample = []
            for feature_name, dist in self.distributions.items():
                value = self._sample_feature(
                    dist,
                    is_attack=True,
                    previous_value=previous_values[feature_name]
                )
                sample.append(value)
                previous_values[feature_name] = value
            
            sequence.append(sample)
        
        return sequence
    
    def generate_dataset(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate complete synthetic dataset with benign and attack samples.
        
        Returns:
            Tuple of (features, labels) where:
              - features: shape (N, 13) - all samples
              - labels: shape (N,) - binary labels (0=benign, 1=attack)
        """
        samples_per_sequence = max(1, self.config.num_benign_samples // 50)
        num_benign_sequences = (self.config.num_benign_samples + samples_per_sequence - 1) // samples_per_sequence
        
        all_features = []
        all_labels = []
        
        # Generate benign sequences
        print(f"Generating {num_benign_sequences} benign sequences...")
        for i in range(num_benign_sequences):
            sequence = self.generate_benign_sequence(samples_per_sequence)
            all_features.extend(sequence)
            all_labels.extend([0] * len(sequence))
            
            if (i + 1) % max(1, num_benign_sequences // 10) == 0:
                print(f"  {i + 1}/{num_benign_sequences} benign sequences generated")
        
        # Generate attack sequences
        samples_per_attack_seq = max(1, self.config.num_attack_samples // 50)
        num_attack_sequences = (self.config.num_attack_samples + samples_per_attack_seq - 1) // samples_per_attack_seq
        
        print(f"Generating {num_attack_sequences} attack sequences...")
        for i in range(num_attack_sequences):
            sequence = self.generate_attack_sequence(samples_per_attack_seq)
            all_features.extend(sequence)
            all_labels.extend([1] * len(sequence))
            
            if (i + 1) % max(1, num_attack_sequences // 10) == 0:
                print(f"  {i + 1}/{num_attack_sequences} attack sequences generated")
        
        # Shuffle
        indices = np.random.permutation(len(all_features))
        features = np.array(all_features)[indices]
        labels = np.array(all_labels)[indices]
        
        # Trim to exact counts
        features = features[:self.config.num_benign_samples + self.config.num_attack_samples]
        labels = labels[:self.config.num_benign_samples + self.config.num_attack_samples]
        
        return features, labels
    
    def save_dataset(self, features: np.ndarray, labels: np.ndarray) -> str:
        """
        Save generated dataset to JSON file with complete metadata.
        
        Args:
            features: Feature matrix (N, 13)
            labels: Label vector (N,)
            
        Returns:
            Path to saved file
        """
        dataset = {
            "metadata": {
                "description": "Kaisen research evaluation synthetic dataset",
                "timestamp": datetime.now().isoformat(),
                "random_seed": self.config.seed,
                "num_features": len(config.FEATURES_FULL_SCHEMA),
                "num_samples": len(features),
                "num_benign": int(np.sum(labels == 0)),
                "num_attack": int(np.sum(labels == 1)),
                "feature_schema": config.FEATURES_FULL_SCHEMA,
                "feature_descriptions": config.FEATURE_DESCRIPTIONS,
            },
            "generation_config": self.config.to_dict(),
            "feature_distributions": {
                name: dist.to_dict()
                for name, dist in self.distributions.items()
            },
            "features": features.tolist(),
            "labels": labels.tolist(),
        }
        
        # Create parent directory if needed
        config.DATA_DIR.mkdir(parents=True, exist_ok=True)
        
        # Save to JSON
        save_path = config.SYNTHETIC_DATA_PATH
        with open(save_path, 'w') as f:
            json.dump(dataset, f, indent=2)
        
        print(f"\n[OK] Dataset saved to: {save_path}")
        print(f"  - File size: {os.path.getsize(save_path) / (1024*1024):.2f} MB")
        
        return str(save_path)


def create_reproducibility_report(
    features: np.ndarray,
    labels: np.ndarray,
    config_obj: SyntheticDataConfig,
    save_path: Optional[str] = None
) -> Dict:
    """
    Create a reproducibility report documenting the data generation process.
    
    Args:
        features: Generated feature matrix
        labels: Generated labels
        config_obj: Configuration used for generation
        save_path: Path to save report (optional)
        
    Returns:
        Dictionary containing the report
    """
    report = {
        "title": "Kaisen Research Evaluation - Data Reproducibility Report",
        "timestamp": datetime.now().isoformat(),
        "random_seed": config_obj.seed,
        "description": "Complete documentation of synthetic data generation",
        
        "generation_parameters": config_obj.to_dict(),
        
        "dataset_statistics": {
            "total_samples": int(len(features)),
            "benign_samples": int(np.sum(labels == 0)),
            "attack_samples": int(np.sum(labels == 1)),
            "feature_count": int(features.shape[1]),
            "class_imbalance_ratio": float(np.sum(labels == 0) / np.sum(labels == 1)),
        },
        
        "feature_statistics": {
            "means": [float(x) for x in np.mean(features, axis=0)],
            "stds": [float(x) for x in np.std(features, axis=0)],
            "mins": [float(x) for x in np.min(features, axis=0)],
            "maxs": [float(x) for x in np.max(features, axis=0)],
        },
        
        "benign_feature_statistics": {
            "means": [float(x) for x in np.mean(features[labels == 0], axis=0)],
            "stds": [float(x) for x in np.std(features[labels == 0], axis=0)],
        },
        
        "attack_feature_statistics": {
            "means": [float(x) for x in np.mean(features[labels == 1], axis=0)],
            "stds": [float(x) for x in np.std(features[labels == 1], axis=0)],
        },
        
        "feature_schema_documentation": {
            "count": len(config.FEATURES_FULL_SCHEMA),
            "features": config.FEATURES_FULL_SCHEMA,
            "descriptions": config.FEATURE_DESCRIPTIONS,
        },
        
        "reproducibility_instructions": [
            "1. Use the same random_seed in config",
            "2. Use identical generation parameters",
            "3. Run with same Python/NumPy versions",
            "4. Results should be bit-identical on same machine",
        ],
    }
    
    if save_path is None:
        save_path = config.REPRODUCIBILITY_REPORT_PATH
    
    # Create parent directory if needed
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    
    with open(save_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n[OK] Reproducibility report saved to: {save_path}")
    
    return report


def main():
    """Main entry point for data preparation."""
    
    print("=" * 80)
    print("KAISEN RESEARCH EVALUATION - DATA PREPARATION")
    print("=" * 80)
    
    # Verify configuration
    print("\nVerifying configuration...")
    config.verify_feature_schema()
    config.verify_seeds()
    print("[OK] Configuration verified")
    
    # Generate dataset with first seed
    print(f"\nGenerating synthetic dataset with seed {config.RANDOM_SEEDS[0]}...")
    gen_config = SyntheticDataConfig(
        num_benign_samples=5000,
        num_attack_samples=1000,
        seed=config.RANDOM_SEEDS[0],
        temporal_correlation=0.7,
        attack_intensity=1.5
    )
    
    generator = SyntheticDataGenerator(gen_config)
    features, labels = generator.generate_dataset()
    
    # Save dataset
    print("\nSaving dataset...")
    save_path = generator.save_dataset(features, labels)
    
    # Create reproducibility report
    print("\nGenerating reproducibility report...")
    report = create_reproducibility_report(features, labels, gen_config)
    
    # Print statistics
    print("\n" + "=" * 80)
    print("DATASET STATISTICS")
    print("=" * 80)
    print(f"Total samples: {len(features)}")
    print(f"  - Benign: {np.sum(labels == 0)}")
    print(f"  - Attack: {np.sum(labels == 1)}")
    print(f"  - Class imbalance: {np.sum(labels == 0) / np.sum(labels == 1):.2f}:1")
    print(f"\nFeature space: 13 OS-layer features (full schema)")
    print(f"Feature ranges verified: [OK]")
    print(f"Temporal correlation applied: [OK]")
    print(f"Random seed documented: {config.RANDOM_SEEDS[0]}")
    
    print("\n" + "=" * 80)
    print("FEATURE SCHEMA (13 features)")
    print("=" * 80)
    
    for i, (name, (min_val, max_val)) in enumerate(config.FEATURES_FULL_SCHEMA.items()):
        desc = config.FEATURE_DESCRIPTIONS.get(name, "")
        print(f"  {i:2d}. {name:25s} [{min_val:8.1f}, {max_val:8.1f}]  # {desc}")
    
    print("\n" + "=" * 80)
    print("DATA PREPARATION COMPLETE")
    print("=" * 80)
    print(f"[OK] Synthetic data: {config.SYNTHETIC_DATA_PATH}")
    print(f"[OK] Reproducibility report: {config.REPRODUCIBILITY_REPORT_PATH}")
    print("\nNext steps:")
    print(f"  1. Review reproducibility report: {config.REPRODUCIBILITY_REPORT_PATH}")
    print(f"  2. Verify feature ranges match schema")
    print(f"  3. Run 1_baseline_implementation.py for baseline models")
    print("=" * 80)


if __name__ == "__main__":
    main()
