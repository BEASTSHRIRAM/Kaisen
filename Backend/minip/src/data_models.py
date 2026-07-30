"""
Data models for the Kaisen Log Collection Backend.

This module defines the core data structures used throughout the log collection
and anomaly detection system.
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, List, Any
from datetime import datetime
import uuid


@dataclass
class FeatureVector:
    """
    Structured representation of system metrics for anomaly detection.
    
    This class represents a complete snapshot of system state including
    CPU, memory, processes, network connections, and IP tracking information.
    
    Attributes:
        cpu_usage: CPU usage percentage (0-100)
        memory_usage: Memory usage percentage (0-100)
        process_count: Number of running processes
        network_connections: Number of active network connections
        failed_logins: Number of failed login attempts
        timestamp: ISO 8601 formatted timestamp
        node_id: Identifier for the machine/node (default: "local")
        unique_ip_count: Count of distinct IP addresses observed
        failed_attempts_per_ip: Mapping of IP addresses to failed login counts
        connection_count_per_ip: Mapping of IP addresses to connection counts
        source_ips: List of source IP addresses from network connections
        destination_ips: List of destination IP addresses from network connections
    """
    cpu_usage: float
    memory_usage: float
    process_count: int
    network_connections: int
    failed_logins: int
    timestamp: str
    node_id: str = "local"
    unique_ip_count: int = 0
    failed_attempts_per_ip: Dict[str, int] = field(default_factory=dict)
    connection_count_per_ip: Dict[str, int] = field(default_factory=dict)
    source_ips: List[str] = field(default_factory=list)
    destination_ips: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the FeatureVector to a dictionary.
        
        Returns:
            Dictionary representation of the feature vector
        """
        return asdict(self)
    
    def to_model_input(self) -> List[float]:
        """
        Convert to format expected by the anomaly detection model.
        
        The model expects 13-dimensional features (enhanced features):
        [failed_logins, file_access_count, cpu_usage,      # 3: basic metrics
         delta_logins, delta_files, delta_cpu,             # 6: deltas
         ma_logins, ma_files, sustained, time_in_state,    # 10: moving avgs + state
         outbound_conn, dst_ports, rare_port]              # 13: network features
        
        Currently, we have only 5 basic metrics, so we pad with zeros for enhanced features.
        
        Returns:
            List of 13 feature values in model-expected order
        """
        return [
            float(self.failed_logins),              # 0: login attempts
            float(self.process_count),              # 1: file access (approximated by process count)
            self.cpu_usage,                         # 2: cpu usage
            0.0,                                    # 3: delta_logins (not computed)
            0.0,                                    # 4: delta_files (not computed)
            0.0,                                    # 5: delta_cpu (not computed)
            float(self.failed_logins),              # 6: ma_logins (use current as MA)
            float(self.process_count),              # 7: ma_files (use current as MA)
            0.0,                                    # 8: sustained (not computed)
            0.0,                                    # 9: time_in_state (not computed)
            float(self.network_connections),        # 10: outbound_conn
            float(self.unique_ip_count),            # 11: dst_ports (approximated by unique IPs)
            0.0,                                    # 12: rare_port (not computed)
        ]


@dataclass
class PredictionResult:
    """
    Result from the anomaly detection model.
    
    Attributes:
        anomaly_score: Anomaly score between 0 and 1
        label: Classification label ('normal' or 'anomaly')
        confidence: Confidence score between 0 and 1
        feature_importance: Optional mapping of feature names to importance scores
    """
    anomaly_score: float
    label: str
    confidence: float
    feature_importance: Optional[Dict[str, float]] = None


@dataclass
class Alert:
    """
    Security alert generated when an anomaly is detected.
    
    Attributes:
        alert_id: Unique identifier for the alert (UUID)
        node_id: Identifier for the machine/node that triggered the alert
        timestamp: ISO 8601 formatted timestamp
        anomaly_score: The anomaly score that triggered the alert
        suspected_reason: Human-readable description of suspected cause
        feature_vector: The FeatureVector that triggered the alert
        severity: Alert severity level ('low', 'medium', 'high', 'critical')
        suspicious_ips: List of IP addresses exhibiting suspicious behavior
    """
    alert_id: str
    node_id: str
    timestamp: str
    anomaly_score: float
    suspected_reason: str
    feature_vector: FeatureVector
    severity: str
    suspicious_ips: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Initialize alert_id and timestamp if not provided."""
        if not self.alert_id:
            self.alert_id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat() + 'Z'


@dataclass
class ExecutionResult:
    """
    Result from terminal command execution.
    
    Attributes:
        success: Whether the command executed successfully
        stdout: Standard output from the command
        stderr: Standard error from the command
        return_code: Command exit code
        execution_time: Time taken to execute the command in seconds
        error_message: Optional error message if execution failed
    """
    success: bool
    stdout: str = ""
    stderr: str = ""
    return_code: int = 0
    execution_time: float = 0.0
    error_message: Optional[str] = None


@dataclass
class RemoteEndpoint:
    """
    Configuration for a remote log collection endpoint.
    
    Attributes:
        node_id: Unique identifier for the remote node
        url: HTTP/HTTPS URL for the remote endpoint
        auth_type: Authentication type ('api_key' or 'bearer')
        auth_token: Authentication token/key
        timeout: Request timeout in seconds (default: 30)
    """
    node_id: str
    url: str
    auth_type: str
    auth_token: str
    timeout: int = 30
