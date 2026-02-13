// Mock data for development and testing
import { SystemMetrics, Alert, AttackGraph, SuspiciousIP, LogEntry } from '../types';

export const mockMetrics: SystemMetrics = {
  cpu_usage: 45.2,
  memory_usage: 62.8,
  process_count: 156,
  network_connections: 42,
  failed_logins: 2,
  unique_ip_count: 12,
  timestamp: new Date().toISOString(),
  node_id: 'local-machine',
  anomaly_score: 0.35,
};

export const mockAlerts: Alert[] = [
  {
    alert_id: '1',
    node_id: 'web-server-01',
    timestamp: new Date(Date.now() - 3600000).toISOString(),
    anomaly_score: 0.85,
    suspected_reason: 'High CPU usage, multiple failed logins',
    severity: 'high',
    suspicious_ips: ['203.0.113.45', '198.51.100.23'],
  },
  {
    alert_id: '2',
    node_id: 'db-server-01',
    timestamp: new Date(Date.now() - 7200000).toISOString(),
    anomaly_score: 0.72,
    suspected_reason: 'Excessive network connections',
    severity: 'medium',
    suspicious_ips: ['203.0.113.45'],
  },
];

export const mockGraph: AttackGraph = {
  nodes: [
    {
      id: 'machine-01',
      type: 'machine',
      anomaly_score: 0.85,
      risk_score: 0.85,
      timestamp: new Date().toISOString(),
    },
    {
      id: '203.0.113.45',
      type: 'external_ip',
      anomaly_score: 0.72,
      risk_score: 0.60,
      timestamp: new Date().toISOString(),
      metadata: {
        connection_count: 45,
        failed_attempts: 12,
      },
    },
    {
      id: 'process-ssh',
      type: 'process',
      anomaly_score: 0.45,
      risk_score: 0.50,
      timestamp: new Date().toISOString(),
    },
  ],
  edges: [
    {
      source: '203.0.113.45',
      target: 'machine-01',
      type: 'ip_connection',
    },
    {
      source: 'machine-01',
      target: 'process-ssh',
      type: 'process_spawn',
    },
  ],
  metadata: {
    generated_at: new Date().toISOString(),
    node_count: 3,
    edge_count: 2,
  },
};

export const mockSuspiciousIPs: SuspiciousIP[] = [
  {
    ip: '203.0.113.45',
    connection_count: 45,
    failed_attempts: 12,
    risk_score: 0.72,
    last_seen: new Date(Date.now() - 1800000).toISOString(),
    node_id: 'web-server-01',
  },
  {
    ip: '198.51.100.23',
    connection_count: 23,
    failed_attempts: 8,
    risk_score: 0.58,
    last_seen: new Date(Date.now() - 3600000).toISOString(),
    node_id: 'web-server-01',
  },
];

export const mockLogs: LogEntry[] = Array.from({ length: 20 }, (_, i) => ({
  timestamp: new Date(Date.now() - i * 300000).toISOString(),
  node_id: 'local-machine',
  cpu_usage: 40 + Math.random() * 30,
  memory_usage: 50 + Math.random() * 30,
  process_count: 150 + Math.floor(Math.random() * 50),
  network_connections: 30 + Math.floor(Math.random() * 30),
  failed_logins: Math.floor(Math.random() * 5),
}));
