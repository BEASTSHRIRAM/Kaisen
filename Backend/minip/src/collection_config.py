"""
Configuration for the Kaisen Log Collection Backend.

This module extends the existing config.py to provide configuration
for log collection, anomaly detection, and attack graph modeling.
"""

import os
import json
import logging
from dataclasses import dataclass, field
from typing import List, Dict, Any
from pathlib import Path

from src.config import PROJECT_ROOT


@dataclass
class CollectionConfig:
    """Configuration for log collection system"""
    
    # Collection settings
    collection_interval_seconds: int = 7
    collection_window_min: int = 5
    collection_window_max: int = 10
    
    # Model settings
    model_path: str = field(default_factory=lambda: str(PROJECT_ROOT / "models" / "best_model.h5"))
    anomaly_threshold: float = 0.7
    
    # Storage settings
    log_dir: str = "logs"
    history_file: str = "history.json"
    alerts_file: str = "alerts.json"
    
    # Remote collection
    remote_endpoints: List[Dict[str, Any]] = field(default_factory=list)
    
    # Terminal execution
    command_timeout: int = 30
    command_whitelist: List[str] = field(default_factory=lambda: [
        'wmic', 'tasklist', 'netstat', 'wevtutil',  # Windows
        'top', 'ps', 'free', 'journalctl', 'ss'     # Linux
    ])
    
    # Logging
    log_level: str = "INFO"
    application_log_file: str = "application.log"
    
    @classmethod
    def from_file(cls, config_path: str) -> 'CollectionConfig':
        """
        Load configuration from JSON file with default fallback.
        
        Args:
            config_path: Path to configuration JSON file
            
        Returns:
            CollectionConfig instance with loaded or default values
        """
        if not os.path.exists(config_path):
            logging.warning(f"Config file not found: {config_path}, using defaults")
            return cls()
        
        try:
            with open(config_path, 'r') as f:
                data = json.load(f)
            
            # Create config with loaded data, using defaults for missing fields
            config = cls()
            
            # Update fields from loaded data
            if 'collection_interval_seconds' in data:
                config.collection_interval_seconds = data['collection_interval_seconds']
            if 'collection_window_min' in data:
                config.collection_window_min = data['collection_window_min']
            if 'collection_window_max' in data:
                config.collection_window_max = data['collection_window_max']
            if 'model_path' in data:
                config.model_path = data['model_path']
            if 'anomaly_threshold' in data:
                config.anomaly_threshold = data['anomaly_threshold']
            if 'log_dir' in data:
                config.log_dir = data['log_dir']
            if 'history_file' in data:
                config.history_file = data['history_file']
            if 'alerts_file' in data:
                config.alerts_file = data['alerts_file']
            if 'remote_endpoints' in data:
                config.remote_endpoints = data['remote_endpoints']
            if 'command_timeout' in data:
                config.command_timeout = data['command_timeout']
            if 'command_whitelist' in data:
                config.command_whitelist = data['command_whitelist']
            if 'log_level' in data:
                config.log_level = data['log_level']
            if 'application_log_file' in data:
                config.application_log_file = data['application_log_file']
            
            logging.info(f"Loaded configuration from: {config_path}")
            return config
            
        except json.JSONDecodeError as e:
            logging.warning(f"Invalid JSON in config file {config_path}: {e}, using defaults")
            return cls()
        except Exception as e:
            logging.warning(f"Error loading config file {config_path}: {e}, using defaults")
            return cls()
    
    def setup_logging(self) -> None:
        """
        Configure logging for the application.
        Sets up both file and console logging with the configured log level.
        """
        # Ensure log directory exists
        log_dir_path = Path(self.log_dir)
        log_dir_path.mkdir(parents=True, exist_ok=True)
        
        # Get log level
        log_level = getattr(logging, self.log_level.upper(), logging.INFO)
        
        # Configure logging
        log_file_path = log_dir_path / self.application_log_file
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file_path),
                logging.StreamHandler()
            ]
        )
        
        logging.info(f"Logging configured: level={self.log_level}, file={log_file_path}")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary for serialization.
        
        Returns:
            Dictionary representation of configuration
        """
        return {
            'collection_interval_seconds': self.collection_interval_seconds,
            'collection_window_min': self.collection_window_min,
            'collection_window_max': self.collection_window_max,
            'model_path': self.model_path,
            'anomaly_threshold': self.anomaly_threshold,
            'log_dir': self.log_dir,
            'history_file': self.history_file,
            'alerts_file': self.alerts_file,
            'remote_endpoints': self.remote_endpoints,
            'command_timeout': self.command_timeout,
            'command_whitelist': self.command_whitelist,
            'log_level': self.log_level,
            'application_log_file': self.application_log_file
        }


if __name__ == "__main__":
    # Test configuration loading
    config = CollectionConfig.from_file("config.json")
    print("=== Log Collection Configuration ===")
    print(f"Collection interval: {config.collection_interval_seconds}s")
    print(f"Model path: {config.model_path}")
    print(f"Anomaly threshold: {config.anomaly_threshold}")
    print(f"Log directory: {config.log_dir}")
    print(f"Command timeout: {config.command_timeout}s")
    print(f"Log level: {config.log_level}")
