import { useState, useEffect } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
  Box,
  Drawer,
  AppBar,
  Toolbar,
  List,
  Typography,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Chip,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Warning as WarningIcon,
  AccountTree as GraphIcon,
  Security as SecurityIcon,
  Description as LogsIcon,
} from '@mui/icons-material';
import { useStore } from '../store/useStore';
import { apiService } from '../services/api';
import { wsService } from '../services/websocket';

const drawerWidth = 240;

const menuItems = [
  { text: 'Dashboard', icon: <DashboardIcon />, path: '/app/dashboard' },
  { text: 'Alerts', icon: <WarningIcon />, path: '/app/alerts' },
  { text: 'Attack Graph', icon: <GraphIcon />, path: '/app/attack-graph' },
  { text: 'Suspicious IPs', icon: <SecurityIcon />, path: '/app/suspicious-ips' },
  { text: 'Logs', icon: <LogsIcon />, path: '/app/logs' },
];

export default function Layout() {
  const navigate = useNavigate();
  const location = useLocation();
  const { connectionStatus, setConnectionStatus, addAlert, setCurrentMetrics, addMetricsToHistory } = useStore();

  useEffect(() => {
    // Initialize WebSocket connections
    const WS_BASE_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';
    
    wsService.connect(`${WS_BASE_URL}/ws/alerts`);
    wsService.subscribe('alert', (alert) => {
      addAlert(alert);
    });

    wsService.subscribe('metrics', (metrics) => {
      setCurrentMetrics(metrics);
      addMetricsToHistory(metrics);
      setConnectionStatus({ connected: true, lastUpdate: new Date(), error: null });
    });

    // Fetch initial data
    const fetchInitialData = async () => {
      try {
        const [metrics, alerts, graph, ips, logs] = await Promise.all([
          apiService.getLatestMetrics(),
          apiService.getAlerts(),
          apiService.getAttackGraph(),
          apiService.getSuspiciousIPs(),
          apiService.getHistory({ limit: 100 }),
        ]);

        useStore.setState({
          currentMetrics: metrics,
          alerts,
          attackGraph: graph,
          suspiciousIPs: ips,
          logs,
        });

        setConnectionStatus({ connected: true, lastUpdate: new Date(), error: null });
      } catch (error) {
        console.error('Failed to fetch initial data:', error);
        setConnectionStatus({ connected: false, error: 'Failed to connect to backend' });
      }
    };

    fetchInitialData();

    // Polling fallback
    const interval = setInterval(async () => {
      try {
        const metrics = await apiService.getLatestMetrics();
        setCurrentMetrics(metrics);
        addMetricsToHistory(metrics);
        setConnectionStatus({ connected: true, lastUpdate: new Date(), error: null });
      } catch (error) {
        setConnectionStatus({ connected: false, error: 'Connection lost' });
      }
    }, 10000);

    return () => {
      clearInterval(interval);
      wsService.disconnect();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <Box sx={{ display: 'flex', height: '100vh' }}>
      <AppBar
        position="fixed"
        sx={{
          width: `calc(100% - ${drawerWidth}px)`,
          ml: `${drawerWidth}px`,
          bgcolor: 'background.paper',
          borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
        }}
        elevation={0}
      >
        <Toolbar>
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            Kaisen Security Monitor
          </Typography>
          <Chip
            label={connectionStatus.connected ? 'Connected' : 'Disconnected'}
            color={connectionStatus.connected ? 'success' : 'error'}
            size="small"
            sx={{ mr: 2 }}
          />
          {connectionStatus.lastUpdate && (
            <Typography variant="caption" color="text.secondary">
              Last update: {connectionStatus.lastUpdate.toLocaleTimeString()}
            </Typography>
          )}
        </Toolbar>
      </AppBar>

      <Drawer
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: drawerWidth,
            boxSizing: 'border-box',
            bgcolor: 'background.paper',
            borderRight: '1px solid rgba(255, 255, 255, 0.1)',
          },
        }}
        variant="permanent"
        anchor="left"
      >
        <Toolbar sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', py: 2 }}>
          <SecurityIcon sx={{ fontSize: 40, color: 'primary.main', mr: 1 }} />
          <Typography variant="h5" sx={{ fontWeight: 700, color: 'primary.main' }}>
            KAISEN
          </Typography>
        </Toolbar>
        <List>
          {menuItems.map((item) => (
            <ListItem key={item.text} disablePadding>
              <ListItemButton
                selected={location.pathname === item.path}
                onClick={() => navigate(item.path)}
                sx={{
                  '&.Mui-selected': {
                    bgcolor: 'rgba(0, 212, 255, 0.1)',
                    borderRight: '3px solid',
                    borderColor: 'primary.main',
                  },
                }}
              >
                <ListItemIcon sx={{ color: location.pathname === item.path ? 'primary.main' : 'inherit' }}>
                  {item.icon}
                </ListItemIcon>
                <ListItemText primary={item.text} />
              </ListItemButton>
            </ListItem>
          ))}
        </List>
      </Drawer>

      <Box
        component="main"
        sx={{
          flexGrow: 1,
          bgcolor: 'background.default',
          p: 3,
          mt: 8,
          overflow: 'auto',
        }}
      >
        <Outlet />
      </Box>
    </Box>
  );
}
