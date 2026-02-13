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
  TextField,
  Chip,
} from '@mui/material';
import { useStore } from '../../store/useStore';

export default function LogsPage() {
  const { logs } = useStore();
  const [searchTerm, setSearchTerm] = useState('');

  const filteredLogs = logs.filter(
    (log) =>
      searchTerm === '' ||
      log.node_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.timestamp.includes(searchTerm)
  );

  const getStatusColor = (log: any) => {
    if (log.failed_logins > 10) return 'error';
    if (log.cpu_usage > 80 || log.memory_usage > 85) return 'warning';
    return 'success';
  };

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 3, fontWeight: 600 }}>
        System Logs
      </Typography>

      <Card sx={{ mb: 3, p: 2 }}>
        <TextField
          fullWidth
          label="Search"
          placeholder="Search by node ID or timestamp"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </Card>

      <Card>
        <TableContainer sx={{ maxHeight: 600 }}>
          <Table stickyHeader>
            <TableHead>
              <TableRow>
                <TableCell>Timestamp</TableCell>
                <TableCell>Node ID</TableCell>
                <TableCell>CPU %</TableCell>
                <TableCell>Memory %</TableCell>
                <TableCell>Processes</TableCell>
                <TableCell>Connections</TableCell>
                <TableCell>Failed Logins</TableCell>
                <TableCell>Status</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredLogs.length > 0 ? (
                filteredLogs.map((log, index) => (
                  <TableRow
                    key={index}
                    sx={{
                      '&:hover': { bgcolor: 'rgba(255, 255, 255, 0.05)' },
                    }}
                  >
                    <TableCell>
                      <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: '0.85rem' }}>
                        {new Date(log.timestamp).toLocaleString()}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                        {log.node_id}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography
                        variant="body2"
                        sx={{
                          color: log.cpu_usage > 80 ? 'error.main' : 'text.primary',
                          fontWeight: log.cpu_usage > 80 ? 600 : 400,
                        }}
                      >
                        {log.cpu_usage.toFixed(1)}%
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography
                        variant="body2"
                        sx={{
                          color: log.memory_usage > 85 ? 'error.main' : 'text.primary',
                          fontWeight: log.memory_usage > 85 ? 600 : 400,
                        }}
                      >
                        {log.memory_usage.toFixed(1)}%
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">{log.process_count}</Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">{log.network_connections}</Typography>
                    </TableCell>
                    <TableCell>
                      <Typography
                        variant="body2"
                        sx={{
                          color: log.failed_logins > 10 ? 'error.main' : 'text.primary',
                          fontWeight: log.failed_logins > 10 ? 600 : 400,
                        }}
                      >
                        {log.failed_logins}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={
                          log.failed_logins > 10
                            ? 'ALERT'
                            : log.cpu_usage > 80 || log.memory_usage > 85
                            ? 'WARNING'
                            : 'NORMAL'
                        }
                        color={getStatusColor(log) as any}
                        size="small"
                      />
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={8} align="center">
                    <Typography color="text.secondary" sx={{ py: 4 }}>
                      No logs found
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
          Showing {filteredLogs.length} of {logs.length} log entries
        </Typography>
        <Typography variant="caption" color="text.secondary">
          Logs are updated in real-time
        </Typography>
      </Box>
    </Box>
  );
}
