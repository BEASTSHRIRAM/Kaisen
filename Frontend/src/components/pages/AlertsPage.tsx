import { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Grid,
} from '@mui/material';
import { useStore } from '../../store/useStore';
import { Alert } from '../../types';

export default function AlertsPage() {
  const { alerts } = useStore();
  const [severityFilter, setSeverityFilter] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');

  const filteredAlerts = alerts.filter((alert) => {
    const matchesSeverity = severityFilter === 'all' || alert.severity === severityFilter;
    const matchesSearch =
      searchTerm === '' ||
      alert.node_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      alert.suspected_reason.toLowerCase().includes(searchTerm.toLowerCase()) ||
      alert.suspicious_ips.some((ip) => ip.includes(searchTerm));
    return matchesSeverity && matchesSearch;
  });

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'error';
      case 'high':
        return 'warning';
      case 'medium':
        return 'info';
      case 'low':
        return 'success';
      default:
        return 'default';
    }
  };

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 3, fontWeight: 600 }}>
        Security Alerts
      </Typography>

      <Card sx={{ mb: 3, p: 2 }}>
        <Grid container spacing={2}>
          <Grid item xs={12} md={4}>
            <FormControl fullWidth>
              <InputLabel>Severity</InputLabel>
              <Select
                value={severityFilter}
                label="Severity"
                onChange={(e) => setSeverityFilter(e.target.value)}
              >
                <MenuItem value="all">All Severities</MenuItem>
                <MenuItem value="critical">Critical</MenuItem>
                <MenuItem value="high">High</MenuItem>
                <MenuItem value="medium">Medium</MenuItem>
                <MenuItem value="low">Low</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={8}>
            <TextField
              fullWidth
              label="Search"
              placeholder="Search by node ID, reason, or IP address"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </Grid>
        </Grid>
      </Card>

      <Card>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Timestamp</TableCell>
                <TableCell>Node ID</TableCell>
                <TableCell>Severity</TableCell>
                <TableCell>Anomaly Score</TableCell>
                <TableCell>Reason</TableCell>
                <TableCell>Suspicious IPs</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredAlerts.length > 0 ? (
                filteredAlerts.map((alert) => (
                  <TableRow
                    key={alert.alert_id}
                    sx={{
                      '&:hover': { bgcolor: 'rgba(255, 255, 255, 0.05)' },
                      borderLeft: '3px solid',
                      borderColor:
                        alert.severity === 'critical'
                          ? 'error.main'
                          : alert.severity === 'high'
                          ? 'warning.main'
                          : alert.severity === 'medium'
                          ? 'info.main'
                          : 'success.main',
                    }}
                  >
                    <TableCell>
                      <Typography variant="body2">
                        {new Date(alert.timestamp).toLocaleString()}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                        {alert.node_id}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={alert.severity.toUpperCase()}
                        color={getSeverityColor(alert.severity) as any}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Typography
                        variant="body2"
                        sx={{
                          fontWeight: 600,
                          color:
                            alert.anomaly_score >= 0.8
                              ? 'error.main'
                              : alert.anomaly_score >= 0.6
                              ? 'warning.main'
                              : 'success.main',
                        }}
                      >
                        {alert.anomaly_score.toFixed(2)}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">{alert.suspected_reason}</Typography>
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                        {alert.suspicious_ips.length > 0 ? (
                          alert.suspicious_ips.map((ip, idx) => (
                            <Chip
                              key={idx}
                              label={ip}
                              size="small"
                              sx={{ fontFamily: 'monospace', fontSize: '0.75rem' }}
                            />
                          ))
                        ) : (
                          <Typography variant="caption" color="text.secondary">
                            None
                          </Typography>
                        )}
                      </Box>
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={6} align="center">
                    <Typography color="text.secondary" sx={{ py: 4 }}>
                      No alerts found
                    </Typography>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Card>

      <Box sx={{ mt: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="body2" color="text.secondary">
          Showing {filteredAlerts.length} of {alerts.length} alerts
        </Typography>
      </Box>
    </Box>
  );
}
