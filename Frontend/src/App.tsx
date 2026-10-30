import { BrowserRouter, HashRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, CssBaseline } from '@mui/material';
import { darkTheme } from './theme';
import Layout from './components/Layout';
import LandingPage from './components/pages/LandingPage';
import AuthPage from './components/pages/AuthPage';
import SetupPage from './components/pages/SetupPage';
import CommandCenter from './components/pages/CommandCenter';
import AgentCockpit from './components/pages/AgentCockpit';
import PlansPage from './components/pages/PlansPage';
import Dashboard from './components/pages/Dashboard';
import AlertsPage from './components/pages/AlertsPage';
import AttackGraphPage from './components/pages/AttackGraphPage';
import SuspiciousIPsPage from './components/pages/SuspiciousIPsPage';
import LogsPage from './components/pages/LogsPage';
import IncidentsPage from './components/pages/IncidentsPage';
import AttackLabPage from './components/pages/AttackLabPage';
import ToolsPage from './components/pages/ToolsPage';
import AuditPage from './components/pages/AuditPage';
import FleetPage from './components/pages/FleetPage';
import BillingPage from './components/pages/BillingPage';
import MemoryPage from './components/pages/MemoryPage';
import ThreatIntelPage from './components/pages/ThreatIntelPage';
import SettingsPage from './components/pages/SettingsPage';

// User journey (exhibition build):
//   Landing → Login/Sign-up → Plans (welcome) → Connect-your-server setup
//   → Command Center / Agent Cockpit (the /app shell, guarded by Layout).
//
// Router choice: the packaged Electron app loads dist/index.html over file://,
// where path-based routes (/login, /app/command, …) can never match — the
// server path is the HTML file itself. Hash-based routing keeps the route in
// the fragment, which file:// handles fine. Web dev/preview (http://) keeps
// BrowserRouter so URLs stay clean. All navigation goes through react-router
// (navigate()/useLocation), so the guards work identically under both.
const Router =
  typeof window !== 'undefined' && window.location.protocol === 'file:'
    ? HashRouter
    : BrowserRouter;

function App() {
  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Router>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<AuthPage mode="login" />} />
          <Route path="/signup" element={<AuthPage mode="signup" />} />
          <Route path="/welcome/plans" element={<PlansPage onboarding />} />
          <Route path="/welcome/setup" element={<SetupPage />} />
          <Route path="/app" element={<Layout />}>
            <Route index element={<Navigate to="/app/command" replace />} />
            <Route path="command" element={<CommandCenter />} />
            <Route path="cockpit" element={<AgentCockpit />} />
            <Route path="plans" element={<PlansPage />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="alerts" element={<AlertsPage />} />
            <Route path="attack-graph" element={<AttackGraphPage />} />
            <Route path="suspicious-ips" element={<SuspiciousIPsPage />} />
            <Route path="logs" element={<LogsPage />} />
            <Route path="incidents" element={<IncidentsPage />} />
            <Route path="lab" element={<AttackLabPage />} />
            <Route path="tools" element={<ToolsPage />} />
            <Route path="audit" element={<AuditPage />} />
            <Route path="fleet" element={<FleetPage />} />
            <Route path="billing" element={<BillingPage />} />
            <Route path="memory" element={<MemoryPage />} />
            <Route path="threat-intel" element={<ThreatIntelPage />} />
            <Route path="settings" element={<SettingsPage />} />
          </Route>
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;
