import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, CssBaseline, Box } from '@mui/material';
import { darkTheme } from './theme';
import Layout from './components/Layout';
import LandingPage from './components/pages/LandingPage';
import Dashboard from './components/pages/Dashboard';
import AlertsPage from './components/pages/AlertsPage';
import AttackGraphPage from './components/pages/AttackGraphPage';
import SuspiciousIPsPage from './components/pages/SuspiciousIPsPage';
import LogsPage from './components/pages/LogsPage';

function App() {
  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Router>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/app" element={<Layout />}>
            <Route index element={<Navigate to="/app/dashboard" replace />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="alerts" element={<AlertsPage />} />
            <Route path="attack-graph" element={<AttackGraphPage />} />
            <Route path="suspicious-ips" element={<SuspiciousIPsPage />} />
            <Route path="logs" element={<LogsPage />} />
          </Route>
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;
