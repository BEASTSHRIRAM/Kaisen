// API Response Types

export interface SystemMetrics {
  cpu_usage: number;
  memory_usage: number;
  process_count: number;
  network_connections: number;
  failed_logins: number;
  unique_ip_count: number;
  timestamp: string;
  node_id: string;
  anomaly_score?: number;
}

export interface Alert {
  alert_id: string;
  node_id: string;
  timestamp: string;
  anomaly_score: number;
  suspected_reason: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  suspicious_ips: string[];
  feature_vector?: SystemMetrics;
}

export interface GraphNode {
  id: string;
  type: 'machine' | 'process' | 'service' | 'remote_server' | 'external_ip';
  anomaly_score: number;
  risk_score: number;
  timestamp: string;
  metadata?: Record<string, any>;
}

export interface GraphEdge {
  source: string;
  target: string;
  type: 'network_connection' | 'process_spawn' | 'service_access' | 'ip_connection';
}

export interface AttackGraph {
  nodes: GraphNode[];
  edges: GraphEdge[];
  metadata: {
    generated_at: string;
    node_count: number;
    edge_count: number;
  };
}

export interface SuspiciousIP {
  ip: string;
  connection_count: number;
  failed_attempts: number;
  risk_score: number;
  last_seen: string;
  node_id?: string;
}

export interface LogEntry {
  timestamp: string;
  node_id: string;
  cpu_usage: number;
  memory_usage: number;
  process_count: number;
  network_connections: number;
  failed_logins: number;
}

export interface ConnectionStatus {
  connected: boolean;
  lastUpdate: Date | null;
  error: string | null;
}

// WebSocket Message Types
export interface WSMessage<T = any> {
  type: 'alert' | 'metrics' | 'graph_update';
  data: T;
  timestamp: string;
}
