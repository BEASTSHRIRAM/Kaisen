import { Box, Typography, Button } from '@mui/material';
import { useStore } from '../../store/useStore';

export default function TestPage() {
  const { connectionStatus, setConnectionStatus } = useStore();

  const handleTest = () => {
    setConnectionStatus({ connected: true, lastUpdate: new Date(), error: null });
  };

  return (
    <Box sx={{ p: 4 }}>
      <Typography variant="h4" sx={{ mb: 3 }}>
        Store Test Page
      </Typography>
      <Typography variant="body1" sx={{ mb: 2 }}>
        Connection Status: {connectionStatus.connected ? 'Connected' : 'Disconnected'}
      </Typography>
      <Button variant="contained" onClick={handleTest}>
        Test Store
      </Button>
    </Box>
  );
}
