"""
Property-based tests for StorageManager.

These tests verify universal properties that should hold across all inputs
using Hypothesis for property-based testing.
"""

import os
import sys
import json
import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from hypothesis import given, settings, strategies as st, HealthCheck
from unittest.mock import patch

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from storage_manager import StorageManager
from data_models import FeatureVector, Alert


# Strategy for generating valid FeatureVectors
@st.composite
def feature_vector_strategy(draw):
    """Generate random valid FeatureVectors."""
    return FeatureVector(
        cpu_usage=draw(st.floats(min_value=0.0, max_value=100.0)),
        memory_usage=draw(st.floats(min_value=0.0, max_value=100.0)),
        process_count=draw(st.integers(min_value=0, max_value=1000)),
        network_connections=draw(st.integers(min_value=0, max_value=500)),
        failed_logins=draw(st.integers(min_value=0, max_value=100)),
        timestamp=datetime.utcnow().isoformat() + 'Z',
        node_id=draw(st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')))),
        unique_ip_count=draw(st.integers(min_value=0, max_value=100)),
        failed_attempts_per_ip=draw(st.dictionaries(
            keys=st.text(min_size=7, max_size=15, alphabet='0123456789.'),
            values=st.integers(min_value=0, max_value=50),
            max_size=10
        )),
        connection_count_per_ip=draw(st.dictionaries(
            keys=st.text(min_size=7, max_size=15, alphabet='0123456789.'),
            values=st.integers(min_value=0, max_value=100),
            max_size=10
        )),
        source_ips=draw(st.lists(
            st.text(min_size=7, max_size=15, alphabet='0123456789.'),
            max_size=20
        )),
        destination_ips=draw(st.lists(
            st.text(min_size=7, max_size=15, alphabet='0123456789.'),
            max_size=20
        ))
    )


# Strategy for generating valid Alerts
@st.composite
def alert_strategy(draw):
    """Generate random valid Alerts."""
    fv = draw(feature_vector_strategy())
    return Alert(
        alert_id=draw(st.text(min_size=1, max_size=100)),
        node_id=draw(st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')))),
        timestamp=datetime.utcnow().isoformat() + 'Z',
        anomaly_score=draw(st.floats(min_value=0.0, max_value=1.0)),
        suspected_reason=draw(st.text(min_size=1, max_size=200)),
        feature_vector=fv,
        severity=draw(st.sampled_from(['low', 'medium', 'high', 'critical'])),
        suspicious_ips=draw(st.lists(
            st.text(min_size=7, max_size=15, alphabet='0123456789.'),
            max_size=10
        ))
    )


class TestStorageAppendProperty:
    """
    Feature: log-collection-backend, Property 21: Storage Append Without Overwrite
    
    For any save operation to an existing file, the new entry should be appended
    and all existing entries should remain unchanged.
    
    **Validates: Requirement 8.6**
    """
    
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(fv1=feature_vector_strategy(), fv2=feature_vector_strategy())
    def test_save_log_always_appends(self, fv1, fv2):
        """Test that saving logs always appends without overwriting."""
        temp_dir = tempfile.mkdtemp()
        try:
            storage = StorageManager(log_dir=temp_dir)
            
            # Save first entry
            result1 = storage.save_log(fv1)
            assert result1 is True
            
            # Get count after first save
            logs_after_first = storage.get_log_history()
            count_after_first = len(logs_after_first)
            
            # Save second entry
            result2 = storage.save_log(fv2)
            assert result2 is True
            
            # Get count after second save
            logs_after_second = storage.get_log_history()
            count_after_second = len(logs_after_second)
            
            # Verify append behavior
            assert count_after_second == count_after_first + 1
            assert logs_after_first[0] == logs_after_second[0]  # First entry unchanged
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(alert1=alert_strategy(), alert2=alert_strategy())
    def test_save_alert_always_appends(self, alert1, alert2):
        """Test that saving alerts always appends without overwriting."""
        temp_dir = tempfile.mkdtemp()
        try:
            storage = StorageManager(log_dir=temp_dir)
            
            # Save first alert
            result1 = storage.save_alert(alert1)
            assert result1 is True
            
            # Get count after first save
            alerts_after_first = storage.get_alerts()
            count_after_first = len(alerts_after_first)
            
            # Save second alert
            result2 = storage.save_alert(alert2)
            assert result2 is True
            
            # Get count after second save
            alerts_after_second = storage.get_alerts()
            count_after_second = len(alerts_after_second)
            
            # Verify append behavior
            assert count_after_second == count_after_first + 1
            assert alerts_after_first[0]['alert_id'] == alerts_after_second[0]['alert_id']
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestStorageJsonValidityProperty:
    """
    Feature: log-collection-backend, Property 22: Storage JSON Validity
    
    For any write operation, the resulting file should be valid JSON
    that can be parsed without errors.
    
    **Validates: Requirement 8.7**
    """
    
    @settings(max_examples=50)
    @given(fv=feature_vector_strategy())
    def test_saved_log_is_valid_json(self, fv):
        """Test that saved logs always produce valid JSON."""
        temp_dir = tempfile.mkdtemp()
        try:
            storage = StorageManager(log_dir=temp_dir)
            
            result = storage.save_log(fv)
            assert result is True
            
            # Verify JSON validity
            filepath = storage.log_dir / storage.history_file
            assert storage.ensure_valid_json(filepath) is True
            
            # Verify we can parse it
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            assert isinstance(data, list)
            assert len(data) > 0
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    @settings(max_examples=50)
    @given(alert=alert_strategy())
    def test_saved_alert_is_valid_json(self, alert):
        """Test that saved alerts always produce valid JSON."""
        temp_dir = tempfile.mkdtemp()
        try:
            storage = StorageManager(log_dir=temp_dir)
            
            result = storage.save_alert(alert)
            assert result is True
            
            # Verify JSON validity
            filepath = storage.log_dir / storage.alerts_file
            assert storage.ensure_valid_json(filepath) is True
            
            # Verify we can parse it
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            assert isinstance(data, list)
            assert len(data) > 0
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestStorageRetryProperty:
    """
    Feature: log-collection-backend, Property 20: Storage Retry Logic
    
    For any failed write operation, the Storage_Manager should retry
    up to 3 times before giving up and logging an error.
    
    **Validates: Requirements 8.4, 8.5**
    """
    
    @settings(max_examples=20, deadline=500)
    @given(fv=feature_vector_strategy(), failures=st.integers(min_value=1, max_value=2))
    def test_save_log_retries_on_failure(self, fv, failures):
        """Test that save_log retries the correct number of times."""
        temp_dir = tempfile.mkdtemp()
        try:
            storage = StorageManager(log_dir=temp_dir)
            
            call_count = 0
            original_write = storage._write_to_file
            
            def mock_write(*args, **kwargs):
                nonlocal call_count
                call_count += 1
                if call_count <= failures:
                    raise IOError("Simulated failure")
                return original_write(*args, **kwargs)
            
            with patch.object(storage, '_write_to_file', side_effect=mock_write):
                result = storage.save_log(fv)
            
            # Should succeed after retries
            assert result is True
            assert call_count == failures + 1
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    @settings(max_examples=20, deadline=500)
    @given(alert=alert_strategy())
    def test_save_alert_fails_after_max_retries(self, alert):
        """Test that save_alert gives up after max retries."""
        temp_dir = tempfile.mkdtemp()
        try:
            storage = StorageManager(log_dir=temp_dir)
            
            call_count = 0
            
            def mock_write(*args, **kwargs):
                nonlocal call_count
                call_count += 1
                raise IOError("Persistent failure")
            
            with patch.object(storage, '_write_to_file', side_effect=mock_write):
                result = storage.save_alert(alert, max_retries=3)
            
            # Should fail after 3 attempts
            assert result is False
            assert call_count == 3
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestStorageFileCreationProperty:
    """
    Feature: log-collection-backend, Property 19: Storage File Creation
    
    For any save operation to a non-existent file, the Storage_Manager
    should create the file before writing.
    
    **Validates: Requirement 8.3**
    """
    
    @settings(max_examples=30)
    @given(fv=feature_vector_strategy())
    def test_save_log_creates_file_if_not_exists(self, fv):
        """Test that save_log creates file when it doesn't exist."""
        temp_dir = tempfile.mkdtemp()
        try:
            storage = StorageManager(log_dir=temp_dir)
            filepath = storage.log_dir / storage.history_file
            
            # Ensure file doesn't exist
            assert not filepath.exists()
            
            # Save log
            result = storage.save_log(fv)
            
            # File should now exist
            assert result is True
            assert filepath.exists()
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    @settings(max_examples=30)
    @given(alert=alert_strategy())
    def test_save_alert_creates_file_if_not_exists(self, alert):
        """Test that save_alert creates file when it doesn't exist."""
        temp_dir = tempfile.mkdtemp()
        try:
            storage = StorageManager(log_dir=temp_dir)
            filepath = storage.log_dir / storage.alerts_file
            
            # Ensure file doesn't exist
            assert not filepath.exists()
            
            # Save alert
            result = storage.save_alert(alert)
            
            # File should now exist
            assert result is True
            assert filepath.exists()
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestStorageFilePathProperty:
    """
    Feature: log-collection-backend, Property 18: Storage File Path Correctness
    
    For any save operation, logs should be written to the configured history file
    and alerts should be written to the configured alerts file.
    
    **Validates: Requirements 8.1, 8.2**
    """
    
    @settings(max_examples=30)
    @given(fv=feature_vector_strategy())
    def test_logs_always_written_to_history_file(self, fv):
        """Test that logs are always written to the correct file."""
        temp_dir = tempfile.mkdtemp()
        try:
            storage = StorageManager(log_dir=temp_dir)
            
            storage.save_log(fv)
            
            # History file should exist
            history_path = storage.log_dir / storage.history_file
            assert history_path.exists()
            
            # Alerts file should not exist
            alerts_path = storage.log_dir / storage.alerts_file
            assert not alerts_path.exists()
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    @settings(max_examples=30)
    @given(alert=alert_strategy())
    def test_alerts_always_written_to_alerts_file(self, alert):
        """Test that alerts are always written to the correct file."""
        temp_dir = tempfile.mkdtemp()
        try:
            storage = StorageManager(log_dir=temp_dir)
            
            storage.save_alert(alert)
            
            # Alerts file should exist
            alerts_path = storage.log_dir / storage.alerts_file
            assert alerts_path.exists()
            
            # History file should not exist
            history_path = storage.log_dir / storage.history_file
            assert not history_path.exists()
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestSuspiciousIpStorageProperty:
    """
    Feature: log-collection-backend, Property 50: Suspicious IP Storage
    
    For any alert saved to alerts.json, the suspicious_ips field should be
    persisted along with other alert data.
    
    **Validates: Requirement 14.11**
    """
    
    @settings(max_examples=30)
    @given(alert=alert_strategy())
    def test_suspicious_ips_always_persisted(self, alert):
        """Test that suspicious_ips are always saved with alerts."""
        temp_dir = tempfile.mkdtemp()
        try:
            storage = StorageManager(log_dir=temp_dir)
            
            # Save alert
            result = storage.save_alert(alert)
            assert result is True
            
            # Retrieve and verify
            alerts = storage.get_alerts()
            assert len(alerts) > 0
            
            saved_alert = alerts[-1]  # Get the last saved alert
            assert 'suspicious_ips' in saved_alert
            assert saved_alert['suspicious_ips'] == alert.suspicious_ips
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
