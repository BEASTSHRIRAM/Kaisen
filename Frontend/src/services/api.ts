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

export const apiService = {
  async getLatestMetrics(): Promise<SystemMetrics> {
    const response = await api.get<SystemMetrics>('/metrics/latest');
    return response.data;
  },

  async getAlerts(params?: { severity?: string; limit?: number }): Promise<Alert[]> {
    const response = await api.get<Alert[]>('/alerts', { params });
    return response.data;
  },

  async getAttackGraph(): Promise<AttackGraph> {
    const response = await api.get<AttackGraph>('/graph');
    return response.data;
  },

  async getSuspiciousIPs(): Promise<SuspiciousIP[]> {
    const response = await api.get<SuspiciousIP[]>('/suspicious-ips');
    return response.data;
  },

  async getHistory(params?: { limit?: number }): Promise<LogEntry[]> {
    const response = await api.get<LogEntry[]>('/history', { params });
    return response.data;
  },
};

export default api;
