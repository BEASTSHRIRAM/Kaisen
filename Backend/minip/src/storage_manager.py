"""
Storage Manager for the Kaisen Log Collection Backend.

This module handles persistence of logs and alerts to local JSON files
with retry logic, file creation, and JSON validation.

Validates: Requirements 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 14.11
"""

import os
import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, List
from dataclasses import asdict

from src.data_models import FeatureVector, Alert
from src.error_handler import handle_warning, handle_recoverable_error, log_error, ErrorCategory


class StorageManager:
    """
    Manages persistence of logs and alerts to local JSON files.
    
    This class provides methods to save log entries and alerts with:
    - Automatic file creation if files don't exist
    - Retry logic with exponential backoff for failed writes
    - JSON validation after each write operation
    - Append-only writes to preserve existing data
    
    Attributes:
        log_dir: Directory path for storing log files
        history_file: Filename for log history
        alerts_file: Filename for alerts
    """
    
    def __init__(self, log_dir: str = "logs", history_file: str = "history.json", 
                 alerts_file: str = "alerts.json"):
        """
        Initialize StorageManager with file paths.
        
        Args:
            log_dir: Directory for log files (default: "logs")
            history_file: Filename for log history (default: "history.json")
            alerts_file: Filename for alerts (default: "alerts.json")
        
        Requirements:
            - 10.2: Continue operation after non-critical errors
        """
        self.log_dir = Path(log_dir)
        self.history_file = history_file
        self.alerts_file = alerts_file
        
        # Ensure log directory exists
        try:
            self.log_dir.mkdir(parents=True, exist_ok=True)
            logging.info(f"StorageManager initialized: log_dir={self.log_dir}")
        except Exception as e:
            # RECOVERABLE ERROR: Failed to create log directory
            handle_recoverable_error(
                "StorageManager",
                f"Failed to create log directory {self.log_dir}: {str(e)}",
                e
            )
            # Try to continue anyway
    
    def save_log(self, feature_vector: FeatureVector, max_retries: int = 3) -> bool:
        """
        Save a log entry to history.json with retry logic.
        
        This method appends the feature vector to the history file without
        overwriting existing entries. If the file doesn't exist, it creates it.
        Failed writes are retried up to max_retries times with exponential backoff.
        
        Args:
            feature_vector: The FeatureVector to save
            max_retries: Maximum number of retry attempts (default: 3)
            
        Returns:
            True if save succeeded, False if all retries failed
            
        Validates: Requirements 8.1, 8.3, 8.4, 8.5, 8.6, 8.7
        """
        filepath = self.log_dir / self.history_file
        
        try:
            log_entry = feature_vector.to_dict()
        except Exception as e:
            handle_recoverable_error(
                "StorageManager",
                f"Failed to convert feature vector to dict: {str(e)}",
                e
            )
            return False
        
        for attempt in range(max_retries):
            try:
                # Read existing data or initialize empty list
                if filepath.exists():
                    try:
                        with open(filepath, 'r') as f:
                            data = json.load(f)
                        if not isinstance(data, list):
                            handle_warning(
                                "StorageManager",
                                f"Invalid data format in {filepath}, expected list. Reinitializing."
                            )
                            data = []
                    except json.JSONDecodeError as e:
                        handle_warning(
                            "StorageManager",
                            f"Corrupted JSON in {filepath}: {str(e)}. Reinitializing."
                        )
                        data = []
                else:
                    data = []
                
                # Append new entry
                data.append(log_entry)
                
                # Write back to file
                try:
                    self._write_to_file(data, filepath)
                except Exception as e:
                    raise IOError(f"Failed to write to file: {str(e)}")
                
                # Validate JSON integrity
                if not self.ensure_valid_json(filepath):
                    raise ValueError(f"JSON validation failed for {filepath}")
                
                logging.debug(f"Log entry saved to {filepath}")
                return True
                
            except Exception as e:
                if attempt == max_retries - 1:
                    # RECOVERABLE ERROR: All retries failed
                    handle_recoverable_error(
                        "StorageManager",
                        f"Failed to save log after {max_retries} attempts: {str(e)}",
                        e
                    )
                    return False
                
                # Exponential backoff: 0.1s, 0.2s, 0.4s
                backoff_time = 0.1 * (2 ** attempt)
                handle_warning(
                    "StorageManager",
                    f"Save log attempt {attempt + 1} failed: {str(e)}, retrying in {backoff_time}s"
                )
                time.sleep(backoff_time)
        
        return False
    
    def save_alert(self, alert: Alert, max_retries: int = 3) -> bool:
        """
        Save an alert to alerts.json with retry logic.
        
        This method appends the alert to the alerts file without overwriting
        existing entries. If the file doesn't exist, it creates it.
        Failed writes are retried up to max_retries times with exponential backoff.
        
        Args:
            alert: The Alert to save
            max_retries: Maximum number of retry attempts (default: 3)
            
        Returns:
            True if save succeeded, False if all retries failed
            
        Validates: Requirements 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 14.11
        """
        filepath = self.log_dir / self.alerts_file
        
        # Convert alert to dictionary, handling nested FeatureVector
        alert_dict = {
            'alert_id': alert.alert_id,
            'node_id': alert.node_id,
            'timestamp': alert.timestamp,
            'anomaly_score': alert.anomaly_score,
            'suspected_reason': alert.suspected_reason,
            'severity': alert.severity,
            'suspicious_ips': alert.suspicious_ips,
            'feature_vector': alert.feature_vector.to_dict()
        }
        
        for attempt in range(max_retries):
            try:
                # Read existing data or initialize empty list
                if filepath.exists():
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                    if not isinstance(data, list):
                        logging.error(f"Invalid data format in {filepath}, expected list")
                        data = []
                else:
                    data = []
                
                # Append new alert
                data.append(alert_dict)
                
                # Write back to file
                self._write_to_file(data, filepath)
                
                # Validate JSON integrity
                if not self.ensure_valid_json(filepath):
                    raise ValueError(f"JSON validation failed for {filepath}")
                
                logging.info(f"Alert saved to {filepath}: alert_id={alert.alert_id}, severity={alert.severity}")
                return True
                
            except Exception as e:
                if attempt == max_retries - 1:
                    logging.error(f"Failed to save alert after {max_retries} attempts: {e}")
                    return False
                
                # Exponential backoff: 0.1s, 0.2s, 0.4s
                backoff_time = 0.1 * (2 ** attempt)
                logging.warning(f"Save alert attempt {attempt + 1} failed: {e}, retrying in {backoff_time}s")
                time.sleep(backoff_time)
        
        return False
    
    def ensure_valid_json(self, filepath: Path) -> bool:
        """
        Validate that a file contains valid JSON.
        
        This method attempts to parse the file as JSON to ensure integrity.
        
        Args:
            filepath: Path to the JSON file to validate
            
        Returns:
            True if file contains valid JSON, False otherwise
            
        Validates: Requirement 8.7
        """
        try:
            with open(filepath, 'r') as f:
                json.load(f)
            return True
        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON in {filepath}: {e}")
            return False
        except Exception as e:
            logging.error(f"Error validating JSON in {filepath}: {e}")
            return False
    
    def _write_to_file(self, data: List[Dict[str, Any]], filepath: Path) -> None:
        """
        Write data to a JSON file with proper formatting.
        
        This is a helper method that handles the actual file write operation.
        It writes with indentation for readability.
        
        Args:
            data: List of dictionaries to write
            filepath: Path to the file
            
        Raises:
            IOError: If write operation fails
        """
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_log_history(self) -> List[Dict[str, Any]]:
        """
        Retrieve all log entries from history.json.
        
        Returns:
            List of log entries as dictionaries, empty list if file doesn't exist
        """
        filepath = self.log_dir / self.history_file
        
        if not filepath.exists():
            logging.warning(f"History file not found: {filepath}")
            return []
        
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            return data if isinstance(data, list) else []
        except Exception as e:
            logging.error(f"Error reading history file: {e}")
            return []
    
    def get_alerts(self) -> List[Dict[str, Any]]:
        """
        Retrieve all alerts from alerts.json.
        
        Returns:
            List of alerts as dictionaries, empty list if file doesn't exist
        """
        filepath = self.log_dir / self.alerts_file
        
        if not filepath.exists():
            logging.warning(f"Alerts file not found: {filepath}")
            return []
        
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            return data if isinstance(data, list) else []
        except Exception as e:
            logging.error(f"Error reading alerts file: {e}")
            return []


if __name__ == "__main__":
    # Test StorageManager
    logging.basicConfig(level=logging.INFO)
    
    from datetime import datetime
    
    # Create test feature vector
    test_fv = FeatureVector(
        cpu_usage=45.2,
        memory_usage=62.8,
        process_count=156,
        network_connections=42,
        failed_logins=0,
        timestamp=datetime.utcnow().isoformat() + 'Z',
        node_id="test_node"
    )
    
    # Create test alert
    test_alert = Alert(
        alert_id="test-alert-001",
        node_id="test_node",
        timestamp=datetime.utcnow().isoformat() + 'Z',
        anomaly_score=0.85,
        suspected_reason="high CPU usage",
        feature_vector=test_fv,
        severity="high",
        suspicious_ips=["192.168.1.100"]
    )
    
    # Test storage
    storage = StorageManager(log_dir="test_logs")
    
    print("Testing save_log...")
    success = storage.save_log(test_fv)
    print(f"Save log: {'SUCCESS' if success else 'FAILED'}")
    
    print("\nTesting save_alert...")
    success = storage.save_alert(test_alert)
    print(f"Save alert: {'SUCCESS' if success else 'FAILED'}")
    
    print("\nRetrieving logs...")
    logs = storage.get_log_history()
    print(f"Found {len(logs)} log entries")
    
    print("\nRetrieving alerts...")
    alerts = storage.get_alerts()
    print(f"Found {len(alerts)} alerts")
