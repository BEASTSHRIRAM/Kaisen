"""
Integration test for the full log collection pipeline.

This test verifies that all components work together correctly:
- LogCollector orchestrates the entire pipeline
- TerminalExecutor executes commands
- DataProcessor parses output
- ModelInterface runs predictions
- AlertEngine generates alerts
- StorageManager persists data
- GraphEngine builds attack graphs
"""

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.log_collector import LogCollector
from src.collection_config import CollectionConfig


def test_full_collection_pipeline():
    """
    Test the complete end-to-end collection pipeline.
    
    This integration test verifies:
    1. LogCollector can be initialized with all components
    2. A single collection cycle completes successfully
    3. Data is processed through all pipeline stages
    4. Logs and alerts are saved to storage
    5. Attack graph is updated
    """
    # Create temporary directory for test logs
    test_dir = tempfile.mkdtemp(prefix="test_logs_")
    
    try:
        # Create test configuration
        config = CollectionConfig(
            collection_interval_seconds=5,
            model_path=str(Path(__file__).parent.parent.parent / "models" / "best_model.h5"),
            anomaly_threshold=0.7,
            log_dir=test_dir,
            history_file="history.json",
            alerts_file="alerts.json",
            remote_endpoints=[],  # No remote endpoints for this test
            command_timeout=30,
            log_level="INFO"
        )
        
        # Initialize LogCollector
        print("\n=== Initializing LogCollector ===")
        collector = LogCollector(config)
        
        assert collector.os_type in ['windows', 'linux'], "OS should be detected"
        assert collector.terminal_executor is not None, "TerminalExecutor should be initialized"
        assert collector.data_processor is not None, "DataProcessor should be initialized"
        assert collector.model_interface is not None, "ModelInterface should be initialized"
        assert collector.alert_engine is not None, "AlertEngine should be initialized"
        assert collector.storage_manager is not None, "StorageManager should be initialized"
        assert collector.graph_engine is not None, "GraphEngine should be initialized"
        
        print("✓ All components initialized successfully")
        
        # Perform single collection
        print("\n=== Running Single Collection Cycle ===")
        feature_vector = collector.collect_once()
        
        assert feature_vector is not None, "Collection should return a feature vector"
        assert 0 <= feature_vector.cpu_usage <= 100, "CPU usage should be in valid range"
        assert 0 <= feature_vector.memory_usage <= 100, "Memory usage should be in valid range"
        assert feature_vector.process_count >= 0, "Process count should be non-negative"
        assert feature_vector.network_connections >= 0, "Network connections should be non-negative"
        assert feature_vector.failed_logins >= 0, "Failed logins should be non-negative"
        assert feature_vector.timestamp, "Timestamp should be present"
        
        print(f"✓ Collection successful:")
        print(f"  CPU: {feature_vector.cpu_usage:.1f}%")
        print(f"  Memory: {feature_vector.memory_usage:.1f}%")
        print(f"  Processes: {feature_vector.process_count}")
        print(f"  Network: {feature_vector.network_connections}")
        print(f"  Failed Logins: {feature_vector.failed_logins}")
        
        # Verify logs were saved
        print("\n=== Verifying Storage ===")
        history_path = Path(test_dir) / "history.json"
        assert history_path.exists(), "History file should be created"
        
        with open(history_path, 'r') as f:
            history = json.load(f)
        
        assert isinstance(history, list), "History should be a list"
        assert len(history) > 0, "History should contain at least one entry"
        
        print(f"✓ Logs saved successfully ({len(history)} entries)")
        
        # Check if alert was generated (depends on anomaly score)
        alerts_path = Path(test_dir) / "alerts.json"
        if alerts_path.exists():
            with open(alerts_path, 'r') as f:
                alerts = json.load(f)
            print(f"✓ Alerts file created ({len(alerts)} alerts)")
        else:
            print("✓ No alerts generated (anomaly score below threshold)")
        
        # Verify attack graph was updated
        print("\n=== Verifying Attack Graph ===")
        assert len(collector.graph_engine.graph.nodes) > 0, "Graph should have nodes"
        
        # Export graph
        graph_path = Path(test_dir) / "attack_graph.json"
        success = collector.export_attack_graph(str(graph_path))
        assert success, "Graph export should succeed"
        assert graph_path.exists(), "Graph file should be created"
        
        with open(graph_path, 'r') as f:
            graph_data = json.load(f)
        
        assert 'nodes' in graph_data, "Graph should have nodes"
        assert 'edges' in graph_data, "Graph should have edges"
        assert 'metadata' in graph_data, "Graph should have metadata"
        
        print(f"✓ Attack graph updated:")
        print(f"  Nodes: {graph_data['metadata']['node_count']}")
        print(f"  Edges: {graph_data['metadata']['edge_count']}")
        
        # Test highest risk path
        print("\n=== Testing Risk Path Analysis ===")
        risk_path = collector.get_highest_risk_path()
        if risk_path:
            print(f"✓ Highest risk path found: {' -> '.join(risk_path)}")
        else:
            print("✓ No high-risk paths identified")
        
        print("\n=== Integration Test PASSED ===")
        return True
        
    except Exception as e:
        print(f"\n✗ Integration test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Clean up temporary directory
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
            print(f"\nCleaned up test directory: {test_dir}")


if __name__ == "__main__":
    import logging
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run test
    success = test_full_collection_pipeline()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
