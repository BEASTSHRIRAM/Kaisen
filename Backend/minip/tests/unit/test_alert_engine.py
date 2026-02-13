"""
Unit tests for AlertEngine.

Tests cover:
- Initialization with valid/invalid thresholds
- Alert generation when threshold exceeded
- No alert when below threshold
- Suspected reason determination
- Suspicious IP identification
- Severity calculation
"""

import pytest
import sys
import os
from datetime import datetime

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from alert_engine import AlertEngine
from data_models import Alert, PredictionResult, FeatureVector


class TestAlertEngineInitialization:
    """Test AlertEngine initialization."""
    
    def test_init_with_default_threshold(self):
        """Test initialization with default threshold."""
        engine = AlertEngine()
        assert engine.threshold == 0.7
    
    def test_init_with_custom_threshold(self):
        """Test initialization with custom threshold."""
        engine = AlertEngine(threshold=0.85)
        assert engine.threshold == 0.85
    
    def test_init_with_invalid_threshold_too_high(self):
        """Test that threshold > 1 raises ValueError."""
        with pytest.raises(ValueError, match="Threshold must be between 0 and 1"):
            AlertEngine(threshold=1.5)
    
    def test_init_with_invalid_threshold_negative(self):
        """Test that negative threshold raises ValueError."""
        with pytest.raises(ValueError, match="Threshold must be between 0 and 1"):
            AlertEngine(threshold=-0.1)
    
    def test_init_with_boundary_thresholds(self):
        """Test initialization with boundary values 0 and 1."""
        engine_zero = AlertEngine(threshold=0.0)
        assert engine_zero.threshold == 0.0
        
        engine_one = AlertEngine(threshold=1.0)
        assert engine_one.threshold == 1.0


class TestProcessPrediction:
    """Test process_prediction method."""
    
    def test_alert_generated_when_threshold_exceeded(self):
        """Test that alert is generated when anomaly score exceeds threshold."""
        engine = AlertEngine(threshold=0.7)
        
        prediction = PredictionResult(
            anomaly_score=0.85,
            label='anomaly',
            confidence=0.9
        )
        
        feature_vector = FeatureVector(
            cpu_usage=92.5,
            memory_usage=78.3,
            process_count=203,
            network_connections=87,
            failed_logins=15,
            timestamp='2024-01-15T10:35:00Z',
            node_id='test_node'
        )
        
        alert = engine.process_prediction('test_node', prediction, feature_vector)
        
        assert alert is not None
        assert alert.node_id == 'test_node'
        assert alert.anomaly_score == 0.85
        assert alert.severity == 'high'
        assert len(alert.alert_id) > 0
        assert alert.timestamp is not None
    
    def test_no_alert_when_below_threshold(self):
        """Test that no alert is generated when score is below threshold."""
        engine = AlertEngine(threshold=0.7)
        
        prediction = PredictionResult(
            anomaly_score=0.65,
            label='normal',
            confidence=0.8
        )
        
        feature_vector = FeatureVector(
            cpu_usage=45.2,
            memory_usage=62.8,
            process_count=156,
            network_connections=42,
            failed_logins=0,
            timestamp='2024-01-15T10:30:00Z'
        )
        
        alert = engine.process_prediction('test_node', prediction, feature_vector)
        
        assert alert is None
    
    def test_no_alert_when_equal_to_threshold(self):
        """Test that no alert is generated when score equals threshold."""
        engine = AlertEngine(threshold=0.7)
        
        prediction = PredictionResult(
            anomaly_score=0.7,
            label='normal',
            confidence=0.8
        )
        
        feature_vector = FeatureVector(
            cpu_usage=50.0,
            memory_usage=60.0,
            process_count=150,
            network_connections=50,
            failed_logins=5,
            timestamp='2024-01-15T10:30:00Z'
        )
        
        alert = engine.process_prediction('test_node', prediction, feature_vector)
        
        assert alert is None
    
    def test_alert_contains_all_required_fields(self):
        """Test that generated alert contains all required fields."""
        engine = AlertEngine(threshold=0.7)
        
        prediction = PredictionResult(
            anomaly_score=0.85,
            label='anomaly',
            confidence=0.9
        )
        
        feature_vector = FeatureVector(
            cpu_usage=92.5,
            memory_usage=88.0,
            process_count=203,
            network_connections=87,
            failed_logins=15,
            timestamp='2024-01-15T10:35:00Z',
            node_id='test_node',
            unique_ip_count=65,
            failed_attempts_per_ip={'203.0.113.45': 12},
            connection_count_per_ip={'203.0.113.45': 55}
        )
        
        alert = engine.process_prediction('test_node', prediction, feature_vector)
        
        assert alert is not None
        assert alert.alert_id is not None
        assert len(alert.alert_id) > 0
        assert alert.node_id == 'test_node'
        assert alert.timestamp is not None
        assert alert.anomaly_score == 0.85
        assert alert.suspected_reason is not None
        assert alert.feature_vector == feature_vector
        assert alert.severity in ['low', 'medium', 'high', 'critical']
        assert isinstance(alert.suspicious_ips, list)


class TestDetermineSuspectedReason:
    """Test determine_suspected_reason method."""
    
    def test_high_cpu_usage(self):
        """Test suspected reason includes high CPU usage."""
        engine = AlertEngine()
        
        feature_vector = FeatureVector(
            cpu_usage=92.5,
            memory_usage=50.0,
            process_count=100,
            network_connections=50,
            failed_logins=0,
            timestamp='2024-01-15T10:35:00Z'
        )
        
        reason = engine.determine_suspected_reason(feature_vector)
        
        assert 'high CPU usage' in reason
    
    def test_high_memory_usage(self):
        """Test suspected reason includes high memory usage."""
        engine = AlertEngine()
        
        feature_vector = FeatureVector(
            cpu_usage=50.0,
            memory_usage=90.0,
            process_count=100,
            network_connections=50,
            failed_logins=0,
            timestamp='2024-01-15T10:35:00Z'
        )
        
        reason = engine.determine_suspected_reason(feature_vector)
        
        assert 'high memory usage' in reason
    
    def test_multiple_failed_logins(self):
        """Test suspected reason includes multiple failed logins."""
        engine = AlertEngine()
        
        feature_vector = FeatureVector(
            cpu_usage=50.0,
            memory_usage=50.0,
            process_count=100,
            network_connections=50,
            failed_logins=15,
            timestamp='2024-01-15T10:35:00Z'
        )
        
        reason = engine.determine_suspected_reason(feature_vector)
        
        assert 'multiple failed logins' in reason
    
    def test_excessive_network_connections(self):
        """Test suspected reason includes excessive network connections."""
        engine = AlertEngine()
        
        feature_vector = FeatureVector(
            cpu_usage=50.0,
            memory_usage=50.0,
            process_count=100,
            network_connections=150,
            failed_logins=0,
            timestamp='2024-01-15T10:35:00Z'
        )
        
        reason = engine.determine_suspected_reason(feature_vector)
        
        assert 'excessive network connections' in reason
    
    def test_high_process_count(self):
        """Test suspected reason includes high process count."""
        engine = AlertEngine()
        
        feature_vector = FeatureVector(
            cpu_usage=50.0,
            memory_usage=50.0,
            process_count=250,
            network_connections=50,
            failed_logins=0,
            timestamp='2024-01-15T10:35:00Z'
        )
        
        reason = engine.determine_suspected_reason(feature_vector)
        
        assert 'high process count' in reason
    
    def test_many_unique_ips(self):
        """Test suspected reason includes connections to many unique IPs."""
        engine = AlertEngine()
        
        feature_vector = FeatureVector(
            cpu_usage=50.0,
            memory_usage=50.0,
            process_count=100,
            network_connections=50,
            failed_logins=0,
            timestamp='2024-01-15T10:35:00Z',
            unique_ip_count=65
        )
        
        reason = engine.determine_suspected_reason(feature_vector)
        
        assert 'connections to many unique IPs' in reason
    
    def test_multiple_reasons_combined(self):
        """Test that multiple reasons are combined with commas."""
        engine = AlertEngine()
        
        feature_vector = FeatureVector(
            cpu_usage=92.5,
            memory_usage=88.0,
            process_count=203,
            network_connections=150,
            failed_logins=15,
            timestamp='2024-01-15T10:35:00Z',
            unique_ip_count=65
        )
        
        reason = engine.determine_suspected_reason(feature_vector)
        
        assert 'high CPU usage' in reason
        assert 'high memory usage' in reason
        assert 'multiple failed logins' in reason
        assert 'excessive network connections' in reason
        assert 'high process count' in reason
        assert 'connections to many unique IPs' in reason
        assert ',' in reason
    
    def test_no_abnormal_metrics(self):
        """Test default message when no metrics are abnormal."""
        engine = AlertEngine()
        
        feature_vector = FeatureVector(
            cpu_usage=50.0,
            memory_usage=50.0,
            process_count=100,
            network_connections=50,
            failed_logins=0,
            timestamp='2024-01-15T10:35:00Z'
        )
        
        reason = engine.determine_suspected_reason(feature_vector)
        
        assert reason == 'anomalous pattern detected'


class TestIdentifySuspiciousIps:
    """Test identify_suspicious_ips method."""
    
    def test_ip_with_high_failed_attempts(self):
        """Test that IPs with >5 failed attempts are marked suspicious."""
        engine = AlertEngine()
        
        feature_vector = FeatureVector(
            cpu_usage=50.0,
            memory_usage=50.0,
            process_count=100,
            network_connections=50,
            failed_logins=15,
            timestamp='2024-01-15T10:35:00Z',
            failed_attempts_per_ip={'203.0.113.45': 12, '198.51.100.23': 3}
        )
        
        suspicious = engine.identify_suspicious_ips(feature_vector)
        
        assert '203.0.113.45' in suspicious
        assert '198.51.100.23' not in suspicious
    
    def test_ip_with_excessive_connections(self):
        """Test that IPs with >50 connections are marked suspicious."""
        engine = AlertEngine()
        
        feature_vector = FeatureVector(
            cpu_usage=50.0,
            memory_usage=50.0,
            process_count=100,
            network_connections=50,
            failed_logins=0,
            timestamp='2024-01-15T10:35:00Z',
            connection_count_per_ip={'203.0.113.45': 75, '198.51.100.23': 30}
        )
        
        suspicious = engine.identify_suspicious_ips(feature_vector)
        
        assert '203.0.113.45' in suspicious
        assert '198.51.100.23' not in suspicious
    
    def test_ip_with_both_criteria(self):
        """Test IP marked suspicious for both failed attempts and connections."""
        engine = AlertEngine()
        
        feature_vector = FeatureVector(
            cpu_usage=50.0,
            memory_usage=50.0,
            process_count=100,
            network_connections=50,
            failed_logins=15,
            timestamp='2024-01-15T10:35:00Z',
            failed_attempts_per_ip={'203.0.113.45': 12},
            connection_count_per_ip={'203.0.113.45': 75}
        )
        
        suspicious = engine.identify_suspicious_ips(feature_vector)
        
        # Should only appear once even though it meets both criteria
        assert suspicious.count('203.0.113.45') == 1
    
    def test_no_suspicious_ips(self):
        """Test empty list when no IPs are suspicious."""
        engine = AlertEngine()
        
        feature_vector = FeatureVector(
            cpu_usage=50.0,
            memory_usage=50.0,
            process_count=100,
            network_connections=50,
            failed_logins=0,
            timestamp='2024-01-15T10:35:00Z',
            failed_attempts_per_ip={'203.0.113.45': 2},
            connection_count_per_ip={'203.0.113.45': 30}
        )
        
        suspicious = engine.identify_suspicious_ips(feature_vector)
        
        assert len(suspicious) == 0
    
    def test_empty_ip_dictionaries(self):
        """Test handling of empty IP dictionaries."""
        engine = AlertEngine()
        
        feature_vector = FeatureVector(
            cpu_usage=50.0,
            memory_usage=50.0,
            process_count=100,
            network_connections=50,
            failed_logins=0,
            timestamp='2024-01-15T10:35:00Z'
        )
        
        suspicious = engine.identify_suspicious_ips(feature_vector)
        
        assert len(suspicious) == 0


class TestCalculateSeverity:
    """Test _calculate_severity method."""
    
    def test_critical_severity(self):
        """Test critical severity for score >= 0.9."""
        engine = AlertEngine()
        
        assert engine._calculate_severity(0.95) == 'critical'
        assert engine._calculate_severity(0.9) == 'critical'
    
    def test_high_severity(self):
        """Test high severity for score >= 0.8."""
        engine = AlertEngine()
        
        assert engine._calculate_severity(0.85) == 'high'
        assert engine._calculate_severity(0.8) == 'high'
    
    def test_medium_severity(self):
        """Test medium severity for score >= 0.7."""
        engine = AlertEngine()
        
        assert engine._calculate_severity(0.75) == 'medium'
        assert engine._calculate_severity(0.7) == 'medium'
    
    def test_low_severity(self):
        """Test low severity for score < 0.7."""
        engine = AlertEngine()
        
        assert engine._calculate_severity(0.65) == 'low'
        assert engine._calculate_severity(0.5) == 'low'
