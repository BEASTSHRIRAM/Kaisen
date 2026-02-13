import { create } from 'zustand';
import {
  SystemMetrics,
  Alert,
  AttackGraph,
  SuspiciousIP,
  LogEntry,
  ConnectionStatus,
} from '../types';

interface AppState {
  // State
  currentMetrics: SystemMetrics | null;
  metricsHistory: SystemMetrics[];
  alerts: Alert[];
  attackGraph: AttackGraph | null;
  suspiciousIPs: SuspiciousIP[];
  logs: LogEntry[];
  connectionStatus: ConnectionStatus;

  // Actions
  setCurrentMetrics: (metrics: SystemMetrics) => void;
  addMetricsToHistory: (metrics: SystemMetrics) => void;
  addAlert: (alert: Alert) => void;
  setAlerts: (alerts: Alert[]) => void;
  setAttackGraph: (graph: AttackGraph) => void;
  setSuspiciousIPs: (ips: SuspiciousIP[]) => void;
  setLogs: (logs: LogEntry[]) => void;
  setConnectionStatus: (status: Partial<ConnectionStatus>) => void;
}

export const useStore = create<AppState>((set) => ({
  // Initial state
  currentMetrics: null,
  metricsHistory: [],
  alerts: [],
  attackGraph: null,
  suspiciousIPs: [],
  logs: [],
  connectionStatus: {
    connected: false,
    lastUpdate: null,
    error: null,
  },

  // Actions
  setCurrentMetrics: (metrics) =>
    set({ currentMetrics: metrics }),

  addMetricsToHistory: (metrics) =>
    set((state) => ({
      metricsHistory: [...state.metricsHistory.slice(-99), metrics],
    })),

  addAlert: (alert) =>
    set((state) => ({
      alerts: [alert, ...state.alerts],
    })),

  setAlerts: (alerts) =>
    set({ alerts }),

  setAttackGraph: (graph) =>
    set({ attackGraph: graph }),

  setSuspiciousIPs: (ips) =>
    set({ suspiciousIPs: ips }),

  setLogs: (logs) =>
    set({ logs }),

  setConnectionStatus: (status) =>
    set((state) => ({
      connectionStatus: { ...state.connectionStatus, ...status },
    })),
}));