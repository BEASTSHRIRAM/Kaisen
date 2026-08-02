#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kaisen Research - CICIDS2017 Real Dataset Loader
Loads the CICIDS2017 dataset from ResearchDocs/datasets/ 
Maps 80+ network features to Kaisen's 13-feature OS-layer
"""

import sys
import os
import io

# Set encoding for printing
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from typing import Tuple

# Add paths
PROJECT_ROOT = Path(__file__).parent.parent
CICIDS_DIR = PROJECT_ROOT / "ResearchDocs" / "datasets" / "MachineLearningCSV" / "MachineLearningCVE"

class CICIDS2017Loader:
    """Load and preprocess CICIDS2017 dataset"""
    
    def __init__(self):
        self.data = None
        self.X = None
        self.y = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.scaler = StandardScaler()
        
    def load_all_days(self):
        """Load all 5 days of CICIDS2017 data"""
        print("=" * 70)
        print("LOADING CICIDS2017 DATASET")
        print("=" * 70)
        
        csv_files = sorted(CICIDS_DIR.glob("*.csv"))
        dfs = []
        
        print(f"\nFound {len(csv_files)} CSV files")
        
        for i, file in enumerate(csv_files, 1):
            print(f"  [{i}] Loading {file.name}...", end=" ")
            try:
                df = pd.read_csv(file, low_memory=False)
                dfs.append(df)
                print(f"OK ({len(df)} rows)")
            except Exception as e:
                print(f"FAILED Error: {e}")
                continue
        
        if not dfs:
            raise ValueError("No CSV files loaded successfully")
        
        print(f"\nCombining {len(dfs)} files...")
        self.data = pd.concat(dfs, ignore_index=True)
        print(f"Total rows: {len(self.data):,}")
        print(f"Total columns: {len(self.data.columns)}")
        
        return self.data
    
    def extract_labels(self):
        """Extract and binarize labels (Normal vs Attack)"""
        print("\n" + "=" * 70)
        print("EXTRACTING LABELS")
        print("=" * 70)
        
        # Find label column (various names possible)
        label_col = None
        for col in self.data.columns:
            if 'label' in col.lower() or 'class' in col.lower():
                label_col = col
                break
        
        if label_col is None:
            raise ValueError(f"No label column found. Columns: {self.data.columns.tolist()}")
        
        print(f"\nLabel column: '{label_col}'")
        print(f"Unique labels:")
        
        label_counts = self.data[label_col].value_counts()
        for label, count in label_counts.items():
            pct = count / len(self.data) * 100
            print(f"  {label}: {count:,} ({pct:.1f}%)")
        
        # Binarize: Normal = 0, Attack = 1
        try:
            self.y = (self.data[label_col].str.lower() != 'benign').astype(int)
        except:
            # Handle encoding issues
            self.y = (self.data[label_col].astype(str).str.lower().str.strip() != 'benign').astype(int)
        
        attack_count = self.y.sum()
        normal_count = len(self.y) - attack_count
        attack_pct = attack_count / len(self.y) * 100
        
        print(f"\nBinarized labels:")
        print(f"  Normal (0): {normal_count:,}")
        print(f"  Attack (1): {attack_count:,} ({attack_pct:.1f}%)")
        
        return self.y
    
    def map_to_13_features(self):
        """Map CICIDS 80+ features to Kaisen's 13-feature OS-layer"""
        print("\n" + "=" * 70)
        print("MAPPING TO KAISEN'S 13-FEATURE OS-LAYER")
        print("=" * 70)
        
        # Select columns that exist in CICIDS
        # Map to approximate Kaisen's 13 OS-layer features
        feature_mapping = {
            'network_connections': 'Total Fwd Packets',
            'connection_rate': 'Flow Packets/s',
            'cpu_usage': 'Flow Duration',
            'memory_usage': 'Total Fwd Packets',
            'unique_ips': 'Total Backward Packets',
            'process_count': 'Fwd Packet Length Mean',
            'failed_logins': 'SYN Flag Count',
            'lateral_movement': 'Total Length of Fwd Packets',
            'port_scan_score': 'Max Packet Length',
            'resource_exhaustion': 'Flow Bytes/s',
            'entropy_spike': 'Fwd Packet Length Std',
            'anomaly_score': 'Min Packet Length',
            'previous_anomaly_score': 'Bwd Packet Length Std',
        }
        
        print("\nFeature mapping:")
        X_mapped = []
        
        for kaisen_feat, cicids_feat in feature_mapping.items():
            # Find actual column (case insensitive)
            found_col = None
            for col in self.data.columns:
                if cicids_feat.lower().replace(' ', '') == col.lower().replace(' ', ''):
                    found_col = col
                    break
            
            if found_col:
                X_mapped.append(self.data[found_col].fillna(0).values)
                print(f"  [{len(X_mapped):2d}] {kaisen_feat:25s} <- {found_col}")
            else:
                # Fallback: use first numeric column
                numeric_cols = self.data.select_dtypes(include=[np.number]).columns.tolist()
                if numeric_cols and len(X_mapped) < 13:
                    col = numeric_cols[len(X_mapped)]
                    X_mapped.append(self.data[col].fillna(0).values)
                    print(f"  [{len(X_mapped):2d}] {kaisen_feat:25s} <- {col} [fallback]")
                else:
                    X_mapped.append(np.zeros(len(self.data)))
                    print(f"  [{len(X_mapped):2d}] {kaisen_feat:25s} <- [zeros]")
        
        # Combine into 13-feature matrix
        self.X = np.column_stack(X_mapped[:13])  # Ensure exactly 13 features
        
        print(f"\nFinal feature matrix: {self.X.shape}")
        print(f"  Samples: {self.X.shape[0]:,}")
        print(f"  Features: {self.X.shape[1]}")
        
        return self.X
    
    def normalize_features(self):
        """Normalize features to [0, 1] range"""
        print("\n" + "=" * 70)
        print("NORMALIZING FEATURES")
        print("=" * 70)
        
        # Clip to safe range
        self.X = np.clip(self.X, 0, 1000000)
        
        # Normalize to [0, 1]
        X_min = self.X.min(axis=0)
        X_max = self.X.max(axis=0)
        self.X = (self.X - X_min) / (X_max - X_min + 1e-8)
        
        print(f"Normalized to [0, 1] range")
        print(f"  Min: {self.X.min():.4f}")
        print(f"  Max: {self.X.max():.4f}")
        print(f"  Mean: {self.X.mean():.4f}")
        print(f"  Std: {self.X.std():.4f}")
        
        return self.X
    
    def train_test_split_data(self, test_size=0.2, random_state=42):
        """Split into train and test sets"""
        print("\n" + "=" * 70)
        print("TRAIN/TEST SPLIT")
        print("=" * 70)
        
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.X, self.y, test_size=test_size, random_state=random_state,
            stratify=self.y
        )
        
        print(f"\nTraining set:")
        print(f"  Samples: {len(self.X_train):,}")
        print(f"  Normal: {(1-self.y_train).sum():,} ({(1-self.y_train).sum()/len(self.y_train)*100:.1f}%)")
        print(f"  Attack: {self.y_train.sum():,} ({self.y_train.sum()/len(self.y_train)*100:.1f}%)")
        
        print(f"\nTest set:")
        print(f"  Samples: {len(self.X_test):,}")
        print(f"  Normal: {(1-self.y_test).sum():,} ({(1-self.y_test).sum()/len(self.y_test)*100:.1f}%)")
        print(f"  Attack: {self.y_test.sum():,} ({self.y_test.sum()/len(self.y_test)*100:.1f}%)")
        
        return self.X_train, self.X_test, self.y_train, self.y_test
    
    def get_data(self):
        """Get train/test data ready for model evaluation"""
        return self.X_train, self.X_test, self.y_train, self.y_test
    
    def load_and_preprocess(self):
        """Complete pipeline: load -> map -> normalize -> split"""
        self.load_all_days()
        self.extract_labels()
        self.map_to_13_features()
        self.normalize_features()
        self.train_test_split_data()
        
        print("\n" + "=" * 70)
        print("CICIDS2017 DATASET READY FOR EVALUATION")
        print("=" * 70)
        
        return self.get_data()


if __name__ == "__main__":
    loader = CICIDS2017Loader()
    
    try:
        X_train, X_test, y_train, y_test = loader.load_and_preprocess()
        
        print(f"\nOK Successfully loaded CICIDS2017 dataset")
        print(f"  Training: {X_train.shape}")
        print(f"  Testing: {X_test.shape}")
        
    except Exception as e:
        print(f"\nERROR loading dataset: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
