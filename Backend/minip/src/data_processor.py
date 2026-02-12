"""
Data processor for parsing raw command output into structured feature vectors.

This module handles OS-specific parsing of system metrics including CPU usage,
memory usage, process counts, network connections, failed logins, and IP tracking.
"""

import re
import logging
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime

from src.data_models import FeatureVector


logger = logging.getLogger(__name__)


class DataProcessor:
    """
    Parse raw command output into structured FeatureVector objects.
    
    This class handles OS-specific parsing logic for Windows and Linux systems,
    extracting metrics and IP information from command outputs.
    
    Attributes:
        os_type: Operating system type ('windows' or 'linux')
    """
    
    def __init__(self, os_type: str):
        """
        Initialize the DataProcessor with OS type.
        
        Args:
            os_type: Operating system type ('windows' or 'linux')
        """
        self.os_type = os_type.lower()
        if self.os_type not in ['windows', 'linux']:
            raise ValueError(f"Unsupported OS type: {os_type}")
    
    def process(self, raw_data: Dict[str, str], node_id: str = "local") -> FeatureVector:
        """
        Parse raw command outputs into a structured FeatureVector.
        
        Args:
            raw_data: Dictionary mapping metric names to raw command outputs
                     Expected keys: 'cpu', 'memory', 'processes', 'network', 'failed_logins'
            node_id: Identifier for the machine/node
        
        Returns:
            FeatureVector with parsed metrics and IP information
        """
        # Parse basic metrics
        cpu_usage = self._parse_cpu(raw_data.get('cpu', ''))
        memory_usage = self._parse_memory(raw_data.get('memory', ''))
        process_count = self._parse_process_count(raw_data.get('processes', ''))
        network_connections = self._parse_network_connections(raw_data.get('network', ''))
        failed_logins = self._parse_failed_logins(raw_data.get('failed_logins', ''))
        
        # Extract IP information from network data
        source_ips, dest_ips = self._extract_ips_from_netstat(raw_data.get('network', ''))
        
        # Compute IP statistics
        ip_stats = self._compute_ip_statistics(
            source_ips,
            dest_ips,
            raw_data.get('failed_logins', '')
        )
        
        # Create timestamp
        timestamp = datetime.utcnow().isoformat() + 'Z'
        
        # Build feature vector
        feature_vector = FeatureVector(
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            process_count=process_count,
            network_connections=network_connections,
            failed_logins=failed_logins,
            timestamp=timestamp,
            node_id=node_id,
            unique_ip_count=ip_stats['unique_ip_count'],
            failed_attempts_per_ip=ip_stats['failed_attempts_per_ip'],
            connection_count_per_ip=ip_stats['connection_count_per_ip'],
            source_ips=source_ips,
            destination_ips=dest_ips
        )
        
        return feature_vector
    
    def validate(self, feature_vector: FeatureVector) -> bool:
        """
        Validate that a FeatureVector is complete and within valid ranges.
        
        Args:
            feature_vector: The FeatureVector to validate
        
        Returns:
            True if valid, False otherwise
        """
        try:
            # Check all required fields are present and not None
            if feature_vector.cpu_usage is None:
                logger.error("Validation failed: cpu_usage is None")
                return False
            if feature_vector.memory_usage is None:
                logger.error("Validation failed: memory_usage is None")
                return False
            if feature_vector.process_count is None:
                logger.error("Validation failed: process_count is None")
                return False
            if feature_vector.network_connections is None:
                logger.error("Validation failed: network_connections is None")
                return False
            if feature_vector.failed_logins is None:
                logger.error("Validation failed: failed_logins is None")
                return False
            if not feature_vector.timestamp:
                logger.error("Validation failed: timestamp is empty")
                return False
            
            # Check ranges
            if not (0 <= feature_vector.cpu_usage <= 100):
                logger.error(f"Validation failed: cpu_usage {feature_vector.cpu_usage} out of range [0, 100]")
                return False
            if not (0 <= feature_vector.memory_usage <= 100):
                logger.error(f"Validation failed: memory_usage {feature_vector.memory_usage} out of range [0, 100]")
                return False
            
            # Check counts are non-negative
            if feature_vector.process_count < 0:
                logger.error(f"Validation failed: process_count {feature_vector.process_count} is negative")
                return False
            if feature_vector.network_connections < 0:
                logger.error(f"Validation failed: network_connections {feature_vector.network_connections} is negative")
                return False
            if feature_vector.failed_logins < 0:
                logger.error(f"Validation failed: failed_logins {feature_vector.failed_logins} is negative")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return False
    
    def _parse_cpu(self, output: str) -> float:
        """Parse CPU usage based on OS type."""
        if self.os_type == 'windows':
            return self._parse_windows_cpu(output)
        else:
            return self._parse_linux_cpu(output)
    
    def _parse_memory(self, output: str) -> float:
        """Parse memory usage based on OS type."""
        if self.os_type == 'windows':
            return self._parse_windows_memory(output)
        else:
            return self._parse_linux_memory(output)
    
    def _parse_windows_cpu(self, output: str) -> float:
        """
        Parse Windows CPU usage from wmic output.
        
        Expected format:
        LoadPercentage
        45
        
        Args:
            output: Raw output from 'wmic cpu get loadpercentage'
        
        Returns:
            CPU usage percentage (0-100), or 0.0 on failure
        """
        try:
            lines = output.strip().split('\n')
            if len(lines) >= 2:
                # Second line contains the percentage
                cpu_value = float(lines[1].strip())
                return max(0.0, min(100.0, cpu_value))
        except (ValueError, IndexError) as e:
            logger.warning(f"Failed to parse Windows CPU usage: {e}")
        return 0.0
    
    def _parse_linux_cpu(self, output: str) -> float:
        """
        Parse Linux CPU usage from top output.
        
        Expected format:
        %Cpu(s): 12.5 us,  3.2 sy,  0.0 ni, 84.3 id, ...
        
        Args:
            output: Raw output from 'top -bn1 | grep "Cpu(s)"'
        
        Returns:
            CPU usage percentage (0-100), or 0.0 on failure
        """
        try:
            # Look for idle percentage and calculate usage
            match = re.search(r'(\d+\.\d+)\s+id', output)
            if match:
                idle = float(match.group(1))
                usage = 100.0 - idle
                return max(0.0, min(100.0, usage))
        except (ValueError, AttributeError) as e:
            logger.warning(f"Failed to parse Linux CPU usage: {e}")
        return 0.0
    
    def _parse_windows_memory(self, output: str) -> float:
        """
        Parse Windows memory usage from wmic output.
        
        Expected format:
        FreePhysicalMemory  TotalVisibleMemorySize
        4194304            16777216
        
        Args:
            output: Raw output from 'wmic OS get FreePhysicalMemory,TotalVisibleMemorySize'
        
        Returns:
            Memory usage percentage (0-100), or 0.0 on failure
        """
        try:
            lines = output.strip().split('\n')
            if len(lines) >= 2:
                # Second line contains the values
                values = lines[1].split()
                if len(values) >= 2:
                    free_memory = float(values[0])
                    total_memory = float(values[1])
                    if total_memory > 0:
                        used_memory = total_memory - free_memory
                        usage = (used_memory / total_memory) * 100.0
                        return max(0.0, min(100.0, usage))
        except (ValueError, IndexError, ZeroDivisionError) as e:
            logger.warning(f"Failed to parse Windows memory usage: {e}")
        return 0.0
    
    def _parse_linux_memory(self, output: str) -> float:
        """
        Parse Linux memory usage from free output.
        
        Expected format:
                      total        used        free      shared  buff/cache   available
        Mem:       16384000     8192000     4096000      102400     4096000     7168000
        
        Args:
            output: Raw output from 'free -m'
        
        Returns:
            Memory usage percentage (0-100), or 0.0 on failure
        """
        try:
            lines = output.strip().split('\n')
            for line in lines:
                if line.startswith('Mem:'):
                    values = line.split()
                    if len(values) >= 3:
                        total = float(values[1])
                        used = float(values[2])
                        if total > 0:
                            usage = (used / total) * 100.0
                            return max(0.0, min(100.0, usage))
        except (ValueError, IndexError, ZeroDivisionError) as e:
            logger.warning(f"Failed to parse Linux memory usage: {e}")
        return 0.0
    
    def _parse_process_count(self, output: str) -> int:
        """
        Parse process count from process list output.
        
        For both Windows (tasklist) and Linux (ps aux), count non-header lines.
        
        Args:
            output: Raw output from tasklist or ps aux
        
        Returns:
            Number of processes, or 0 on failure
        """
        try:
            lines = output.strip().split('\n')
            # Filter out empty lines and header lines
            process_lines = [line for line in lines if line.strip()]
            
            if self.os_type == 'windows':
                # Windows tasklist has header lines, skip them
                # Typically starts with "Image Name" or similar
                count = 0
                for line in process_lines:
                    # Skip header-like lines
                    if not line.startswith('Image Name') and not line.startswith('='):
                        count += 1
                return max(0, count)
            else:
                # Linux ps aux has one header line
                return max(0, len(process_lines) - 1)
        except Exception as e:
            logger.warning(f"Failed to parse process count: {e}")
        return 0
    
    def _parse_network_connections(self, output: str) -> int:
        """
        Parse network connection count from netstat output.
        
        Counts lines that represent active connections (contain IP addresses).
        
        Args:
            output: Raw output from netstat -an
        
        Returns:
            Number of network connections, or 0 on failure
        """
        try:
            lines = output.strip().split('\n')
            count = 0
            
            # IPv4 pattern to identify connection lines
            ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
            
            for line in lines:
                # Count lines that contain IP addresses (actual connections)
                if re.search(ip_pattern, line):
                    count += 1
            
            return max(0, count)
        except Exception as e:
            logger.warning(f"Failed to parse network connections: {e}")
        return 0
    
    def _parse_failed_logins(self, output: str) -> int:
        """
        Parse failed login count from authentication logs.
        
        For Windows: Count Event ID 4625 entries
        For Linux: Count "Failed password" entries
        
        Args:
            output: Raw output from wevtutil or journalctl
        
        Returns:
            Number of failed login attempts, or 0 on failure
        """
        try:
            lines = output.strip().split('\n')
            count = 0
            
            if self.os_type == 'windows':
                # Count Event ID 4625 occurrences
                for line in lines:
                    if 'Event ID: 4625' in line or 'EventID=4625' in line:
                        count += 1
            else:
                # Count "Failed password" occurrences
                for line in lines:
                    if 'Failed password' in line or 'failed password' in line:
                        count += 1
            
            return max(0, count)
        except Exception as e:
            logger.warning(f"Failed to parse failed logins: {e}")
        return 0
    
    def _extract_ips_from_netstat(self, output: str) -> Tuple[List[str], List[str]]:
        """
        Extract source and destination IP addresses from netstat output.
        
        Parses netstat lines to extract IP addresses from connection entries.
        Format: "TCP 192.168.1.100:50000 10.0.0.5:443 ESTABLISHED"
        
        Args:
            output: Raw output from netstat -an
        
        Returns:
            Tuple of (source_ips, destination_ips)
        """
        source_ips = []
        dest_ips = []
        
        try:
            # IPv4 pattern
            ip_pattern = r'\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
            
            lines = output.strip().split('\n')
            for line in lines:
                # Find all IP addresses in the line
                ips = re.findall(ip_pattern, line)
                
                # Netstat typically shows: protocol local_address foreign_address state
                # We consider the first IP as source, second as destination
                if len(ips) >= 2:
                    source_ips.append(ips[0])
                    dest_ips.append(ips[1])
        except Exception as e:
            logger.warning(f"Failed to extract IPs from netstat: {e}")
        
        return source_ips, dest_ips
    
    def _compute_ip_statistics(self, source_ips: List[str], dest_ips: List[str],
                               failed_login_output: str) -> Dict[str, Any]:
        """
        Compute IP-based statistics for the feature vector.
        
        Calculates:
        - unique_ip_count: Count of distinct IPs
        - connection_count_per_ip: Mapping of IPs to connection counts
        - failed_attempts_per_ip: Mapping of IPs to failed login counts
        
        Args:
            source_ips: List of source IP addresses
            dest_ips: List of destination IP addresses
            failed_login_output: Raw output from failed login logs
        
        Returns:
            Dictionary with IP statistics
        """
        # Combine all IPs
        all_ips = source_ips + dest_ips
        unique_ips = set(all_ips)
        
        # Count connections per IP
        connection_count_per_ip = {}
        for ip in all_ips:
            connection_count_per_ip[ip] = connection_count_per_ip.get(ip, 0) + 1
        
        # Extract failed attempts per IP
        failed_attempts_per_ip = self._extract_failed_attempts_per_ip(failed_login_output)
        
        return {
            'unique_ip_count': len(unique_ips),
            'failed_attempts_per_ip': failed_attempts_per_ip,
            'connection_count_per_ip': connection_count_per_ip
        }
    
    def _extract_failed_attempts_per_ip(self, log_output: str) -> Dict[str, int]:
        """
        Extract failed login attempts per IP from authentication logs.
        
        Searches for IP addresses in log lines containing failure keywords.
        
        Args:
            log_output: Raw output from authentication logs
        
        Returns:
            Dictionary mapping IP addresses to failed attempt counts
        """
        failed_per_ip = {}
        
        try:
            # IPv4 pattern
            ip_pattern = r'\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\b'
            
            lines = log_output.strip().split('\n')
            for line in lines:
                # Check if line indicates a failure
                if any(keyword in line.lower() for keyword in ['failed', 'failure', 'invalid', 'denied']):
                    # Extract all IPs from the line
                    ips = re.findall(ip_pattern, line)
                    for ip in ips:
                        failed_per_ip[ip] = failed_per_ip.get(ip, 0) + 1
        except Exception as e:
            logger.warning(f"Failed to extract failed attempts per IP: {e}")
        
        return failed_per_ip
