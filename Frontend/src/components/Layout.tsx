import { useEffect } from 'react';
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
  IconButton,
} from '@mui/material';
import {
  Radar,
  Siren,
  Bot,
  Wrench,
  Brain,
  LayoutDashboard,
  Bell,
  Network,
  Shield,
  ScrollText,
  Crown,
  CreditCard,
  Settings,
  Globe2,
  FlaskConical,
  Server,
  FileText,
  LogOut,
} from 'lucide-react';
import { useStore } from '../store/useStore';
import { apiService, deriveGraphFromAlerts } from '../services/api';
import { useCockpit } from '../unified/cockpitStore';
import { useAuth, PLAN_LABEL } from '../unified/authStore';
import { DemoBanner, ScenarioControls, Tag } from '../unified/ui';
import { LogoLockup } from '../unified/Logo';
import { ACCENT } from '../theme';

const drawerWidth = 232;
const ICON_SIZE = 17;

const sections: { label: string; items: { text: string; icon: React.ReactNode; path: string }[] }[] = [
  {
    label: 'Overview',
    items: [
      { text: 'Command Center', icon: <Radar size={ICON_SIZE} />, path: '/app/command' },
      { text: 'Incidents', icon: <Siren size={ICON_SIZE} />, path: '/app/incidents' },
      { text: 'Attack Graph', icon: <Network size={ICON_SIZE} />, path: '/app/attack-graph' },
    ],
  },
  {
    label: 'Agent',
    items: [
      { text: 'Agent Cockpit', icon: <Bot size={ICON_SIZE} />, path: '/app/cockpit' },
      { text: 'Tool Registry', icon: <Wrench size={ICON_SIZE} />, path: '/app/tools' },
      { text: 'Memory Inspector', icon: <Brain size={ICON_SIZE} />, path: '/app/memory' },
    ],
  },
  {
    label: 'Platform',
    items: [
      { text: 'Fleet — Servers', icon: <Server size={ICON_SIZE} />, path: '/app/fleet' },
      { text: 'Attack Lab', icon: <FlaskConical size={ICON_SIZE} />, path: '/app/lab' },
      { text: 'Threat Intel', icon: <Globe2 size={ICON_SIZE} />, path: '/app/threat-intel' },
      { text: 'Audit & Compliance', icon: <ScrollText size={ICON_SIZE} />, path: '/app/audit' },
    ],
  },
  {
    label: 'Account',
    items: [
      { text: 'Plans', icon: <Crown size={ICON_SIZE} />, path: '/app/plans' },
      { text: 'Billing & Usage', icon: <CreditCard size={ICON_SIZE} />, path: '/app/billing' },
      { text: 'Settings', icon: <Settings size={ICON_SIZE} />, path: '/app/settings' },
    ],
  },
  {
    label: 'Host monitors (original)',
    items: [
      { text: 'Host Dashboard', icon: <LayoutDashboard size={ICON_SIZE} />, path: '/app/dashboard' },
      { text: 'Alerts', icon: <Bell size={ICON_SIZE} />, path: '/app/alerts' },
      { text: 'Suspicious IPs', icon: <Shield size={ICON_SIZE} />, path: '/app/suspicious-ips' },
      { text: 'Logs', icon: <FileText size={ICON_SIZE} />, path: '/app/logs' },
    ],
  },
];

export default function Layout() {
  const navigate = useNavigate();
  const location = useLocation();
  const { connectionStatus, setConnectionStatus, setCurrentMetrics, addMetricsToHistory } = useStore();
  const demoActive = useCockpit((s) => s.demoActive);
  const playing = useCockpit((s) => s.playing);
  const tick = useCockpit((s) => s.tick);
  const { user, plan, onboarded, serverName, signOut } = useAuth();

  // Journey guard: Login → Plans → Setup → app. Anyone landing in the app
  // without finishing the earlier steps is sent back to the right one.
  useEffect(() => {
    if (!user) navigate('/login', { replace: true });
    else if (!plan) navigate('/welcome/plans', { replace: true });
    else if (!onboarded) navigate('/welcome/setup', { replace: true });
  }, [user, plan, onboarded, navigate]);

  // Global scenario-replay engine: advances everywhere, on every page.
  useEffect(() => {
    if (!playing) return;
    const id = setInterval(tick, 1600);
    return () => clearInterval(id);
  }, [playing, tick]);

  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        const [metrics, alerts, graph, ips, logs] = await Promise.all([
          apiService.getLatestMetrics(),
          apiService.getAlerts(),
          apiService.getAttackGraph(),
          apiService.getSuspiciousIPs(),
          apiService.getHistory({ limit: 100 }),
        ]);

        // Attack-graph filename-mismatch fallback (frontend side): if the
        // API graph is empty but real alerts/IPs exist, derive a graph.
        const usableGraph =
          graph && graph.nodes && graph.nodes.length > 0
            ? graph
            : ips.length > 0
              ? deriveGraphFromAlerts(alerts, ips)
              : graph;

        useStore.setState({
          currentMetrics: metrics,
          alerts,
          attackGraph: usableGraph,
          suspiciousIPs: ips,
          logs,
        });
        setConnectionStatus({ connected: true, lastUpdate: new Date(), error: null });
      } catch {
        setConnectionStatus({ connected: false, error: 'Failed to connect to backend' });
      }
    };

    fetchInitialData();

    // Polling for live metrics (the frontend's WebSocket client is
    // protocol-incompatible with the backend's Socket.IO — audit, 24 Oct —
    // so polling remains the honest live path).
    const interval = setInterval(async () => {
      try {
        const metrics = await apiService.getLatestMetrics();
        setCurrentMetrics(metrics);
        addMetricsToHistory(metrics);
        setConnectionStatus({ connected: true, lastUpdate: new Date(), error: null });
      } catch {
        setConnectionStatus({ connected: false, error: 'Connection lost' });
      }
    }, 2000);

    return () => clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const initials = (user?.name || 'K')
    .split(' ')
    .map((w) => w[0])
    .slice(0, 2)
    .join('')
    .toUpperCase();

  return (
    <Box sx={{ display: 'flex', height: '100vh', bgcolor: 'background.default' }}>
      <Drawer
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: drawerWidth,
            boxSizing: 'border-box',
            bgcolor: '#060D12',
            borderRight: '1px solid rgba(255,255,255,0.08)',
            display: 'flex',
            flexDirection: 'column',
          },
        }}
        variant="permanent"
        anchor="left"
      >
        <Box sx={{ px: 2.25, pt: 2.5, pb: 1.5 }}>
          <LogoLockup size={30} stacked />
          <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1.5, lineHeight: 1.45 }}>
            Security for businesses running AI agents on their own servers.
          </Typography>
        </Box>

        {sections.map((section) => (
          <Box key={section.label} sx={{ px: 1.25, mt: 1 }}>
            <Typography variant="caption" sx={{ px: 1, textTransform: 'uppercase', letterSpacing: '0.13em', color: 'text.secondary', fontWeight: 650, fontSize: '0.62rem' }}>
              {section.label}
            </Typography>
            <List dense sx={{ pt: 0.5 }}>
              {section.items.map((item) => {
                const active = location.pathname === item.path;
                return (
                  <ListItem key={item.text} disablePadding sx={{ mb: 0.25 }}>
                    <ListItemButton
                      selected={active}
                      onClick={() => navigate(item.path)}
                      sx={{
                        borderRadius: '8px',
                        py: 0.7,
                        '&.Mui-selected': { bgcolor: 'rgba(2,151,222,0.1)' },
                        '&.Mui-selected:hover': { bgcolor: 'rgba(2,151,222,0.15)' },
                      }}
                    >
                      <ListItemIcon sx={{ minWidth: 32, color: active ? ACCENT : '#7E93A1' }}>
                        {item.icon}
                      </ListItemIcon>
                      <ListItemText
                        primary={item.text}
                        primaryTypographyProps={{ fontSize: '0.85rem', fontWeight: active ? 620 : 450, color: active ? 'text.primary' : 'text.secondary' }}
                      />
                    </ListItemButton>
                  </ListItem>
                );
              })}
            </List>
          </Box>
        ))}

        <Box sx={{ mt: 'auto', p: 1.75 }}>
          {plan === 'free' && (
            <Box sx={{ p: 1.5, mb: 1.25, borderRadius: '10px', border: '1px solid rgba(2,151,222,0.35)', bgcolor: 'rgba(2,151,222,0.06)' }}>
              <Typography variant="caption" sx={{ fontWeight: 650, display: 'block' }}>You're on Free</Typography>
              <Typography variant="caption" color="text.secondary">
                Cockpit feeds, compliance exports and Slack alerts are Pro.
              </Typography>
              <Typography
                variant="caption"
                sx={{ color: 'primary.main', fontWeight: 650, cursor: 'pointer', display: 'block', mt: 0.75 }}
                onClick={() => navigate('/app/plans')}
              >
                Compare plans →
              </Typography>
            </Box>
          )}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.25, p: 1.25, borderRadius: '10px', border: '1px solid rgba(255,255,255,0.08)', bgcolor: 'rgba(255,255,255,0.02)' }}>
            <Box sx={{ width: 32, height: 32, borderRadius: '50%', bgcolor: 'rgba(2,151,222,0.14)', color: ACCENT, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.72rem', fontWeight: 700, flexShrink: 0 }}>
              {initials}
            </Box>
            <Box sx={{ minWidth: 0, flex: 1 }}>
              <Typography variant="caption" sx={{ fontWeight: 650, display: 'block', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                {user?.name || 'Operator'}
              </Typography>
              <Typography variant="caption" color="text.secondary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                <Server size={11} /> {serverName || 'vps-blr-01'} · {plan ? PLAN_LABEL[plan].split('·')[0].trim() : '—'}
              </Typography>
            </Box>
            <IconButton
              size="small"
              title="Sign out (resets the demo journey)"
              onClick={() => { signOut(); navigate('/login'); }}
              sx={{ color: 'text.secondary' }}
            >
              <LogOut size={16} />
            </IconButton>
          </Box>
        </Box>
      </Drawer>

      <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', minWidth: 0 }}>
        <AppBar position="static" elevation={0} sx={{ bgcolor: '#060D12', borderBottom: '1px solid rgba(255,255,255,0.08)' }}>
          <Toolbar sx={{ minHeight: 56, gap: 2 }}>
            <Typography sx={{ fontWeight: 620, flexGrow: 1, fontSize: '0.95rem' }}>
              Kaisen Unified <span style={{ color: '#5D7280', fontWeight: 450 }}>· host + AI-agent security</span>
            </Typography>
            {demoActive ? (
              <Tag tone="warn">DEMO MODE</Tag>
            ) : connectionStatus.connected ? (
              <Tag tone="accent">LIVE BACKEND</Tag>
            ) : (
              <Tag>BACKEND OFFLINE</Tag>
            )}
            <ScenarioControls size="small" />
          </Toolbar>
        </AppBar>

        <Box component="main" sx={{ flexGrow: 1, overflow: 'auto', p: 3 }}>
          {demoActive && location.pathname !== '/app/command' && location.pathname !== '/app/cockpit' && (
            <DemoBanner compact />
          )}
          <Outlet />
        </Box>
      </Box>
    </Box>
  );
}
