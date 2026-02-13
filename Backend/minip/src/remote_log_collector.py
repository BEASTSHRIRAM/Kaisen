"""
Remote log collector for the Kaisen Log Collection Backend.

This module fetches logs from remote machines via HTTP/HTTPS APIs,
handling authentication, retries, and schema validation.

Requirements validated:
- 13.1: Fetch logs from remote API endpoints via HTTP/HTTPS
- 13.2: Support authentication using API keys or bearer tokens
- 13.3: Retry up to 3 times with exponential backoff
- 13.4: Log error and continue with other endpoints on failure
- 13.5: Tag each log entry with source node_id
- 13.6: Merge remote logs with local logs in same pipeline
- 13.7: Support configuring multiple remote endpoints
- 13.8: Validate remote log data matches expected schema
- 13.9: Log warning and skip invalid entries
"""

import logging
import time
from typing import List, Dict, Any, Optional

import requests

from src.data_models import RemoteEndpoint, FeatureVector
from src.collection_config import CollectionConfig
from src.error_handler import handle_warning, handle_recoverable_error, log_error, ErrorCategory


logger = logging.getLogger(__name__)


class RemoteLogCollector:
    """
    Fetches logs from remote machines via HTTP/HTTPS APIs.
    
    This class is responsible for:
    - Making authenticated HTTP requests to remote endpoints
    - Implementing retry logic with exponential backoff
    - Validating remote log data against expected schema
    - Tagging logs with source node_id
    - Handling errors gracefully to continue with other endpoints
    
    Attributes:
        endpoints: List of RemoteEndpoint configurations
        config: CollectionConfig instance with system settings
    """
    
    # Required fields for remote log validation
    REQUIRED_FIELDS = {
        'cpu_usage', 'memory_usage', 'process_count',
        'network_connections', 'failed_logins', 'timestamp'
    }
    
    def __init__(self, endpoints: List[RemoteEndpoint], config: CollectionConfig):
        """
        Initialize the RemoteLogCollector with endpoint configurations.
        
        Args:
            endpoints: List of RemoteEndpoint configurations
            config: CollectionConfig instance with system settings
        
        Requirements:
            - 13.7: Support configuring multiple remote endpoints
        """
        self.endpoints = endpoints
        self.config = config
        
        logger.info(f"RemoteLogCollector initialized with {len(endpoints)} endpoints")
        for endpoint in endpoints:
            logger.debug(f"Endpoint configured: {endpoint.node_id} at {endpoint.url}")
    
    def collect_from_all(self) -> List[Dict[str, Any]]:
        """
        Collect logs from all configured endpoints.
        
        Iterates through all endpoints and collects logs from each.
        If an endpoint fails after retries, logs an error and continues
        with the remaining endpoints.
        
        Returns:
            List of log dictionaries from all successful endpoints
        
        Requirements:
            - 13.4: Continue with other endpoints when one fails
            - 13.6: Merge remote logs with local logs in same pipeline
            - 10.2: Continue operation after non-critical errors
        """
        all_logs = []
        
        logger.info(f"Starting collection from {len(self.endpoints)} remote endpoints")
        
        for endpoint in self.endpoints:
            try:
                log_data = self.collect_from_endpoint(endpoint)
                
                if log_data is not None:
                    all_logs.append(log_data)
                    logger.info(f"Successfully collected from endpoint: {endpoint.node_id}")
                else:
                    # RECOVERABLE ERROR: Endpoint failed but continue with others
                    handle_warning(
                        "RemoteLogCollector",
                        f"No data collected from endpoint: {endpoint.node_id}"
                    )
            
            except Exception as e:
                # RECOVERABLE ERROR: Unexpected error, continue with other endpoints
                handle_recoverable_error(
                    "RemoteLogCollector",
                    f"Unexpected error collecting from endpoint {endpoint.node_id}: {str(e)}",
                    e
                )
                # Continue with other endpoints
                continue
        
        logger.info(f"Remote collection completed. Collected {len(all_logs)} logs")
        return all_logs
    
    def collect_from_endpoint(self, endpoint: RemoteEndpoint) -> Optional[Dict[str, Any]]:
        """
        Collect logs from a single remote endpoint.
        
        Makes an HTTP request to the endpoint with authentication,
        validates the response schema, and tags the log with node_id.
        Implements retry logic with exponential backoff.
        
        Args:
            endpoint: RemoteEndpoint configuration
        
        Returns:
            Log data dictionary with node_id tag, or None if collection fails
        
        Requirements:
            - 13.1: Fetch logs from remote API endpoints via HTTP/HTTPS
            - 13.3: Retry up to 3 times with exponential backoff
            - 13.5: Tag each log entry with source node_id
            - 13.8: Validate remote log data matches expected schema
        """
        logger.debug(f"Collecting from endpoint: {endpoint.node_id}")
        
        # Attempt collection with retries
        for attempt in range(3):
            try:
                # Make HTTP request
                response_data = self._make_request(endpoint)
                
                if response_data is None:
                    # Request failed, will retry
                    if attempt < 2:
                        backoff_time = 2 ** attempt  # 1s, 2s, 4s
                        logger.warning(
                            f"Request to {endpoint.node_id} failed, "
                            f"retrying in {backoff_time}s (attempt {attempt + 1}/3)"
                        )
                        time.sleep(backoff_time)
                        continue
                    else:
                        logger.error(
                            f"Remote endpoint {endpoint.node_id} failed after 3 attempts"
                        )
                        return None
                
                # Validate schema
                if not self._validate_schema(response_data):
                    logger.warning(
                        f"Invalid schema from endpoint {endpoint.node_id}, skipping entry"
                    )
                    return None
                
                # Tag with node_id
                response_data['node_id'] = endpoint.node_id
                
                logger.debug(f"Successfully collected and validated data from {endpoint.node_id}")
                return response_data
            
            except Exception as e:
                if attempt < 2:
                    backoff_time = 2 ** attempt
                    logger.warning(
                        f"Error collecting from {endpoint.node_id}: {e}, "
                        f"retrying in {backoff_time}s (attempt {attempt + 1}/3)"
                    )
                    time.sleep(backoff_time)
                else:
                    logger.error(
                        f"Failed to collect from {endpoint.node_id} after 3 attempts: {e}"
                    )
                    return None
        
        return None
    
    def _make_request(self, endpoint: RemoteEndpoint) -> Optional[Dict[str, Any]]:
        """
        Make an authenticated HTTP request to a remote endpoint.
        
        Constructs appropriate authentication headers based on auth_type
        and makes the HTTP GET request.
        
        Args:
            endpoint: RemoteEndpoint configuration
        
        Returns:
            Response JSON data, or None if request fails
        
        Requirements:
            - 13.1: Fetch logs via HTTP/HTTPS
            - 13.2: Support authentication using API keys or bearer tokens
        """
        # Construct authentication headers
        headers = {}
        
        if endpoint.auth_type == 'api_key':
            headers['X-API-Key'] = endpoint.auth_token
        elif endpoint.auth_type == 'bearer':
            headers['Authorization'] = f'Bearer {endpoint.auth_token}'
        else:
            logger.warning(
                f"Unknown auth_type '{endpoint.auth_type}' for endpoint {endpoint.node_id}"
            )
        
        try:
            logger.debug(f"Making request to {endpoint.url}")
            
            response = requests.get(
                endpoint.url,
                headers=headers,
                timeout=endpoint.timeout
            )
            
            # Check HTTP status
            response.raise_for_status()
            
            # Parse JSON response
            data = response.json()
            
            logger.debug(f"Request successful: {endpoint.url}")
            return data
        
        except requests.exceptions.Timeout:
            logger.warning(f"Request timeout for endpoint {endpoint.node_id}")
            return None
        
        except requests.exceptions.ConnectionError:
            logger.warning(f"Connection error for endpoint {endpoint.node_id}")
            return None
        
        except requests.exceptions.HTTPError as e:
            logger.warning(f"HTTP error for endpoint {endpoint.node_id}: {e}")
            return None
        
        except requests.exceptions.RequestException as e:
            logger.warning(f"Request error for endpoint {endpoint.node_id}: {e}")
            return None
        
        except ValueError as e:
            logger.warning(f"Invalid JSON response from endpoint {endpoint.node_id}: {e}")
            return None
    
    def _validate_schema(self, data: Dict[str, Any]) -> bool:
        """
        Validate that remote log data matches the expected schema.
        
        Checks that all required fields are present and have appropriate types.
        
        Args:
            data: Log data dictionary to validate
        
        Returns:
            True if schema is valid, False otherwise
        
        Requirements:
            - 13.8: Validate remote log data matches expected schema
            - 13.9: Log warning and skip invalid entries
        """
        try:
            # Check for required fields
            missing_fields = self.REQUIRED_FIELDS - set(data.keys())
            
            if missing_fields:
                handle_warning(
                    "RemoteLogCollector",
                    f"Missing required fields in remote log: {missing_fields}"
                )
                return False
            
            # Validate field types
            try:
                # CPU and memory should be numeric and in valid range
                cpu = float(data['cpu_usage'])
                memory = float(data['memory_usage'])
                
                if not (0 <= cpu <= 100):
                    handle_warning(
                        "RemoteLogCollector",
                        f"Invalid cpu_usage value: {cpu}"
                    )
                    return False
                
                if not (0 <= memory <= 100):
                    handle_warning(
                        "RemoteLogCollector",
                        f"Invalid memory_usage value: {memory}"
                    )
                    return False
                
                # Counts should be non-negative integers
                process_count = int(data['process_count'])
                network_connections = int(data['network_connections'])
                failed_logins = int(data['failed_logins'])
                
                if process_count < 0 or network_connections < 0 or failed_logins < 0:
                    handle_warning(
                        "RemoteLogCollector",
                        "Negative count values in remote log"
                    )
                    return False
                
                # Timestamp should be a string
                if not isinstance(data['timestamp'], str):
                    handle_warning(
                        "RemoteLogCollector",
                        "Invalid timestamp type in remote log"
                    )
                    return False
                
                logger.debug("Remote log schema validation passed")
                return True
            
            except (ValueError, TypeError, KeyError) as e:
                handle_warning(
                    "RemoteLogCollector",
                    f"Schema validation error: {str(e)}"
                )
                return False
        except Exception as e:
            # RECOVERABLE ERROR: Unexpected validation error
            handle_recoverable_error(
                "RemoteLogCollector",
                f"Unexpected error during schema validation: {str(e)}",
                e
            )
            return False


if __name__ == "__main__":
    # Test the RemoteLogCollector
    from src.collection_config import CollectionConfig
    
    # Load configuration
    config = CollectionConfig.from_file("config.json")
    config.setup_logging()
    
    # Create test endpoints
    test_endpoints = [
        RemoteEndpoint(
            node_id="test_server_001",
            url="https://api.example.com/logs",
            auth_type="bearer",
            auth_token="test_token_123",
            timeout=10
        )
    ]
    
    # Create collector
    collector = RemoteLogCollector(endpoints=test_endpoints, config=config)
    
    # Test collection
    print("\n=== Testing Remote Collection ===")
    logs = collector.collect_from_all()
    
    print(f"Collected {len(logs)} logs from remote endpoints")
    for log in logs:
        print(f"Node: {log.get('node_id')}, Timestamp: {log.get('timestamp')}")
    
    print("\nTest completed")
