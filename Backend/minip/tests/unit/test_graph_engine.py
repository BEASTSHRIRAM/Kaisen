"""
Unit tests for GraphEngine.

Tests cover:
- Initialization
- Node addition with type validation
- Edge addition with type validation
- Anomaly score updates
- IP node creation from feature vectors
- IP anomaly computation
- Risk propagation with decay
- Highest risk path finding
- JSON export
"""

import pytest
import sys
import os
import json

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from graph_engine import GraphEngine, NODE_TYPES, EDGE_TYPES
from data_models import FeatureVector


class TestGraphEngineInitialization:
    """Test GraphEngine initialization."""
    
    def test_init_creates_empty_graph(self):
        """Test that initialization creates an empty graph."""
        engine = GraphEngine()
        assert engine.graph is not None
        assert engine.graph.number_of_nodes() == 0
        assert engine.graph.number_of_edges() == 0


class TestAddNode:
    """Test add_node method."""
    
    def test_add_node_with_valid_type(self):
        """Test adding a node with a valid node type."""
        engine = GraphEngine()
        engine.add_node('node1', 'machine')
        
        assert 'node1' in engine.graph
        assert engine.graph.nodes['node1']['node_type'] == 'machine'
        assert engine.graph.nodes['node1']['anomaly_score'] == 0.0
        assert engine.graph.nodes['node1']['risk_score'] == 0.0
    
    def test_add_node_with_all_valid_types(self):
        """Test adding nodes with all valid node types."""
        engine = GraphEngine()
        
        for i, node_type in enumerate(NODE_TYPES):
            node_id = f'node{i}'
            engine.add_node(node_id, node_type)
            assert engine.graph.nodes[node_id]['node_type'] == node_type
    
    def test_add_node_with_invalid_type(self):
        """Test that adding a node with invalid type raises ValueError."""
        engine = GraphEngine()
        
        with pytest.raises(ValueError, match="Invalid node_type"):
            engine.add_node('node1', 'invalid_type')
    
    def test_add_node_with_attributes(self):
        """Test adding a node with custom attributes."""
        engine = GraphEngine()
        attrs = {
            'timestamp': '2024-01-15T10:30:00Z',
            'anomaly_score': 0.5,
            'metadata': {'key': 'value'}
        }
        
        engine.add_node('node1', 'machine', attrs)
        
        assert engine.graph.nodes['node1']['timestamp'] == '2024-01-15T10:30:00Z'
        assert engine.graph.nodes['node1']['anomaly_score'] == 0.5
        assert engine.graph.nodes['node1']['metadata'] == {'key': 'value'}
    
    def test_add_duplicate_node_updates_attributes(self):
        """Test that adding a duplicate node updates its attributes."""
        engine = GraphEngine()
        engine.add_node('node1', 'machine', {'anomaly_score': 0.3})
        engine.add_node('node1', 'machine', {'anomaly_score': 0.7})
        
        assert engine.graph.nodes['node1']['anomaly_score'] == 0.7


class TestAddEdge:
    """Test add_edge method."""
    
    def test_add_edge_with_valid_type(self):
        """Test adding an edge with a valid edge type."""
        engine = GraphEngine()
        engine.add_node('node1', 'machine')
        engine.add_node('node2', 'external_ip')
        
        engine.add_edge('node1', 'node2', 'ip_connection')
        
        assert engine.graph.has_edge('node1', 'node2')
        assert engine.graph.edges['node1', 'node2']['edge_type'] == 'ip_connection'
    
    def test_add_edge_with_all_valid_types(self):
        """Test adding edges with all valid edge types."""
        engine = GraphEngine()
        
        for i, edge_type in enumerate(EDGE_TYPES):
            source = f'source{i}'
            target = f'target{i}'
            engine.add_node(source, 'machine')
            engine.add_node(target, 'service')
            engine.add_edge(source, target, edge_type)
            
            assert engine.graph.edges[source, target]['edge_type'] == edge_type
    
    def test_add_edge_with_invalid_type(self):
        """Test that adding an edge with invalid type raises ValueError."""
        engine = GraphEngine()
        engine.add_node('node1', 'machine')
        engine.add_node('node2', 'service')
        
        with pytest.raises(ValueError, match="Invalid edge_type"):
            engine.add_edge('node1', 'node2', 'invalid_type')
    
    def test_add_edge_creates_nodes_if_not_exist(self):
        """Test that adding an edge creates nodes if they don't exist."""
        engine = GraphEngine()
        engine.add_edge('node1', 'node2', 'network_connection')
        
        # NetworkX creates nodes automatically
        assert 'node1' in engine.graph
        assert 'node2' in engine.graph


class TestUpdateAnomalyScore:
    """Test update_anomaly_score method."""
    
    def test_update_anomaly_score_for_existing_node(self):
        """Test updating anomaly score for an existing node."""
        engine = GraphEngine()
        engine.add_node('node1', 'machine')
        
        engine.update_anomaly_score('node1', 0.85)
        
        assert engine.graph.nodes['node1']['anomaly_score'] == 0.85
    
    def test_update_anomaly_score_for_nonexistent_node(self):
        """Test that updating score for nonexistent node raises KeyError."""
        engine = GraphEngine()
        
        with pytest.raises(KeyError, match="Node .* does not exist"):
            engine.update_anomaly_score('nonexistent', 0.5)
    
    def test_update_anomaly_score_multiple_times(self):
        """Test updating anomaly score multiple times."""
        engine = GraphEngine()
        engine.add_node('node1', 'machine')
        
        engine.update_anomaly_score('node1', 0.5)
        assert engine.graph.nodes['node1']['anomaly_score'] == 0.5
        
        engine.update_anomaly_score('node1', 0.9)
        assert engine.graph.nodes['node1']['anomaly_score'] == 0.9


class TestAddIpNodesFromFeatureVector:
    """Test add_ip_nodes_from_feature_vector method."""
    
    def test_add_ip_nodes_creates_machine_node(self):
        """Test that IP node creation also creates machine node if needed."""
        engine = GraphEngine()
        
        fv = FeatureVector(
            cpu_usage=50.0,
            memory_usage=60.0,
            process_count=100,
            network_connections=10,
            failed_logins=0,
            timestamp='2024-01-15T10:30:00Z',
            node_id='machine1',
            destination_ips=['192.168.1.1']
        )
        
        engine.add_ip_nodes_from_feature_vector(fv)
        
        assert 'machine1' in engine.graph
        assert engine.graph.nodes['machine1']['node_type'] == 'machine'
    
    def test_add_ip_nodes_creates_external_ip_nodes(self):
        """Test that external IP nodes are created."""
        engine = GraphEngine()
        
        fv = FeatureVector(
            cpu_usage=50.0,
            memory_usage=60.0,
            process_count=100,
            network_connections=10,
            failed_logins=0,
            timestamp='2024-01-15T10:30:00Z',
            node_id='machine1',
            source_ips=['10.0.0.1'],
            destination_ips=['192.168.1.1', '8.8.8.8']
        )
        
        engine.add_ip_nodes_from_feature_vector(fv)
        
        assert '10.0.0.1' in engine.graph
        assert '192.168.1.1' in engine.graph
        assert '8.8.8.8' in engine.graph
        assert engine.graph.nodes['192.168.1.1']['node_type'] == 'external_ip'
    
    def test_add_ip_nodes_creates_edges_to_destination_ips(self):
        """Test that edges are created from machine to destination IPs."""
        engine = GraphEngine()
        
        fv = FeatureVector(
            cpu_usage=50.0,
            memory_usage=60.0,
            process_count=100,
            network_connections=10,
            failed_logins=0,
            timestamp='2024-01-15T10:30:00Z',
            node_id='machine1',
            destination_ips=['192.168.1.1', '8.8.8.8']
        )
        
        engine.add_ip_nodes_from_feature_vector(fv)
        
        assert engine.graph.has_edge('machine1', '192.168.1.1')
        assert engine.graph.has_edge('machine1', '8.8.8.8')
        assert engine.graph.edges['machine1', '192.168.1.1']['edge_type'] == 'ip_connection'
    
    def test_add_ip_nodes_computes_anomaly_scores(self):
        """Test that anomaly scores are computed for IPs."""
        engine = GraphEngine()
        
        fv = FeatureVector(
            cpu_usage=50.0,
            memory_usage=60.0,
            process_count=100,
            network_connections=10,
            failed_logins=15,
            timestamp='2024-01-15T10:30:00Z',
            node_id='machine1',
            destination_ips=['192.168.1.1'],
            connection_count_per_ip={'192.168.1.1': 75},
            failed_attempts_per_ip={'192.168.1.1': 12}
        )
        
        engine.add_ip_nodes_from_feature_vector(fv)
        
        # IP should have elevated anomaly score due to high connections and failed attempts
        assert engine.graph.nodes['192.168.1.1']['anomaly_score'] > 0
    
    def test_add_ip_nodes_updates_metadata(self):
        """Test that IP node metadata is updated."""
        engine = GraphEngine()
        
        fv = FeatureVector(
            cpu_usage=50.0,
            memory_usage=60.0,
            process_count=100,
            network_connections=10,
            failed_logins=5,
            timestamp='2024-01-15T10:30:00Z',
            node_id='machine1',
            destination_ips=['192.168.1.1'],
            connection_count_per_ip={'192.168.1.1': 25},
            failed_attempts_per_ip={'192.168.1.1': 3}
        )
        
        engine.add_ip_nodes_from_feature_vector(fv)
        
        metadata = engine.graph.nodes['192.168.1.1']['metadata']
        assert metadata['connection_count'] == 25
        assert metadata['failed_attempts'] == 3
    
    def test_add_ip_nodes_handles_empty_ip_lists(self):
        """Test handling of feature vectors with no IPs."""
        engine = GraphEngine()
        
        fv = FeatureVector(
            cpu_usage=50.0,
            memory_usage=60.0,
            process_count=100,
            network_connections=0,
            failed_logins=0,
            timestamp='2024-01-15T10:30:00Z',
            node_id='machine1'
        )
        
        engine.add_ip_nodes_from_feature_vector(fv)
        
        # Should only have machine node
        assert 'machine1' in engine.graph
        assert engine.graph.number_of_nodes() == 1


class TestComputeIpAnomaly:
    """Test _compute_ip_anomaly method."""
    
    def test_low_connections_low_failures(self):
        """Test that low connections and failures result in low anomaly."""
        engine = GraphEngine()
        score = engine._compute_ip_anomaly(10, 2)
        assert score == 0.0
    
    def test_high_connections(self):
        """Test that high connection count increases anomaly score."""
        engine = GraphEngine()
        score = engine._compute_ip_anomaly(100, 0)
        assert score > 0
        assert score <= 0.5
    
    def test_high_failed_attempts(self):
        """Test that high failed attempts increase anomaly score."""
        engine = GraphEngine()
        score = engine._compute_ip_anomaly(0, 15)
        assert score > 0
        assert score <= 0.5
    
    def test_both_high_connections_and_failures(self):
        """Test that both high connections and failures result in high anomaly."""
        engine = GraphEngine()
        score = engine._compute_ip_anomaly(150, 20)
        assert score > 0.5
        assert score <= 1.0
    
    def test_anomaly_score_capped_at_one(self):
        """Test that anomaly score never exceeds 1.0."""
        engine = GraphEngine()
        score = engine._compute_ip_anomaly(1000, 100)
        assert score <= 1.0
    
    def test_connection_threshold_boundary(self):
        """Test behavior at connection count threshold (50)."""
        engine = GraphEngine()
        
        score_below = engine._compute_ip_anomaly(50, 0)
        score_above = engine._compute_ip_anomaly(51, 0)
        
        assert score_below == 0.0
        assert score_above > 0.0
    
    def test_failed_attempts_threshold_boundary(self):
        """Test behavior at failed attempts threshold (5)."""
        engine = GraphEngine()
        
        score_below = engine._compute_ip_anomaly(0, 5)
        score_above = engine._compute_ip_anomaly(0, 6)
        
        assert score_below == 0.0
        assert score_above > 0.0


class TestPropagateRisk:
    """Test propagate_risk method."""
    
    def test_propagate_risk_from_single_node(self):
        """Test risk propagation from a single high-anomaly node."""
        engine = GraphEngine()
        
        engine.add_node('node1', 'machine', {'anomaly_score': 0.9})
        engine.add_node('node2', 'service')
        engine.add_node('node3', 'external_ip')
        engine.add_edge('node1', 'node2', 'service_access')
        engine.add_edge('node2', 'node3', 'ip_connection')
        
        engine.propagate_risk(decay_factor=0.7)
        
        # node1 should have risk_score = anomaly_score
        assert engine.graph.nodes['node1']['risk_score'] == 0.9
        
        # node2 should have decayed risk (0.9 * 0.7)
        assert engine.graph.nodes['node2']['risk_score'] == pytest.approx(0.63, rel=0.01)
        
        # node3 should have further decayed risk (0.9 * 0.7^2)
        assert engine.graph.nodes['node3']['risk_score'] == pytest.approx(0.441, rel=0.01)
    
    def test_propagate_risk_with_multiple_sources(self):
        """Test risk propagation from multiple high-anomaly nodes."""
        engine = GraphEngine()
        
        engine.add_node('node1', 'machine', {'anomaly_score': 0.8})
        engine.add_node('node2', 'machine', {'anomaly_score': 0.6})
        engine.add_node('target', 'service')
        engine.add_edge('node1', 'target', 'service_access')
        engine.add_edge('node2', 'target', 'service_access')
        
        engine.propagate_risk(decay_factor=0.7)
        
        # Target should have max of propagated risks
        expected_risk = max(0.8 * 0.7, 0.6 * 0.7)
        assert engine.graph.nodes['target']['risk_score'] == pytest.approx(expected_risk, rel=0.01)
    
    def test_propagate_risk_no_high_anomaly_nodes(self):
        """Test that propagation does nothing when no nodes have anomaly scores."""
        engine = GraphEngine()
        
        engine.add_node('node1', 'machine')
        engine.add_node('node2', 'service')
        engine.add_edge('node1', 'node2', 'service_access')
        
        engine.propagate_risk()
        
        assert engine.graph.nodes['node1']['risk_score'] == 0.0
        assert engine.graph.nodes['node2']['risk_score'] == 0.0
    
    def test_propagate_risk_with_custom_decay_factor(self):
        """Test risk propagation with custom decay factor."""
        engine = GraphEngine()
        
        engine.add_node('node1', 'machine', {'anomaly_score': 1.0})
        engine.add_node('node2', 'service')
        engine.add_edge('node1', 'node2', 'service_access')
        
        engine.propagate_risk(decay_factor=0.5)
        
        assert engine.graph.nodes['node2']['risk_score'] == 0.5


class TestFindHighestRiskPath:
    """Test find_highest_risk_path method."""
    
    def test_find_path_from_remote_server_to_machine(self):
        """Test finding path from remote server to high-anomaly machine."""
        engine = GraphEngine()
        
        engine.add_node('remote1', 'remote_server', {'anomaly_score': 0.5})
        engine.add_node('machine1', 'machine', {'anomaly_score': 0.9, 'risk_score': 0.9})
        engine.add_edge('remote1', 'machine1', 'network_connection')
        
        engine.propagate_risk()
        path = engine.find_highest_risk_path()
        
        assert path == ['remote1', 'machine1']
    
    def test_find_path_prefers_higher_risk(self):
        """Test that higher risk path is preferred over lower risk path."""
        engine = GraphEngine()
        
        # Path 1: remote -> machine1 (high risk)
        engine.add_node('remote1', 'remote_server')
        engine.add_node('machine1', 'machine', {'anomaly_score': 0.9, 'risk_score': 0.9})
        engine.add_edge('remote1', 'machine1', 'network_connection')
        
        # Path 2: remote -> machine2 (low risk)
        engine.add_node('machine2', 'machine', {'anomaly_score': 0.75, 'risk_score': 0.75})
        engine.add_edge('remote1', 'machine2', 'network_connection')
        
        path = engine.find_highest_risk_path()
        
        assert 'machine1' in path
    
    def test_find_path_prefers_shorter_on_tie(self):
        """Test that shorter path is preferred when risk scores are equal."""
        engine = GraphEngine()
        
        # Short path: remote -> machine1
        engine.add_node('remote1', 'remote_server')
        engine.add_node('machine1', 'machine', {'anomaly_score': 0.8, 'risk_score': 0.8})
        engine.add_edge('remote1', 'machine1', 'network_connection')
        
        # Long path: remote -> service -> machine2 (same total risk)
        engine.add_node('service1', 'service', {'risk_score': 0.0})
        engine.add_node('machine2', 'machine', {'anomaly_score': 0.8, 'risk_score': 0.8})
        engine.add_edge('remote1', 'service1', 'service_access')
        engine.add_edge('service1', 'machine2', 'network_connection')
        
        path = engine.find_highest_risk_path()
        
        # Should prefer shorter path
        assert len(path) == 2
    
    def test_find_path_returns_empty_when_no_paths(self):
        """Test that empty list is returned when no paths exist."""
        engine = GraphEngine()
        
        # Disconnected nodes
        engine.add_node('remote1', 'remote_server')
        engine.add_node('machine1', 'machine', {'anomaly_score': 0.9})
        
        path = engine.find_highest_risk_path()
        
        assert path == []
    
    def test_find_path_with_external_ip_as_entry(self):
        """Test finding path starting from external IP."""
        engine = GraphEngine()
        
        engine.add_node('203.0.113.45', 'external_ip', {'anomaly_score': 0.8})
        engine.add_node('machine1', 'machine', {'anomaly_score': 0.9, 'risk_score': 0.9})
        engine.add_edge('203.0.113.45', 'machine1', 'ip_connection')
        
        engine.propagate_risk()
        path = engine.find_highest_risk_path()
        
        assert '203.0.113.45' in path
        assert 'machine1' in path


class TestExportJson:
    """Test export_json method."""
    
    def test_export_empty_graph(self):
        """Test exporting an empty graph."""
        engine = GraphEngine()
        
        json_str = engine.export_json()
        data = json.loads(json_str)
        
        assert 'nodes' in data
        assert 'edges' in data
        assert 'metadata' in data
        assert len(data['nodes']) == 0
        assert len(data['edges']) == 0
        assert data['metadata']['node_count'] == 0
        assert data['metadata']['edge_count'] == 0
    
    def test_export_graph_with_nodes(self):
        """Test exporting graph with nodes."""
        engine = GraphEngine()
        
        engine.add_node('node1', 'machine', {
            'anomaly_score': 0.85,
            'risk_score': 0.75,
            'timestamp': '2024-01-15T10:30:00Z'
        })
        engine.add_node('node2', 'external_ip', {
            'anomaly_score': 0.6,
            'risk_score': 0.5,
            'timestamp': '2024-01-15T10:30:00Z',
            'metadata': {'connection_count': 50}
        })
        
        json_str = engine.export_json()
        data = json.loads(json_str)
        
        assert len(data['nodes']) == 2
        assert data['metadata']['node_count'] == 2
        
        # Check node data
        node1 = next(n for n in data['nodes'] if n['id'] == 'node1')
        assert node1['type'] == 'machine'
        assert node1['anomaly_score'] == 0.85
        assert node1['risk_score'] == 0.75
    
    def test_export_graph_with_edges(self):
        """Test exporting graph with edges."""
        engine = GraphEngine()
        
        engine.add_node('node1', 'machine')
        engine.add_node('node2', 'external_ip')
        engine.add_edge('node1', 'node2', 'ip_connection')
        
        json_str = engine.export_json()
        data = json.loads(json_str)
        
        assert len(data['edges']) == 1
        assert data['metadata']['edge_count'] == 1
        
        edge = data['edges'][0]
        assert edge['source'] == 'node1'
        assert edge['target'] == 'node2'
        assert edge['type'] == 'ip_connection'
    
    def test_export_json_is_valid(self):
        """Test that exported JSON is valid and parseable."""
        engine = GraphEngine()
        
        engine.add_node('node1', 'machine')
        engine.add_node('node2', 'service')
        engine.add_edge('node1', 'node2', 'service_access')
        
        json_str = engine.export_json()
        
        # Should not raise exception
        data = json.loads(json_str)
        assert isinstance(data, dict)
    
    def test_export_includes_metadata_timestamp(self):
        """Test that export includes generated_at timestamp."""
        engine = GraphEngine()
        engine.add_node('node1', 'machine')
        
        json_str = engine.export_json()
        data = json.loads(json_str)
        
        assert 'generated_at' in data['metadata']
        assert 'Z' in data['metadata']['generated_at']  # ISO 8601 format
