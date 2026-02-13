import { ThemeProvider, CssBaseline, Box, Typography } from '@mui/material';
import { darkTheme } from './theme';
import { useStore } from './store/useStore';

function App() {
  const { connectionStatus } = useStore();

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Box sx={{ p: 4 }}>
        <Typography variant="h3" sx={{ mb: 2 }}>
          Kaisen - Minimal Test
        </Typography>
        <Typography variant="body1">
          Store Status: {connectionStatus.connected ? 'Connected' : 'Disconnected'}
        </Typography>
        <Typography variant="body2" sx={{ mt: 2, color: 'success.main' }}>
          ✅ If you see this, the store is working!
        </Typography>
      </Box>
    </ThemeProvider>
  );
}

export default App;
