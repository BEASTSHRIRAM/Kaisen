import axios from 'axios';
import { SystemMetrics, Alert, AttackGraph, SuspiciousIP, LogEntry } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Frontend-side fallback for the attack-graph filename mismatch found in the
 * 2026-10-24 audit (collector writes logs/attack_graph.json, the API read
 * logs/collected_graph.json). If /api/graph returns an empty graph but alerts
 * / suspicious IPs exist, derive a renderable graph from them client-side so
 * real data still shows up instead of a blank page. Derived nodes are built
 * only from real alert/IP records returned by the API.
 */
export function deriveGraphFromAlerts(alerts: Alert[], ips: SuspiciousIP[]): AttackGraph {
  const nodes: AttackGraph['nodes'] = [
    {
      id: 'local-host',
      type: 'machine',
      anomaly_score: alerts[0]?.anomaly_score ?? 0,
      risk_score: alerts[0]?.anomaly_score ?? 0,
      timestamp: alerts[0]?.timestamp ?? '',
      metadata: { label: alerts[0]?.node_id || 'local host', sub: 'monitored host' },
    },
  ];
  const edges: AttackGraph['edges'] = [];
  ips.slice(0, 6).forEach((ip) => {
    nodes.push({
      id: `ip-${ip.ip}`,
      type: 'external_ip',
      anomaly_score: ip.risk_score,
      risk_score: ip.risk_score,
      timestamp: ip.last_seen,
      metadata: { label: ip.ip, sub: `${ip.connection_count} connections` },
    });
    edges.push({ source: `ip-${ip.ip}`, target: 'local-host', type: 'ip_connection' });
  });
  return {
    nodes,
    edges,
    metadata: { generated_at: new Date().toISOString(), node_count: nodes.length, edge_count: edges.length },
  };
}

export const apiService = {
  async getLatestMetrics(): Promise<SystemMetrics> {
    const response = await api.get<SystemMetrics>('/api/metrics/latest');
    return response.data;
  },

  async getAlerts(params?: { severity?: string; limit?: number }): Promise<Alert[]> {
    const response = await api.get<Alert[]>('/api/alerts', { params });
    return response.data;
  },

  async getAttackGraph(): Promise<AttackGraph> {
    const response = await api.get<AttackGraph>('/api/graph');
    return response.data;
  },

  async getSuspiciousIPs(): Promise<SuspiciousIP[]> {
    const response = await api.get<SuspiciousIP[]>('/api/suspicious-ips');
    return response.data;
  },

  async getHistory(params?: { limit?: number }): Promise<LogEntry[]> {
    const response = await api.get<LogEntry[]>('/api/history', { params });
    return response.data;
  },
};

export default api;
