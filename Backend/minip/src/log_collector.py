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
from typing import Dict, Any, Optional
from datetime import datetime

from src.collection_config import CollectionConfig
from src.terminal_executor import TerminalExecutor
from src.data_processor import DataProcessor
from src.data_models import FeatureVector


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
        system = platform.system().lower()
        
        if system == 'windows':
            logger.info("Detected operating system: Windows")
            return 'windows'
        elif system == 'linux':
            logger.info("Detected operating system: Linux")
            return 'linux'
        else:
            error_msg = f"Unsupported operating system: {system}. Only Windows and Linux are supported."
            logger.critical(error_msg)
            raise OSError(error_msg)
    
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
        
        # Collect each metric
        for metric_name, command in commands.items():
            try:
                logger.debug(f"Collecting metric: {metric_name}")
                result = self.terminal_executor.execute(command)
                
                if result.success:
                    raw_data[metric_name] = result.stdout
                    logger.debug(f"Successfully collected {metric_name}")
                else:
                    logger.warning(
                        f"Failed to collect {metric_name}: {result.error_message}. "
                        f"Will use default value."
                    )
                    raw_data[metric_name] = ""
            
            except Exception as e:
                logger.warning(
                    f"Exception while collecting {metric_name}: {e}. "
                    f"Will use default value."
                )
                raw_data[metric_name] = ""
        
        # Add timestamp in ISO 8601 format
        raw_data['timestamp'] = datetime.utcnow().isoformat() + 'Z'
        
        logger.info(f"Metrics collection completed at {raw_data['timestamp']}")
        return raw_data
    
    def _schedule_collection(self) -> None:
        """
        Perform periodic collection in a loop.
        
        This method runs in a separate thread and collects metrics at the
        configured interval until stopped.
        
        Requirements:
            - 1.5: Collect logs every 5-10 seconds continuously
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
                
                # Wait for next collection interval
                self._stop_event.wait(self.config.collection_interval_seconds)
            
            except Exception as e:
                logger.error(f"Error during collection cycle: {e}", exc_info=True)
                # Continue running despite errors
                self._stop_event.wait(self.config.collection_interval_seconds)
        
        logger.info("Scheduled collection stopped")
    
    def collect_once(self) -> Optional[FeatureVector]:
        """
        Collect logs once and return structured data.
        
        This method performs a single collection cycle:
        1. Collect raw metrics from the system
        2. Process raw data into a FeatureVector
        3. Return the structured data
        
        Returns:
            FeatureVector with collected metrics, or None if collection fails
        
        Requirements:
            - 3.1-3.7: Collect all system metrics with proper handling
        """
        try:
            # Collect raw metrics
            raw_data = self._collect_metrics()
            
            # Process into feature vector
            feature_vector = self.data_processor.process(raw_data)
            
            # Validate the feature vector
            if self.data_processor.validate(feature_vector):
                logger.debug("Feature vector validated successfully")
                return feature_vector
            else:
                logger.error("Feature vector validation failed")
                return None
        
        except Exception as e:
            logger.error(f"Failed to collect metrics: {e}", exc_info=True)
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


if __name__ == "__main__":
    # Test the LogCollector
    from src.collection_config import CollectionConfig
    
    # Load configuration
    config = CollectionConfig.from_file("config.json")
    config.setup_logging()
    
    # Create collector
    collector = LogCollector(config)
    
    # Test single collection
    print("\n=== Testing Single Collection ===")
    feature_vector = collector.collect_once()
    
    if feature_vector:
        print(f"CPU Usage: {feature_vector.cpu_usage}%")
        print(f"Memory Usage: {feature_vector.memory_usage}%")
        print(f"Process Count: {feature_vector.process_count}")
        print(f"Network Connections: {feature_vector.network_connections}")
        print(f"Failed Logins: {feature_vector.failed_logins}")
        print(f"Timestamp: {feature_vector.timestamp}")
    else:
        print("Collection failed")
    
    # Test continuous collection
    print("\n=== Testing Continuous Collection (10 seconds) ===")
    collector.start()
    time.sleep(10)
    collector.stop()
    
    print("\nTest completed")
