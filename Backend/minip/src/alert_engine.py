"""
Alert Engine for the Kaisen Log Collection Backend.

This module generates security alerts when anomalies are detected,
analyzes abnormal metrics to determine suspected reasons, and identifies
suspicious IP addresses exhibiting abnormal behavior.
"""

import logging
import uuid
import time
from datetime import datetime
from typing import Optional, List
from src.data_models import Alert, PredictionResult, FeatureVector
from src.error_handler import handle_warning, handle_recoverable_error


logger = logging.getLogger(__name__)


class AlertEngine:
    """
    Generates alerts when anomaly scores exceed configured thresholds.
    
    The AlertEngine analyzes prediction results and feature vectors to:
    - Generate alerts when anomaly thresholds are exceeded
    - Determine suspected reasons based on abnormal metrics
    - Identify suspicious IP addresses
    - Calculate alert severity based on anomaly scores
    
    Attributes:
        threshold: Anomaly score threshold for alert generation (default: 0.7)
    """
    
    def __init__(self, threshold: float = 0.7):
        """
        Initialize the AlertEngine with a configurable threshold.
        
        Args:
            threshold: Anomaly score threshold above which alerts are generated.
                      Must be between 0 and 1. Default is 0.7.
        
        Raises:
            ValueError: If threshold is not between 0 and 1
        """
        if not 0 <= threshold <= 1:
            raise ValueError(f"Threshold must be between 0 and 1, got {threshold}")
        
        self.threshold = threshold
        logger.info(f"AlertEngine initialized with threshold={threshold}")
    
    def process_prediction(
        self,
        node_id: str,
        prediction: PredictionResult,
        feature_vector: FeatureVector
    ) -> Optional[Alert]:
        """
        Process a prediction result and generate an alert if threshold is exceeded.
        
        This method checks if the anomaly score exceeds the configured threshold.
        If so, it generates a complete Alert with:
        - Unique alert ID (UUID)
        - Timestamp
        - Suspected reason based on abnormal metrics
        - Severity level
        - List of suspicious IP addresses
        
        Args:
            node_id: Identifier for the machine/node
            prediction: PredictionResult from the anomaly detection model
            feature_vector: FeatureVector containing the system metrics
        
        Returns:
            Alert object if threshold exceeded, None otherwise
        
        Validates: Requirements 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 14.10
        """
        try:
            # Check if anomaly score exceeds threshold
            if prediction.anomaly_score <= self.threshold:
                logger.debug(
                    f"Anomaly score {prediction.anomaly_score:.3f} below threshold "
                    f"{self.threshold}, no alert generated"
                )
                return None
            
            # Generate alert components with error handling
            try:
                alert_id = str(uuid.uuid4())
            except Exception as e:
                handle_warning("AlertEngine", f"Failed to generate UUID: {str(e)}")
                alert_id = f"alert-{int(time.time())}"
            
            try:
                timestamp = datetime.utcnow().isoformat() + 'Z'
            except Exception as e:
                handle_warning("AlertEngine", f"Failed to generate timestamp: {str(e)}")
                timestamp = datetime.now().isoformat() + 'Z'
            
            try:
                suspected_reason = self.determine_suspected_reason(feature_vector)
            except Exception as e:
                handle_warning("AlertEngine", f"Failed to determine suspected reason: {str(e)}")
                suspected_reason = "anomalous pattern detected"
            
            try:
                severity = self._calculate_severity(prediction.anomaly_score)
            except Exception as e:
                handle_warning("AlertEngine", f"Failed to calculate severity: {str(e)}")
                severity = "medium"
            
            try:
                suspicious_ips = self.identify_suspicious_ips(feature_vector)
            except Exception as e:
                handle_warning("AlertEngine", f"Failed to identify suspicious IPs: {str(e)}")
                suspicious_ips = []
            
            # Create alert
            try:
                alert = Alert(
                    alert_id=alert_id,
                    node_id=node_id,
                    timestamp=timestamp,
                    anomaly_score=prediction.anomaly_score,
                    suspected_reason=suspected_reason,
                    feature_vector=feature_vector,
                    severity=severity,
                    suspicious_ips=suspicious_ips
                )
                
                logger.warning(
                    f"Alert generated: {alert_id} for node {node_id} "
                    f"(score={prediction.anomaly_score:.3f}, severity={severity})"
                )
                
                return alert
            except Exception as e:
                handle_recoverable_error(
                    "AlertEngine",
                    f"Failed to create Alert object: {str(e)}",
                    e
                )
                return None
        
        except Exception as e:
            # RECOVERABLE ERROR: Unexpected error during alert processing
            handle_recoverable_error(
                "AlertEngine",
                f"Unexpected error in process_prediction: {str(e)}",
                e
            )
            return None
    
    def determine_suspected_reason(self, feature_vector: FeatureVector) -> str:
        """
        Analyze feature vector to determine which metrics are abnormal.
        
        This method examines each metric in the feature vector against
        predefined thresholds to identify abnormal behavior patterns.
        
        Thresholds:
        - CPU usage > 80%
        - Memory usage > 85%
        - Failed logins > 10
        - Network connections > 100
        - Process count > 200
        - Unique IP count > 50
        
        Args:
            feature_vector: FeatureVector containing system metrics
        
        Returns:
            Comma-separated string of suspected reasons, or
            "anomalous pattern detected" if no specific threshold exceeded
        
        Validates: Requirement 7.5
        """
        reasons = []
        
        # Check CPU usage
        if feature_vector.cpu_usage > 80:
            reasons.append("high CPU usage")
        
        # Check memory usage
        if feature_vector.memory_usage > 85:
            reasons.append("high memory usage")
        
        # Check failed logins
        if feature_vector.failed_logins > 10:
            reasons.append("multiple failed logins")
        
        # Check network connections
        if feature_vector.network_connections > 100:
            reasons.append("excessive network connections")
        
        # Check process count
        if feature_vector.process_count > 200:
            reasons.append("high process count")
        
        # Check unique IP count
        if feature_vector.unique_ip_count > 50:
            reasons.append("connections to many unique IPs")
        
        # Return combined reasons or default message
        if not reasons:
            return "anomalous pattern detected"
        
        return ", ".join(reasons)
    
    def identify_suspicious_ips(self, feature_vector: FeatureVector) -> List[str]:
        """
        Identify IP addresses exhibiting abnormal behavior.
        
        An IP is considered suspicious if:
        - It has more than 5 failed login attempts, OR
        - It has more than 50 network connections
        
        Args:
            feature_vector: FeatureVector containing IP statistics
        
        Returns:
            List of suspicious IP addresses (may be empty)
        
        Validates: Requirement 14.10
        """
        suspicious = []
        
        # Check for IPs with high failed attempts
        for ip, count in feature_vector.failed_attempts_per_ip.items():
            if count > 5:
                suspicious.append(ip)
                logger.debug(f"IP {ip} marked suspicious: {count} failed attempts")
        
        # Check for IPs with excessive connections
        for ip, count in feature_vector.connection_count_per_ip.items():
            if count > 50 and ip not in suspicious:
                suspicious.append(ip)
                logger.debug(f"IP {ip} marked suspicious: {count} connections")
        
        return suspicious
    
    def _calculate_severity(self, anomaly_score: float) -> str:
        """
        Calculate alert severity based on anomaly score.
        
        Severity levels:
        - critical: score >= 0.9
        - high: score >= 0.8
        - medium: score >= 0.7
        - low: score < 0.7
        
        Args:
            anomaly_score: Anomaly score between 0 and 1
        
        Returns:
            Severity level as string
        """
        if anomaly_score >= 0.9:
            return 'critical'
        elif anomaly_score >= 0.8:
            return 'high'
        elif anomaly_score >= 0.7:
            return 'medium'
        else:
            return 'low'
