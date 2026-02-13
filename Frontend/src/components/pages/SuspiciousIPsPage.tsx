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
  TextField,
  LinearProgress,
} from '@mui/material';
import { useStore } from '../../store/useStore';

export default function SuspiciousIPsPage() {
  const { suspiciousIPs } = useStore();
  const [searchTerm, setSearchTerm] = useState('');

  const filteredIPs = suspiciousIPs.filter((ip) =>
    ip.ip.includes(searchTerm) || (ip.node_id && ip.node_id.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  const getRiskColor = (score: number) => {
    if (score >= 0.7) return 'error';
    if (score >= 0.5) return 'warning';
    if (score >= 0.3) return 'info';
    return 'success';
  };

  const getRiskLabel = (score: number) => {
    if (score >= 0.7) return 'HIGH';
    if (score >= 0.5) return 'MEDIUM';
    if (score >= 0.3) return 'LOW';
    return 'MINIMAL';
  };

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 3, fontWeight: 600 }}>
        Suspicious IP Addresses
      </Typography>

      <Card sx={{ mb: 3, p: 2 }}>
        <TextField
          fullWidth
          label="Search"
          placeholder="Search by IP address or node ID"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </Card>

      <Card>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>IP Address</TableCell>
                <TableCell>Connection Count</TableCell>
                <TableCell>Failed Attempts</TableCell>
                <TableCell>Risk Score</TableCell>
                <TableCell>Risk Level</TableCell>
                <TableCell>Last Seen</TableCell>
                <TableCell>Node ID</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredIPs.length > 0 ? (
                filteredIPs.map((ip, index) => (
                  <TableRow
                    key={index}
                    sx={{
                      '&:hover': { bgcolor: 'rgba(255, 255, 255, 0.05)' },
                      borderLeft: '3px solid',
                      borderColor:
                        ip.risk_score >= 0.7
                          ? 'error.main'
                          : ip.risk_score >= 0.5
                          ? 'warning.main'
                          : 'info.main',
                    }}
                  >
                    <TableCell>
                      <Typography variant="body2" sx={{ fontFamily: 'monospace', fontWeight: 600 }}>
                        {ip.ip}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Box>
                        <Typography variant="body2" sx={{ mb: 0.5 }}>
                          {ip.connection_count}
                        </Typography>
                        <LinearProgress
                          variant="determinate"
                          value={Math.min((ip.connection_count / 100) * 100, 100)}
                          sx={{
                            height: 4,
                            borderRadius: 2,
                            bgcolor: 'rgba(255, 255, 255, 0.1)',
                            '& .MuiLinearProgress-bar': {
                              bgcolor: ip.connection_count > 50 ? 'error.main' : 'primary.main',
                            },
                          }}
                        />
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Box>
                        <Typography
                          variant="body2"
                          sx={{
                            mb: 0.5,
                            color: ip.failed_attempts > 5 ? 'error.main' : 'text.primary',
                            fontWeight: ip.failed_attempts > 5 ? 600 : 400,
                          }}
                        >
                          {ip.failed_attempts}
                        </Typography>
                        <LinearProgress
                          variant="determinate"
                          value={Math.min((ip.failed_attempts / 20) * 100, 100)}
                          sx={{
                            height: 4,
                            borderRadius: 2,
                            bgcolor: 'rgba(255, 255, 255, 0.1)',
                            '& .MuiLinearProgress-bar': {
                              bgcolor: ip.failed_attempts > 5 ? 'error.main' : 'warning.main',
                            },
                          }}
                        />
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Typography
                        variant="body2"
                        sx={{
                          fontWeight: 600,
                          color:
                            ip.risk_score >= 0.7
                              ? 'error.main'
                              : ip.risk_score >= 0.5
                              ? 'warning.main'
                              : 'success.main',
                        }}
                      >
                        {ip.risk_score.toFixed(2)}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={getRiskLabel(ip.risk_score)}
                        color={getRiskColor(ip.risk_score) as any}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" color="text.secondary">
                        {new Date(ip.last_seen).toLocaleString()}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                        {ip.node_id || 'N/A'}
                      </Typography>
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={7} align="center">
                    <Typography color="text.secondary" sx={{ py: 4 }}>
                      No suspicious IPs found
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
          Showing {filteredIPs.length} of {suspiciousIPs.length} suspicious IPs
        </Typography>
      </Box>
    </Box>
  );
}
