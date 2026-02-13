"""
Unit tests for StorageManager.

Tests the storage manager's ability to save logs and alerts,
handle file creation, retry logic, and JSON validation.
"""

import os
import sys
import json
import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, mock_open, MagicMock

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from storage_manager import StorageManager
from data_models import FeatureVector, Alert


@pytest.fixture
def temp_log_dir():
    """Create a temporary directory for test logs."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def storage_manager(temp_log_dir):
    """Create a StorageManager instance with temporary directory."""
    return StorageManager(log_dir=temp_log_dir)


@pytest.fixture
def sample_feature_vector():
    """Create a sample FeatureVector for testing."""
    return FeatureVector(
        cpu_usage=45.2,
        memory_usage=62.8,
        process_count=156,
        network_connections=42,
        failed_logins=0,
        timestamp=datetime.utcnow().isoformat() + 'Z',
        node_id="test_node"
    )


@pytest.fixture
def sample_alert(sample_feature_vector):
    """Create a sample Alert for testing."""
    return Alert(
        alert_id="test-alert-001",
        node_id="test_node",
        timestamp=datetime.utcnow().isoformat() + 'Z',
        anomaly_score=0.85,
        suspected_reason="high CPU usage",
        feature_vector=sample_feature_vector,
        severity="high",
        suspicious_ips=["192.168.1.100"]
    )


class TestStorageManagerInitialization:
    """Test StorageManager initialization."""
    
    def test_init_creates_log_directory(self, temp_log_dir):
        """Test that initialization creates the log directory if it doesn't exist."""
        log_dir = Path(temp_log_dir) / "new_logs"
        assert not log_dir.exists()
        
        storage = StorageManager(log_dir=str(log_dir))
        
        assert log_dir.exists()
        assert storage.log_dir == log_dir
    
    def test_init_with_existing_directory(self, temp_log_dir):
        """Test initialization with an existing directory."""
        storage = StorageManager(log_dir=temp_log_dir)
        
        assert storage.log_dir == Path(temp_log_dir)
        assert storage.history_file == "history.json"
        assert storage.alerts_file == "alerts.json"
    
    def test_init_with_custom_filenames(self, temp_log_dir):
        """Test initialization with custom filenames."""
        storage = StorageManager(
            log_dir=temp_log_dir,
            history_file="custom_history.json",
            alerts_file="custom_alerts.json"
        )
        
        assert storage.history_file == "custom_history.json"
        assert storage.alerts_file == "custom_alerts.json"


class TestSaveLog:
    """Test save_log functionality."""
    
    def test_save_log_creates_file_if_not_exists(self, storage_manager, sample_feature_vector):
        """Test that save_log creates the history file if it doesn't exist."""
        history_path = storage_manager.log_dir / storage_manager.history_file
        assert not history_path.exists()
        
        result = storage_manager.save_log(sample_feature_vector)
        
        assert result is True
        assert history_path.exists()
    
    def test_save_log_appends_to_existing_file(self, storage_manager, sample_feature_vector):
        """Test that save_log appends without overwriting existing entries."""
        # Save first entry
        storage_manager.save_log(sample_feature_vector)
        
        # Create second entry with different values
        second_fv = FeatureVector(
            cpu_usage=80.0,
            memory_usage=90.0,
            process_count=200,
            network_connections=100,
            failed_logins=5,
            timestamp=datetime.utcnow().isoformat() + 'Z',
            node_id="test_node_2"
        )
        
        result = storage_manager.save_log(second_fv)
        
        assert result is True
        
        # Verify both entries exist
        logs = storage_manager.get_log_history()
        assert len(logs) == 2
        assert logs[0]['cpu_usage'] == 45.2
        assert logs[1]['cpu_usage'] == 80.0
    
    def test_save_log_valid_json_format(self, storage_manager, sample_feature_vector):
        """Test that saved log is valid JSON."""
        storage_manager.save_log(sample_feature_vector)
        
        history_path = storage_manager.log_dir / storage_manager.history_file
        
        # Should be able to parse as JSON
        with open(history_path, 'r') as f:
            data = json.load(f)
        
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]['cpu_usage'] == 45.2
    
    def test_save_log_includes_all_fields(self, storage_manager, sample_feature_vector):
        """Test that all FeatureVector fields are saved."""
        storage_manager.save_log(sample_feature_vector)
        
        logs = storage_manager.get_log_history()
        log_entry = logs[0]
        
        assert 'cpu_usage' in log_entry
        assert 'memory_usage' in log_entry
        assert 'process_count' in log_entry
        assert 'network_connections' in log_entry
        assert 'failed_logins' in log_entry
        assert 'timestamp' in log_entry
        assert 'node_id' in log_entry
    
    def test_save_log_retry_on_failure(self, storage_manager, sample_feature_vector):
        """Test that save_log retries on failure."""
        # Mock _write_to_file to fail twice then succeed
        call_count = 0
        original_write = storage_manager._write_to_file
        
        def mock_write(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise IOError("Simulated write failure")
            return original_write(*args, **kwargs)
        
        with patch.object(storage_manager, '_write_to_file', side_effect=mock_write):
            result = storage_manager.save_log(sample_feature_vector)
        
        assert result is True
        assert call_count == 3
    
    def test_save_log_fails_after_max_retries(self, storage_manager, sample_feature_vector):
        """Test that save_log returns False after max retries."""
        # Mock _write_to_file to always fail
        with patch.object(storage_manager, '_write_to_file', side_effect=IOError("Persistent failure")):
            result = storage_manager.save_log(sample_feature_vector, max_retries=3)
        
        assert result is False


class TestSaveAlert:
    """Test save_alert functionality."""
    
    def test_save_alert_creates_file_if_not_exists(self, storage_manager, sample_alert):
        """Test that save_alert creates the alerts file if it doesn't exist."""
        alerts_path = storage_manager.log_dir / storage_manager.alerts_file
        assert not alerts_path.exists()
        
        result = storage_manager.save_alert(sample_alert)
        
        assert result is True
        assert alerts_path.exists()
    
    def test_save_alert_appends_to_existing_file(self, storage_manager, sample_alert, sample_feature_vector):
        """Test that save_alert appends without overwriting existing entries."""
        # Save first alert
        storage_manager.save_alert(sample_alert)
        
        # Create second alert
        second_alert = Alert(
            alert_id="test-alert-002",
            node_id="test_node_2",
            timestamp=datetime.utcnow().isoformat() + 'Z',
            anomaly_score=0.92,
            suspected_reason="multiple failed logins",
            feature_vector=sample_feature_vector,
            severity="critical",
            suspicious_ips=["10.0.0.5"]
        )
        
        result = storage_manager.save_alert(second_alert)
        
        assert result is True
        
        # Verify both alerts exist
        alerts = storage_manager.get_alerts()
        assert len(alerts) == 2
        assert alerts[0]['alert_id'] == "test-alert-001"
        assert alerts[1]['alert_id'] == "test-alert-002"
    
    def test_save_alert_valid_json_format(self, storage_manager, sample_alert):
        """Test that saved alert is valid JSON."""
        storage_manager.save_alert(sample_alert)
        
        alerts_path = storage_manager.log_dir / storage_manager.alerts_file
        
        # Should be able to parse as JSON
        with open(alerts_path, 'r') as f:
            data = json.load(f)
        
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]['alert_id'] == "test-alert-001"
    
    def test_save_alert_includes_all_fields(self, storage_manager, sample_alert):
        """Test that all Alert fields are saved."""
        storage_manager.save_alert(sample_alert)
        
        alerts = storage_manager.get_alerts()
        alert_entry = alerts[0]
        
        assert 'alert_id' in alert_entry
        assert 'node_id' in alert_entry
        assert 'timestamp' in alert_entry
        assert 'anomaly_score' in alert_entry
        assert 'suspected_reason' in alert_entry
        assert 'severity' in alert_entry
        assert 'suspicious_ips' in alert_entry
        assert 'feature_vector' in alert_entry
    
    def test_save_alert_includes_suspicious_ips(self, storage_manager, sample_alert):
        """Test that suspicious_ips are saved correctly (Requirement 14.11)."""
        storage_manager.save_alert(sample_alert)
        
        alerts = storage_manager.get_alerts()
        alert_entry = alerts[0]
        
        assert 'suspicious_ips' in alert_entry
        assert alert_entry['suspicious_ips'] == ["192.168.1.100"]
    
    def test_save_alert_retry_on_failure(self, storage_manager, sample_alert):
        """Test that save_alert retries on failure."""
        # Mock _write_to_file to fail once then succeed
        call_count = 0
        original_write = storage_manager._write_to_file
        
        def mock_write(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise IOError("Simulated write failure")
            return original_write(*args, **kwargs)
        
        with patch.object(storage_manager, '_write_to_file', side_effect=mock_write):
            result = storage_manager.save_alert(sample_alert)
        
        assert result is True
        assert call_count == 2
    
    def test_save_alert_fails_after_max_retries(self, storage_manager, sample_alert):
        """Test that save_alert returns False after max retries."""
        # Mock _write_to_file to always fail
        with patch.object(storage_manager, '_write_to_file', side_effect=IOError("Persistent failure")):
            result = storage_manager.save_alert(sample_alert, max_retries=3)
        
        assert result is False


class TestEnsureValidJson:
    """Test ensure_valid_json functionality."""
    
    def test_ensure_valid_json_with_valid_file(self, storage_manager, sample_feature_vector):
        """Test validation of a valid JSON file."""
        storage_manager.save_log(sample_feature_vector)
        history_path = storage_manager.log_dir / storage_manager.history_file
        
        result = storage_manager.ensure_valid_json(history_path)
        
        assert result is True
    
    def test_ensure_valid_json_with_invalid_file(self, storage_manager):
        """Test validation of an invalid JSON file."""
        invalid_path = storage_manager.log_dir / "invalid.json"
        
        # Write invalid JSON
        with open(invalid_path, 'w') as f:
            f.write("{invalid json content")
        
        result = storage_manager.ensure_valid_json(invalid_path)
        
        assert result is False
    
    def test_ensure_valid_json_with_empty_file(self, storage_manager):
        """Test validation of an empty file."""
        empty_path = storage_manager.log_dir / "empty.json"
        
        # Create empty file
        empty_path.touch()
        
        result = storage_manager.ensure_valid_json(empty_path)
        
        assert result is False


class TestGetLogHistory:
    """Test get_log_history functionality."""
    
    def test_get_log_history_with_existing_logs(self, storage_manager, sample_feature_vector):
        """Test retrieving log history when logs exist."""
        storage_manager.save_log(sample_feature_vector)
        
        logs = storage_manager.get_log_history()
        
        assert isinstance(logs, list)
        assert len(logs) == 1
        assert logs[0]['node_id'] == "test_node"
    
    def test_get_log_history_with_no_file(self, storage_manager):
        """Test retrieving log history when file doesn't exist."""
        logs = storage_manager.get_log_history()
        
        assert isinstance(logs, list)
        assert len(logs) == 0
    
    def test_get_log_history_with_invalid_json(self, storage_manager):
        """Test retrieving log history with corrupted file."""
        history_path = storage_manager.log_dir / storage_manager.history_file
        
        # Write invalid JSON
        with open(history_path, 'w') as f:
            f.write("{invalid")
        
        logs = storage_manager.get_log_history()
        
        assert isinstance(logs, list)
        assert len(logs) == 0


class TestGetAlerts:
    """Test get_alerts functionality."""
    
    def test_get_alerts_with_existing_alerts(self, storage_manager, sample_alert):
        """Test retrieving alerts when alerts exist."""
        storage_manager.save_alert(sample_alert)
        
        alerts = storage_manager.get_alerts()
        
        assert isinstance(alerts, list)
        assert len(alerts) == 1
        assert alerts[0]['alert_id'] == "test-alert-001"
    
    def test_get_alerts_with_no_file(self, storage_manager):
        """Test retrieving alerts when file doesn't exist."""
        alerts = storage_manager.get_alerts()
        
        assert isinstance(alerts, list)
        assert len(alerts) == 0
    
    def test_get_alerts_with_invalid_json(self, storage_manager):
        """Test retrieving alerts with corrupted file."""
        alerts_path = storage_manager.log_dir / storage_manager.alerts_file
        
        # Write invalid JSON
        with open(alerts_path, 'w') as f:
            f.write("[invalid")
        
        alerts = storage_manager.get_alerts()
        
        assert isinstance(alerts, list)
        assert len(alerts) == 0


class TestExponentialBackoff:
    """Test exponential backoff behavior."""
    
    def test_exponential_backoff_timing(self, storage_manager, sample_feature_vector):
        """Test that retry delays follow exponential backoff pattern."""
        import time
        
        call_times = []
        
        def mock_write(*args, **kwargs):
            call_times.append(time.time())
            raise IOError("Simulated failure")
        
        with patch.object(storage_manager, '_write_to_file', side_effect=mock_write):
            storage_manager.save_log(sample_feature_vector, max_retries=3)
        
        # Verify we had 3 attempts
        assert len(call_times) == 3
        
        # Verify delays are approximately exponential (0.1s, 0.2s)
        # Allow some tolerance for execution time
        if len(call_times) >= 2:
            delay1 = call_times[1] - call_times[0]
            assert 0.08 <= delay1 <= 0.15  # ~0.1s with tolerance
        
        if len(call_times) >= 3:
            delay2 = call_times[2] - call_times[1]
            assert 0.18 <= delay2 <= 0.25  # ~0.2s with tolerance


class TestFilePathCorrectness:
    """Test that files are written to correct paths (Requirement 8.1, 8.2)."""
    
    def test_logs_written_to_history_file(self, storage_manager, sample_feature_vector):
        """Test that logs are written to the configured history file."""
        storage_manager.save_log(sample_feature_vector)
        
        expected_path = storage_manager.log_dir / storage_manager.history_file
        assert expected_path.exists()
        
        # Verify it's the history file, not alerts file
        alerts_path = storage_manager.log_dir / storage_manager.alerts_file
        assert not alerts_path.exists()
    
    def test_alerts_written_to_alerts_file(self, storage_manager, sample_alert):
        """Test that alerts are written to the configured alerts file."""
        storage_manager.save_alert(sample_alert)
        
        expected_path = storage_manager.log_dir / storage_manager.alerts_file
        assert expected_path.exists()
        
        # Verify it's the alerts file, not history file
        history_path = storage_manager.log_dir / storage_manager.history_file
        assert not history_path.exists()
