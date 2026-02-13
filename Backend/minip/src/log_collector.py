"""
Log collector for the Kaisen Log Collection Backend.

This module orchestrates the collection of system logs from local machines
at regular intervals. It detects the operating system, executes appropriate
commands, and coordinates with other components for processing and storage.

Requirements validated:
- 1.1: Execute Windows-specific commands on Windows
- 1.2: Execute Linux-specific commands on Linux
- 1.3: Detect operating system automatically at startup
- 1.4: Log error and terminate gracefully for unsupported OS
- 1.5: Collect logs every 5-10 seconds continuously
- 3.1-3.7: Collect all required system metrics
"""

import platform
import logging
import threading
import time
from typing import Dict, Any, Optional, List
from datetime import datetime

from src.collection_config import CollectionConfig
from src.terminal_executor import TerminalExecutor
from src.data_processor import DataProcessor
from src.data_models import FeatureVector
from src.model_interface import ModelInterface
from src.alert_engine import AlertEngine
from src.storage_manager import StorageManager
from src.graph_engine import GraphEngine
from src.remote_log_collector import RemoteLogCollector
from src.error_handler import (
    ErrorCategory, handle_critical_error, handle_recoverable_error,
    handle_warning, log_error
)


logger = logging.getLogger(__name__)


class LogCollector:
    """
    Orchestrates log collection from local machine at regular intervals.
    
    This class is responsible for:
    - Detecting the operating system
    - Selecting appropriate commands for the OS
    - Executing commands via TerminalExecutor
    - Coordinating with DataProcessor for parsing
    - Managing collection scheduling
    
    Attributes:
        config: CollectionConfig instance with system settings
        os_type: Detected operating system ('windows' or 'linux')
        terminal_executor: TerminalExecutor for safe command execution
        data_processor: DataProcessor for parsing command output
        model_interface: ModelInterface for anomaly detection
        alert_engine: AlertEngine for generating alerts
        storage_manager: StorageManager for persisting data
        graph_engine: GraphEngine for attack graph modeling
        remote_log_collector: RemoteLogCollector for fetching remote logs
        collection_thread: Thread for continuous collection
        running: Flag indicating if collection is active
    """
    
    # Command mappings for different operating systems
    COMMANDS = {
        'windows': {
            'cpu': 'wmic cpu get loadpercentage',
            'memory': 'wmic OS get FreePhysicalMemory,TotalVisibleMemorySize',
            'processes': 'tasklist',
            'network': 'netstat -an',
            'failed_logins': 'wevtutil qe Security /q:"*[System[(EventID=4625)]]" /c:100 /rd:true /f:text'
        },
        'linux': {
            'cpu': 'top -bn1 | grep "Cpu(s)"',
            'memory': 'free -m',
            'processes': 'ps aux',
            'network': 'netstat -an',
            'failed_logins': 'journalctl _SYSTEMD_UNIT=sshd.service | grep "Failed password" | tail -100'
        }
    }
    
    def __init__(self, config: CollectionConfig):
        """
        Initialize the LogCollector with configuration.
        
        Args:
            config: CollectionConfig instance with system settings
        
        Raises:
            OSError: If the operating system is not supported
        """
        self.config = config
        self.os_type = self._detect_os()
        
        # Initialize terminal executor with whitelist
        self.terminal_executor = TerminalExecutor(
            whitelist=config.command_whitelist,
            timeout=config.command_timeout
        )
        
        # Initialize data processor
        self.data_processor = DataProcessor(os_type=self.os_type)
        
        # Initialize model interface
        try:
            self.model_interface = ModelInterface(model_path=config.model_path)
            logger.info(f"Model loaded from: {config.model_path}")
        except Exception as e:
            # CRITICAL ERROR: Model loading is essential
            handle_critical_error(
                "LogCollector",
                f"Failed to load anomaly detection model: {str(e)}",
                e
            )
            raise
        
        # Initialize alert engine
        self.alert_engine = AlertEngine(threshold=config.anomaly_threshold)
        logger.info(f"Alert engine initialized with threshold: {config.anomaly_threshold}")
        
        # Initialize storage manager
        self.storage_manager = StorageManager(
            log_dir=config.log_dir,
            history_file=config.history_file,
            alerts_file=config.alerts_file
        )
        logger.info(f"Storage manager initialized: {config.log_dir}")
        
        # Initialize graph engine
        self.graph_engine = GraphEngine()
        logger.info("Graph engine initialized")
        
        # Initialize remote log collector if endpoints configured
        if config.remote_endpoints:
            from src.data_models import RemoteEndpoint
            endpoints = [
                RemoteEndpoint(
                    node_id=ep['node_id'],
                    url=ep['url'],
                    auth_type=ep['auth_type'],
                    auth_token=ep['auth_token'],
                    timeout=ep.get('timeout', 30)
                )
                for ep in config.remote_endpoints
            ]
            self.remote_log_collector = RemoteLogCollector(endpoints=endpoints, config=config)
            logger.info(f"Remote log collector initialized with {len(endpoints)} endpoints")
        else:
            self.remote_log_collector = None
            logger.info("No remote endpoints configured")
        
        # Collection control
        self.collection_thread: Optional[threading.Thread] = None
        self.running = False
        self._stop_event = threading.Event()
        
        logger.info(f"LogCollector initialized for OS: {self.os_type}")
    
    def _detect_os(self) -> str:
        """
        Detect the operating system.
        
        Uses platform.system() to determine if running on Windows or Linux.
        
        Returns:
            'windows' or 'linux'
        
        Raises:
            OSError: If the operating system is not Windows or Linux
        
        Requirements:
            - 1.3: Detect operating system automatically at startup
            - 1.4: Log error and terminate gracefully for unsupported OS
        """
        try:
            system = platform.system().lower()
            
            if system == 'windows':
                logger.info("Detected operating system: Windows")
                return 'windows'
            elif system == 'linux':
                logger.info("Detected operating system: Linux")
                return 'linux'
            else:
                # CRITICAL ERROR: Unsupported OS - terminate gracefully
                error_msg = f"Unsupported operating system: {system}. Only Windows and Linux are supported."
                handle_critical_error("LogCollector", error_msg)
                raise OSError(error_msg)  # Won't reach here due to sys.exit in handle_critical_error
        except Exception as e:
            # CRITICAL ERROR: Cannot detect OS - terminate gracefully
            handle_critical_error("LogCollector", f"Failed to detect operating system: {str(e)}", e)
            raise
    
    def _get_commands_for_os(self) -> Dict[str, str]:
        """
        Get the command mapping for the detected operating system.
        
        Returns:
            Dictionary mapping metric names to OS-specific commands
        
        Requirements:
            - 1.1: Return Windows commands for Windows OS
            - 1.2: Return Linux commands for Linux OS
        """
        commands = self.COMMANDS.get(self.os_type, {})
        logger.debug(f"Using command set for {self.os_type}: {list(commands.keys())}")
        return commands

    
    def _collect_metrics(self) -> Dict[str, Any]:
        """
        Gather all system metrics by executing OS-specific commands.
        
        Executes commands for CPU, memory, processes, network, and failed logins.
        If any metric collection fails, uses a default value of 0 and logs a warning.
        
        Returns:
            Dictionary containing raw command outputs and metadata
        
        Requirements:
            - 3.1: Collect CPU usage percentage
            - 3.2: Collect memory usage percentage
            - 3.3: Collect count of running processes
            - 3.4: Collect count of active network connections
            - 3.5: Collect count of failed login attempts
            - 3.6: Use default value of 0 when metric cannot be collected
            - 3.7: Timestamp each collection with ISO 8601 format
        """
        commands = self._get_commands_for_os()
        raw_data = {}
        
        # Collect each metric with error handling
        for metric_name, command in commands.items():
            try:
                logger.debug(f"Collecting metric: {metric_name}")
                result = self.terminal_executor.execute(command)
                
                if result.success:
                    raw_data[metric_name] = result.stdout
                    logger.debug(f"Successfully collected {metric_name}")
                else:
                    # RECOVERABLE ERROR: Metric collection failed, use default
                    handle_warning(
                        "LogCollector",
                        f"Failed to collect {metric_name}: {result.error_message}. Will use default value."
                    )
                    raw_data[metric_name] = ""
            
            except Exception as e:
                # RECOVERABLE ERROR: Exception during metric collection
                handle_recoverable_error(
                    "LogCollector",
                    f"Exception while collecting {metric_name}: {str(e)}. Will use default value.",
                    e
                )
                raw_data[metric_name] = ""
        
        # Add timestamp in ISO 8601 format
        try:
            raw_data['timestamp'] = datetime.utcnow().isoformat() + 'Z'
        except Exception as e:
            # RECOVERABLE ERROR: Timestamp generation failed
            handle_recoverable_error(
                "LogCollector",
                f"Failed to generate timestamp: {str(e)}. Using fallback.",
                e
            )
            raw_data['timestamp'] = datetime.now().isoformat() + 'Z'
        
        logger.info(f"Metrics collection completed at {raw_data['timestamp']}")
        return raw_data
    
    def _schedule_collection(self) -> None:
        """
        Perform periodic collection in a loop.
        
        This method runs in a separate thread and collects metrics at the
        configured interval until stopped.
        
        Requirements:
            - 1.5: Collect logs every 5-10 seconds continuously
            - 10.2: Continue operation after non-critical errors
        """
        logger.info(
            f"Starting scheduled collection with interval: "
            f"{self.config.collection_interval_seconds}s"
        )
        
        while not self._stop_event.is_set():
            try:
                # Collect once
                feature_vector = self.collect_once()
                
                if feature_vector:
                    logger.info(
                        f"Collection cycle completed. "
                        f"CPU: {feature_vector.cpu_usage:.1f}%, "
                        f"Memory: {feature_vector.memory_usage:.1f}%, "
                        f"Processes: {feature_vector.process_count}, "
                        f"Network: {feature_vector.network_connections}, "
                        f"Failed logins: {feature_vector.failed_logins}"
                    )
                else:
                    # RECOVERABLE ERROR: Collection failed but continue
                    handle_warning(
                        "LogCollector",
                        "Collection cycle returned None, will retry on next interval"
                    )
                
                # Wait for next collection interval
                self._stop_event.wait(self.config.collection_interval_seconds)
            
            except Exception as e:
                # RECOVERABLE ERROR: Continue running despite errors
                handle_recoverable_error(
                    "LogCollector",
                    f"Error during collection cycle: {str(e)}. Continuing operation.",
                    e
                )
                # Wait before retrying
                self._stop_event.wait(self.config.collection_interval_seconds)
        
        logger.info("Scheduled collection stopped")
    
    def collect_once(self) -> Optional[FeatureVector]:
        """
        Collect logs once and return structured data.
        
        This method performs a single collection cycle:
        1. Collect raw metrics from the system
        2. Collect remote logs if configured
        3. Process raw data into a FeatureVector
        4. Run anomaly detection on the feature vector
        5. Generate alerts if anomaly threshold exceeded
        6. Update attack graph with new data
        7. Save logs and alerts to storage
        
        Returns:
            FeatureVector with collected metrics, or None if collection fails
        
        Requirements:
            - 3.1-3.7: Collect all system metrics with proper handling
            - 10.2: Continue operation after non-critical errors
            - 11.1: Integrate all components in end-to-end pipeline
            - 11.5: Use existing codebase patterns
            - 13.6: Merge remote and local logs
        """
        try:
            # Step 1: Collect raw metrics from local system
            raw_data = self._collect_metrics()
            
            # Step 2: Collect remote logs if configured
            remote_logs = []
            if self.remote_log_collector:
                try:
                    remote_logs = self.remote_log_collector.collect_from_all()
                    logger.debug(f"Collected {len(remote_logs)} remote logs")
                except Exception as e:
                    # RECOVERABLE ERROR: Remote collection failed, continue with local
                    handle_recoverable_error(
                        "LogCollector",
                        f"Remote log collection failed: {str(e)}. Continuing with local logs.",
                        e
                    )
            
            # Step 3: Process local data into feature vector
            try:
                feature_vector = self.data_processor.process(raw_data)
            except Exception as e:
                # RECOVERABLE ERROR: Processing failed
                handle_recoverable_error(
                    "LogCollector",
                    f"Failed to process raw data into feature vector: {str(e)}",
                    e
                )
                return None
            
            # Step 4: Validate the feature vector
            try:
                if not self.data_processor.validate(feature_vector):
                    # RECOVERABLE ERROR: Validation failed
                    handle_warning(
                        "LogCollector",
                        "Feature vector validation failed, skipping this collection"
                    )
                    return None
            except Exception as e:
                # RECOVERABLE ERROR: Validation threw exception
                handle_recoverable_error(
                    "LogCollector",
                    f"Exception during feature vector validation: {str(e)}",
                    e
                )
                return None
            
            # Step 5: Run anomaly detection
            try:
                prediction = self.model_interface.predict(feature_vector)
                logger.debug(
                    f"Anomaly detection: score={prediction.anomaly_score:.3f}, "
                    f"label={prediction.label}"
                )
            except Exception as e:
                # RECOVERABLE ERROR: Prediction failed, continue without it
                handle_recoverable_error(
                    "LogCollector",
                    f"Anomaly detection failed: {str(e)}. Skipping alert generation.",
                    e
                )
                prediction = None
            
            # Step 6: Generate alert if threshold exceeded
            alert = None
            if prediction:
                try:
                    alert = self.alert_engine.process_prediction(
                        node_id=feature_vector.node_id,
                        prediction=prediction,
                        feature_vector=feature_vector
                    )
                    
                    if alert:
                        logger.warning(
                            f"ALERT: {alert.severity.upper()} - {alert.suspected_reason} "
                            f"(score={alert.anomaly_score:.3f})"
                        )
                except Exception as e:
                    # RECOVERABLE ERROR: Alert generation failed
                    handle_recoverable_error(
                        "LogCollector",
                        f"Alert generation failed: {str(e)}",
                        e
                    )
            
            # Step 7: Update attack graph
            try:
                # Add/update machine node with anomaly score
                if prediction:
                    if feature_vector.node_id not in self.graph_engine.graph:
                        self.graph_engine.add_node(
                            feature_vector.node_id,
                            'machine',
                            {'timestamp': feature_vector.timestamp}
                        )
                    self.graph_engine.update_anomaly_score(
                        feature_vector.node_id,
                        prediction.anomaly_score
                    )
                
                # Add IP nodes and edges from feature vector
                self.graph_engine.add_ip_nodes_from_feature_vector(feature_vector)
                
                # Propagate risk scores
                self.graph_engine.propagate_risk()
                
                logger.debug("Attack graph updated")
            except Exception as e:
                # RECOVERABLE ERROR: Graph update failed
                handle_recoverable_error(
                    "LogCollector",
                    f"Attack graph update failed: {str(e)}",
                    e
                )
            
            # Step 8: Save log to storage
            try:
                if not self.storage_manager.save_log(feature_vector):
                    handle_warning(
                        "LogCollector",
                        "Failed to save log to storage"
                    )
            except Exception as e:
                # RECOVERABLE ERROR: Storage failed
                handle_recoverable_error(
                    "LogCollector",
                    f"Exception while saving log: {str(e)}",
                    e
                )
            
            # Step 9: Save alert to storage if generated
            if alert:
                try:
                    if not self.storage_manager.save_alert(alert):
                        handle_warning(
                            "LogCollector",
                            f"Failed to save alert {alert.alert_id} to storage"
                        )
                except Exception as e:
                    # RECOVERABLE ERROR: Alert storage failed
                    handle_recoverable_error(
                        "LogCollector",
                        f"Exception while saving alert: {str(e)}",
                        e
                    )
            
            # Step 10: Process remote logs through the same pipeline
            for remote_log in remote_logs:
                try:
                    # Convert remote log dict to FeatureVector
                    remote_fv = FeatureVector(
                        cpu_usage=remote_log['cpu_usage'],
                        memory_usage=remote_log['memory_usage'],
                        process_count=remote_log['process_count'],
                        network_connections=remote_log['network_connections'],
                        failed_logins=remote_log['failed_logins'],
                        timestamp=remote_log['timestamp'],
                        node_id=remote_log['node_id'],
                        unique_ip_count=remote_log.get('unique_ip_count', 0),
                        failed_attempts_per_ip=remote_log.get('failed_attempts_per_ip', {}),
                        connection_count_per_ip=remote_log.get('connection_count_per_ip', {}),
                        source_ips=remote_log.get('source_ips', []),
                        destination_ips=remote_log.get('destination_ips', [])
                    )
                    
                    # Run through the same pipeline
                    remote_prediction = self.model_interface.predict(remote_fv)
                    remote_alert = self.alert_engine.process_prediction(
                        node_id=remote_fv.node_id,
                        prediction=remote_prediction,
                        feature_vector=remote_fv
                    )
                    
                    # Update graph
                    if remote_fv.node_id not in self.graph_engine.graph:
                        self.graph_engine.add_node(
                            remote_fv.node_id,
                            'remote_server',
                            {'timestamp': remote_fv.timestamp}
                        )
                    self.graph_engine.update_anomaly_score(
                        remote_fv.node_id,
                        remote_prediction.anomaly_score
                    )
                    self.graph_engine.add_ip_nodes_from_feature_vector(remote_fv)
                    
                    # Save to storage
                    self.storage_manager.save_log(remote_fv)
                    if remote_alert:
                        self.storage_manager.save_alert(remote_alert)
                        logger.warning(
                            f"REMOTE ALERT: {remote_alert.severity.upper()} from {remote_fv.node_id}"
                        )
                
                except Exception as e:
                    # RECOVERABLE ERROR: Remote log processing failed
                    handle_recoverable_error(
                        "LogCollector",
                        f"Failed to process remote log: {str(e)}",
                        e
                    )
                    continue
            
            logger.debug("Collection cycle completed successfully")
            return feature_vector
        
        except Exception as e:
            # RECOVERABLE ERROR: Unexpected error during collection
            handle_recoverable_error(
                "LogCollector",
                f"Unexpected error in collect_once: {str(e)}",
                e
            )
            return None
    
    def start(self) -> None:
        """
        Start continuous log collection.
        
        Launches a background thread that performs periodic collection
        at the configured interval.
        
        Requirements:
            - 1.5: Collect logs continuously at regular intervals
        """
        if self.running:
            logger.warning("LogCollector is already running")
            return
        
        self.running = True
        self._stop_event.clear()
        
        # Start collection thread
        self.collection_thread = threading.Thread(
            target=self._schedule_collection,
            name="LogCollectionThread",
            daemon=True
        )
        self.collection_thread.start()
        
        logger.info("LogCollector started")
    
    def stop(self) -> None:
        """
        Stop log collection gracefully.
        
        Signals the collection thread to stop and waits for it to finish.
        """
        if not self.running:
            logger.warning("LogCollector is not running")
            return
        
        logger.info("Stopping LogCollector...")
        
        self.running = False
        self._stop_event.set()
        
        # Wait for collection thread to finish
        if self.collection_thread and self.collection_thread.is_alive():
            self.collection_thread.join(timeout=5.0)
            
            if self.collection_thread.is_alive():
                logger.warning("Collection thread did not stop within timeout")
            else:
                logger.info("Collection thread stopped successfully")
        
        logger.info("LogCollector stopped")
    
    def export_attack_graph(self, output_path: str = "logs/attack_graph.json") -> bool:
        """
        Export the current attack graph to a JSON file.
        
        Args:
            output_path: Path where the graph JSON should be saved
            
        Returns:
            True if export succeeded, False otherwise
            
        Requirements:
            - 12.9: Export attack graph in JSON format
        """
        try:
            import os
            
            # Get JSON representation
            graph_json = self.graph_engine.export_json()
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Write to file
            with open(output_path, 'w') as f:
                f.write(graph_json)
            
            logger.info(f"Attack graph exported to: {output_path}")
            return True
        
        except Exception as e:
            handle_recoverable_error(
                "LogCollector",
                f"Failed to export attack graph: {str(e)}",
                e
            )
            return False
    
    def get_highest_risk_path(self) -> List[str]:
        """
        Get the highest risk attack path from the current graph.
        
        Returns:
            List of node IDs representing the attack path
            
        Requirements:
            - 12.7: Identify highest-risk attack path
        """
        try:
            return self.graph_engine.find_highest_risk_path()
        except Exception as e:
            handle_recoverable_error(
                "LogCollector",
                f"Failed to find highest risk path: {str(e)}",
                e
            )
            return []


if __name__ == "__main__":
    # Test the LogCollector with full integration
    from src.collection_config import CollectionConfig
    
    # Load configuration
    config = CollectionConfig.from_file("config.json")
    config.setup_logging()
    
    # Create collector
    collector = LogCollector(config)
    
    # Test single collection with full pipeline
    print("\n=== Testing Single Collection with Full Pipeline ===")
    feature_vector = collector.collect_once()
    
    if feature_vector:
        print(f"CPU Usage: {feature_vector.cpu_usage}%")
        print(f"Memory Usage: {feature_vector.memory_usage}%")
        print(f"Process Count: {feature_vector.process_count}")
        print(f"Network Connections: {feature_vector.network_connections}")
        print(f"Failed Logins: {feature_vector.failed_logins}")
        print(f"Timestamp: {feature_vector.timestamp}")
        print(f"Unique IPs: {feature_vector.unique_ip_count}")
    else:
        print("Collection failed")
    
    # Export attack graph
    print("\n=== Exporting Attack Graph ===")
    if collector.export_attack_graph():
        print("Attack graph exported successfully")
    
    # Get highest risk path
    print("\n=== Finding Highest Risk Path ===")
    risk_path = collector.get_highest_risk_path()
    if risk_path:
        print(f"Highest risk path: {' -> '.join(risk_path)}")
    else:
        print("No high-risk paths found")
    
    # Test continuous collection
    print("\n=== Testing Continuous Collection (10 seconds) ===")
    collector.start()
    time.sleep(10)
    collector.stop()
    
    # Final graph export
    print("\n=== Final Attack Graph Export ===")
    collector.export_attack_graph("logs/final_attack_graph.json")
    
    print("\nTest completed")
