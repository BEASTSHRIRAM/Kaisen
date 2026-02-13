"""
Graph Engine for Attack Graph Modeling and Analysis.

This module implements the GraphEngine class which builds and analyzes attack graphs
using NetworkX. It models relationships between machines, processes, services, and
external IP addresses to identify potential attack paths and propagate risk scores.
"""

import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from collections import deque
import networkx as nx
from src.data_models import FeatureVector
from src.error_handler import handle_warning, handle_recoverable_error, log_error, ErrorCategory


# Configure logging
logger = logging.getLogger(__name__)


# Supported node types
NODE_TYPES = ['machine', 'process', 'service', 'remote_server', 'external_ip']

# Supported edge types
EDGE_TYPES = ['network_connection', 'process_spawn', 'service_access', 'ip_connection']


class GraphEngine:
    """
    Attack graph modeling and analysis engine.
    
    This class builds directed graphs representing relationships between machines,
    processes, services, and external IP addresses. It supports anomaly score
    assignment, risk propagation, and attack path analysis.
    
    Attributes:
        graph: NetworkX DiGraph representing the attack graph
    """
    
    def __init__(self):
        """Initialize an empty attack graph."""
        self.graph = nx.DiGraph()
        logger.info("GraphEngine initialized with empty graph")
    
    def add_node(self, node_id: str, node_type: str, attributes: Optional[Dict[str, Any]] = None) -> None:
        """
        Add a node to the attack graph with type validation.
        
        Args:
            node_id: Unique identifier for the node
            node_type: Type of node (must be in NODE_TYPES)
            attributes: Optional dictionary of node attributes
            
        Raises:
            ValueError: If node_type is not in NODE_TYPES
        
        Requirements:
            - 10.2: Continue operation after non-critical errors
        """
        try:
            if node_type not in NODE_TYPES:
                raise ValueError(f"Invalid node_type '{node_type}'. Must be one of {NODE_TYPES}")
            
            # Initialize default attributes
            node_attrs = {
                'node_id': node_id,
                'node_type': node_type,
                'anomaly_score': 0.0,
                'risk_score': 0.0,
                'metadata': {}
            }
            
            # Merge with provided attributes
            if attributes:
                node_attrs.update(attributes)
            
            self.graph.add_node(node_id, **node_attrs)
            logger.debug(f"Added node {node_id} with type {node_type}")
        except ValueError as e:
            # RECOVERABLE ERROR: Invalid node type
            handle_warning("GraphEngine", str(e))
            raise
        except Exception as e:
            # RECOVERABLE ERROR: Unexpected error adding node
            handle_recoverable_error(
                "GraphEngine",
                f"Failed to add node {node_id}: {str(e)}",
                e
            )
            raise
    
    def add_edge(self, source: str, target: str, edge_type: str) -> None:
        """
        Add an edge to the attack graph with type validation.
        
        Args:
            source: Source node ID
            target: Target node ID
            edge_type: Type of edge (must be in EDGE_TYPES)
            
        Raises:
            ValueError: If edge_type is not in EDGE_TYPES
        """
        if edge_type not in EDGE_TYPES:
            raise ValueError(f"Invalid edge_type '{edge_type}'. Must be one of {EDGE_TYPES}")
        
        self.graph.add_edge(source, target, edge_type=edge_type)
        logger.debug(f"Added edge {source} -> {target} with type {edge_type}")
    
    def update_anomaly_score(self, node_id: str, score: float) -> None:
        """
        Update the anomaly score for a node.
        
        Args:
            node_id: Node identifier
            score: Anomaly score (0-1)
            
        Raises:
            KeyError: If node_id does not exist in the graph
        """
        if node_id not in self.graph:
            raise KeyError(f"Node {node_id} does not exist in graph")
        
        self.graph.nodes[node_id]['anomaly_score'] = score
        logger.debug(f"Updated anomaly score for {node_id}: {score}")
    
    def add_ip_nodes_from_feature_vector(self, fv: FeatureVector) -> None:
        """
        Create external IP nodes and edges from a feature vector.
        
        This method extracts IP addresses from the feature vector, creates nodes
        for external IPs, computes their anomaly scores based on behavior patterns,
        and creates edges from the machine to destination IPs.
        
        Args:
            fv: FeatureVector containing IP address information
        
        Requirements:
            - 10.2: Continue operation after non-critical errors
            - 14.12: Continue with empty IP lists if extraction fails
        """
        try:
            # Ensure the machine node exists
            if fv.node_id not in self.graph:
                try:
                    self.add_node(
                        fv.node_id,
                        'machine',
                        {
                            'timestamp': fv.timestamp,
                            'anomaly_score': 0.0,
                            'risk_score': 0.0
                        }
                    )
                except Exception as e:
                    handle_recoverable_error(
                        "GraphEngine",
                        f"Failed to create machine node {fv.node_id}: {str(e)}",
                        e
                    )
                    return
            
            # Get all unique IPs
            try:
                all_ips = set(fv.source_ips + fv.destination_ips)
            except Exception as e:
                handle_warning(
                    "GraphEngine",
                    f"Failed to extract IPs from feature vector: {str(e)}"
                )
                all_ips = set()
            
            # Add external IP nodes
            for ip in all_ips:
                try:
                    if ip not in self.graph:
                        self.graph.add_node(
                            ip,
                            node_id=ip,
                            node_type='external_ip',
                            anomaly_score=0.0,
                            risk_score=0.0,
                            timestamp=fv.timestamp,
                            metadata={
                                'connection_count': fv.connection_count_per_ip.get(ip, 0),
                                'failed_attempts': fv.failed_attempts_per_ip.get(ip, 0)
                            }
                        )
                        logger.debug(f"Created external_ip node for {ip}")
                    
                    # Update anomaly score based on behavior
                    try:
                        anomaly_contribution = self._compute_ip_anomaly(
                            fv.connection_count_per_ip.get(ip, 0),
                            fv.failed_attempts_per_ip.get(ip, 0)
                        )
                        
                        current_score = self.graph.nodes[ip].get('anomaly_score', 0.0)
                        self.graph.nodes[ip]['anomaly_score'] = max(current_score, anomaly_contribution)
                        
                        # Update metadata
                        self.graph.nodes[ip]['metadata'] = {
                            'connection_count': fv.connection_count_per_ip.get(ip, 0),
                            'failed_attempts': fv.failed_attempts_per_ip.get(ip, 0)
                        }
                    except Exception as e:
                        handle_warning(
                            "GraphEngine",
                            f"Failed to update anomaly score for IP {ip}: {str(e)}"
                        )
                except Exception as e:
                    handle_warning(
                        "GraphEngine",
                        f"Failed to process IP node {ip}: {str(e)}"
                    )
                    continue
            
            # Add edges from machine to destination IPs
            for dest_ip in fv.destination_ips:
                try:
                    if not self.graph.has_edge(fv.node_id, dest_ip):
                        self.graph.add_edge(fv.node_id, dest_ip, edge_type='ip_connection')
                        logger.debug(f"Created ip_connection edge: {fv.node_id} -> {dest_ip}")
                except Exception as e:
                    handle_warning(
                        "GraphEngine",
                        f"Failed to create edge to {dest_ip}: {str(e)}"
                    )
                    continue
        except Exception as e:
            # RECOVERABLE ERROR: Unexpected error processing feature vector
            handle_recoverable_error(
                "GraphEngine",
                f"Unexpected error in add_ip_nodes_from_feature_vector: {str(e)}",
                e
            )
    
    def _compute_ip_anomaly(self, connection_count: int, failed_attempts: int) -> float:
        """
        Compute anomaly score for an IP based on behavior patterns.
        
        High connection counts or failed login attempts indicate suspicious activity.
        
        Args:
            connection_count: Number of connections from/to this IP
            failed_attempts: Number of failed login attempts from this IP
            
        Returns:
            Anomaly score between 0 and 1
        """
        anomaly = 0.0
        
        # High connection count threshold (>50 connections)
        if connection_count > 50:
            anomaly += min(0.5, connection_count / 200.0)
        
        # Failed attempts threshold (>5 attempts)
        if failed_attempts > 5:
            anomaly += min(0.5, failed_attempts / 20.0)
        
        return min(1.0, anomaly)
    
    def propagate_risk(self, decay_factor: float = 0.7) -> None:
        """
        Propagate risk scores from high-anomaly nodes to connected nodes.
        
        Uses breadth-first search (BFS) with a decay factor applied at each hop.
        Risk scores are propagated from nodes with anomaly_score > 0 to their
        successors in the graph.
        
        Args:
            decay_factor: Multiplicative decay factor per hop (default: 0.7)
        """
        # Find nodes with anomaly scores > 0
        high_risk_nodes = [
            n for n, attrs in self.graph.nodes(data=True)
            if attrs.get('anomaly_score', 0.0) > 0
        ]
        
        logger.debug(f"Propagating risk from {len(high_risk_nodes)} high-risk nodes")
        
        for source in high_risk_nodes:
            # BFS traversal
            visited = {source}
            queue = deque([(source, self.graph.nodes[source]['anomaly_score'], 0)])
            
            while queue:
                node, risk, depth = queue.popleft()
                
                # Update risk score with decay
                current_risk = self.graph.nodes[node].get('risk_score', 0.0)
                propagated_risk = risk * (decay_factor ** depth)
                self.graph.nodes[node]['risk_score'] = max(
                    current_risk,
                    propagated_risk
                )
                
                # Add neighbors to queue
                for neighbor in self.graph.successors(node):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append((neighbor, risk, depth + 1))
        
        logger.info("Risk propagation completed")
    
    def find_highest_risk_path(self) -> List[str]:
        """
        Find the attack path with the highest cumulative risk score.
        
        Searches for paths from entry points (remote_server nodes) to high-value
        targets (machine nodes with high anomaly scores). Returns the path with
        the highest cumulative risk score, preferring shorter paths in case of ties.
        
        Returns:
            List of node IDs representing the highest-risk path (empty if no paths found)
        """
        # Find entry points (remote servers or external IPs with high anomaly)
        entry_points = [
            n for n, attrs in self.graph.nodes(data=True)
            if attrs.get('node_type') in ['remote_server', 'external_ip']
        ]
        
        # Find targets (machines with high anomaly scores)
        targets = [
            n for n, attrs in self.graph.nodes(data=True)
            if attrs.get('node_type') == 'machine'
            and attrs.get('anomaly_score', 0.0) > 0.7
        ]
        
        # If no clear entry points, use all nodes with high anomaly as potential starts
        if not entry_points:
            entry_points = [
                n for n, attrs in self.graph.nodes(data=True)
                if attrs.get('anomaly_score', 0.0) > 0.5
            ]
        
        # If no clear targets, use all nodes with some anomaly
        if not targets:
            targets = [
                n for n, attrs in self.graph.nodes(data=True)
                if attrs.get('anomaly_score', 0.0) > 0
            ]
        
        best_path = []
        best_score = 0.0
        
        for entry in entry_points:
            for target in targets:
                if entry == target:
                    continue
                
                if nx.has_path(self.graph, entry, target):
                    # Find all simple paths (no cycles)
                    try:
                        paths = list(nx.all_simple_paths(self.graph, entry, target, cutoff=10))
                        
                        for path in paths:
                            # Calculate cumulative risk score
                            score = sum(
                                self.graph.nodes[n].get('risk_score', 0.0)
                                for n in path
                            )
                            
                            # Update best path (prefer higher score, then shorter path)
                            if score > best_score or (score == best_score and len(path) < len(best_path)):
                                best_score = score
                                best_path = path
                    except nx.NetworkXNoPath:
                        continue
        
        logger.info(f"Found highest risk path with score {best_score}: {best_path}")
        return best_path
    
    def export_json(self) -> str:
        """
        Export the attack graph to JSON format.
        
        Returns:
            JSON string representation of the graph including nodes, edges, and metadata
        """
        from datetime import datetime, timezone
        
        # Build nodes list
        nodes = []
        for node_id, attrs in self.graph.nodes(data=True):
            node_data = {
                'id': node_id,
                'type': attrs.get('node_type', 'unknown'),
                'anomaly_score': attrs.get('anomaly_score', 0.0),
                'risk_score': attrs.get('risk_score', 0.0),
                'timestamp': attrs.get('timestamp', ''),
            }
            
            # Include metadata if present
            if 'metadata' in attrs and attrs['metadata']:
                node_data['metadata'] = attrs['metadata']
            
            nodes.append(node_data)
        
        # Build edges list
        edges = []
        for source, target, attrs in self.graph.edges(data=True):
            edge_data = {
                'source': source,
                'target': target,
                'type': attrs.get('edge_type', 'unknown')
            }
            edges.append(edge_data)
        
        # Build complete graph structure
        graph_data = {
            'nodes': nodes,
            'edges': edges,
            'metadata': {
                'generated_at': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'node_count': len(nodes),
                'edge_count': len(edges)
            }
        }
        
        return json.dumps(graph_data, indent=2)
