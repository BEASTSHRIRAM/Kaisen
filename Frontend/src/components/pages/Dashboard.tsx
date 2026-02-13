import { Grid, Card, CardContent, Typography, Box, LinearProgress } from '@mui/material';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import { useStore } from '../../store/useStore';
import MetricCard from '../MetricCard';
import {
  Memory as MemoryIcon,
  Speed as SpeedIcon,
  NetworkCheck as NetworkIcon,
  Lock as LockIcon,
  Warning as WarningIcon,
} from '@mui/icons-material';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler);

export default function Dashboard() {
  const { currentMetrics, metricsHistory, alerts } = useStore();

  const recentAlerts = alerts.slice(0, 5);
  const criticalAlerts = alerts.filter((a) => a.severity === 'critical').length;

  const chartData = {
    labels: metricsHistory.map((m) => new Date(m.timestamp).toLocaleTimeString()),
    datasets: [
      {
        label: 'CPU Usage (%)',
        data: metricsHistory.map((m) => m.cpu_usage),
        borderColor: '#00d4ff',
        backgroundColor: 'rgba(0, 212, 255, 0.1)',
        fill: true,
        tension: 0.4,
      },
      {
        label: 'Memory Usage (%)',
        data: metricsHistory.map((m) => m.memory_usage),
        borderColor: '#ff4081',
        backgroundColor: 'rgba(255, 64, 129, 0.1)',
        fill: true,
        tension: 0.4,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
        labels: {
          color: '#ffffff',
        },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 100,
        grid: {
          color: 'rgba(255, 255, 255, 0.1)',
        },
        ticks: {
          color: '#b0b0b0',
        },
      },
      x: {
        grid: {
          color: 'rgba(255, 255, 255, 0.1)',
        },
        ticks: {
          color: '#b0b0b0',
        },
      },
    },
  };

  const getAnomalyColor = (score?: number) => {
    if (!score) return 'success';
    if (score >= 0.8) return 'error';
    if (score >= 0.6) return 'warning';
    return 'success';
  };

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 3, fontWeight: 600 }}>
        Security Dashboard
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} sm={6} md={2.4}>
          <MetricCard
            title="CPU Usage"
            value={currentMetrics?.cpu_usage.toFixed(1) || '0'}
            unit="%"
            icon={<SpeedIcon />}
            color="#00d4ff"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <MetricCard
            title="Memory Usage"
            value={currentMetrics?.memory_usage.toFixed(1) || '0'}
            unit="%"
            icon={<MemoryIcon />}
            color="#ff4081"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <MetricCard
            title="Network Connections"
            value={currentMetrics?.network_connections.toString() || '0'}
            unit=""
            icon={<NetworkIcon />}
            color="#4caf50"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <MetricCard
            title="Failed Logins"
            value={currentMetrics?.failed_logins.toString() || '0'}
            unit=""
            icon={<LockIcon />}
            color="#ff9800"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <MetricCard
            title="Anomaly Score"
            value={currentMetrics?.anomaly_score?.toFixed(2) || '0.00'}
            unit=""
            icon={<WarningIcon />}
            color={
              currentMetrics?.anomaly_score && currentMetrics.anomaly_score >= 0.7
                ? '#f44336'
                : currentMetrics?.anomaly_score && currentMetrics.anomaly_score >= 0.5
                ? '#ff9800'
                : '#4caf50'
            }
          />
        </Grid>

        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2 }}>
                System Metrics Trend
              </Typography>
              <Box sx={{ height: 300 }}>
                {metricsHistory.length > 0 ? (
                  <Line data={chartData} options={chartOptions} />
                ) : (
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
                    <Typography color="text.secondary">Waiting for data...</Typography>
                  </Box>
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2 }}>
                Recent Alerts
              </Typography>
              {recentAlerts.length > 0 ? (
                <Box>
                  {recentAlerts.map((alert) => (
                    <Box
                      key={alert.alert_id}
                      sx={{
                        mb: 2,
                        p: 1.5,
                        borderRadius: 1,
                        bgcolor: 'rgba(255, 255, 255, 0.05)',
                        borderLeft: '3px solid',
                        borderColor:
                          alert.severity === 'critical'
                            ? 'error.main'
                            : alert.severity === 'high'
                            ? 'warning.main'
                            : 'info.main',
                      }}
                    >
                      <Typography variant="caption" color="text.secondary">
                        {new Date(alert.timestamp).toLocaleString()}
                      </Typography>
                      <Typography variant="body2" sx={{ mt: 0.5 }}>
                        {alert.suspected_reason}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        Node: {alert.node_id}
                      </Typography>
                    </Box>
                  ))}
                </Box>
              ) : (
                <Typography color="text.secondary">No recent alerts</Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {currentMetrics && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 2 }}>
                  System Health Overview
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} md={6}>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                      CPU Usage
                    </Typography>
                    <LinearProgress
                      variant="determinate"
                      value={currentMetrics.cpu_usage}
                      sx={{
                        height: 8,
                        borderRadius: 4,
                        bgcolor: 'rgba(255, 255, 255, 0.1)',
                        '& .MuiLinearProgress-bar': {
                          bgcolor: currentMetrics.cpu_usage > 80 ? 'error.main' : 'primary.main',
                        },
                      }}
                    />
                    <Typography variant="caption" color="text.secondary">
                      {currentMetrics.cpu_usage.toFixed(1)}%
                    </Typography>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                      Memory Usage
                    </Typography>
                    <LinearProgress
                      variant="determinate"
                      value={currentMetrics.memory_usage}
                      sx={{
                        height: 8,
                        borderRadius: 4,
                        bgcolor: 'rgba(255, 255, 255, 0.1)',
                        '& .MuiLinearProgress-bar': {
                          bgcolor: currentMetrics.memory_usage > 85 ? 'error.main' : 'secondary.main',
                        },
                      }}
                    />
                    <Typography variant="caption" color="text.secondary">
                      {currentMetrics.memory_usage.toFixed(1)}%
                    </Typography>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        )}
      </Grid>
    </Box>
  );
}
