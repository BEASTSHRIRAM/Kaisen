import { useNavigate } from 'react-router-dom';
import { Box, Typography, Button, Container, Grid, Card, CardContent } from '@mui/material';
import {
  Security as SecurityIcon,
  Speed as SpeedIcon,
  Visibility as VisibilityIcon,
  AutoFixHigh as AutoFixHighIcon,
} from '@mui/icons-material';

export default function LandingPage() {
  const navigate = useNavigate();

  const features = [
    {
      icon: <SecurityIcon sx={{ fontSize: 48 }} />,
      title: 'Real-Time Threat Detection',
      description: 'AI-powered anomaly detection identifies security threats in real-time',
    },
    {
      icon: <SpeedIcon sx={{ fontSize: 48 }} />,
      title: 'Instant Response',
      description: 'Automated incident response with reinforcement learning',
    },
    {
      icon: <VisibilityIcon sx={{ fontSize: 48 }} />,
      title: 'Attack Visualization',
      description: 'Interactive attack graphs show complete threat landscape',
    },
    {
      icon: <AutoFixHighIcon sx={{ fontSize: 48 }} />,
      title: 'Intelligent Analysis',
      description: 'Deep learning models detect patterns invisible to traditional systems',
    },
  ];

  return (
    <Box
      sx={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%)',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      {/* Animated background elements */}
      <Box
        sx={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          opacity: 0.1,
          background: `
            radial-gradient(circle at 20% 50%, #00d4ff 0%, transparent 50%),
            radial-gradient(circle at 80% 80%, #ff4081 0%, transparent 50%)
          `,
        }}
      />

      <Container maxWidth="lg" sx={{ position: 'relative', zIndex: 1 }}>
        <Box sx={{ textAlign: 'center', mb: 8 }}>
          <SecurityIcon sx={{ fontSize: 80, color: 'primary.main', mb: 2 }} />
          <Typography
            variant="h2"
            sx={{
              fontWeight: 700,
              mb: 2,
              background: 'linear-gradient(45deg, #00d4ff 30%, #ff4081 90%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}
          >
            KAISEN
          </Typography>
          <Typography variant="h5" color="text.secondary" sx={{ mb: 4 }}>
            AI-Powered Cybersecurity Monitoring Platform
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 4, maxWidth: 600, mx: 'auto' }}>
            Protect your data center infrastructure with advanced machine learning, real-time anomaly detection,
            and automated incident response powered by deep reinforcement learning.
          </Typography>
          <Button
            variant="contained"
            size="large"
            onClick={() => navigate('/app/dashboard')}
            sx={{
              px: 6,
              py: 2,
              fontSize: '1.1rem',
              background: 'linear-gradient(45deg, #00d4ff 30%, #0099cc 90%)',
              '&:hover': {
                background: 'linear-gradient(45deg, #00d4ff 60%, #0099cc 100%)',
              },
            }}
          >
            Launch Dashboard
          </Button>
        </Box>

        <Grid container spacing={3}>
          {features.map((feature, index) => (
            <Grid item xs={12} sm={6} md={3} key={index}>
              <Card
                sx={{
                  height: '100%',
                  bgcolor: 'rgba(20, 27, 45, 0.6)',
                  backdropFilter: 'blur(10px)',
                  border: '1px solid rgba(0, 212, 255, 0.2)',
                  transition: 'all 0.3s',
                  '&:hover': {
                    transform: 'translateY(-8px)',
                    border: '1px solid rgba(0, 212, 255, 0.5)',
                    boxShadow: '0 8px 24px rgba(0, 212, 255, 0.2)',
                  },
                }}
              >
                <CardContent sx={{ textAlign: 'center', p: 3 }}>
                  <Box sx={{ color: 'primary.main', mb: 2 }}>{feature.icon}</Box>
                  <Typography variant="h6" sx={{ mb: 1, fontWeight: 600 }}>
                    {feature.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {feature.description}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>

        <Box sx={{ textAlign: 'center', mt: 8 }}>
          <Typography variant="caption" color="text.secondary">
            Powered by TensorFlow, Deep Q-Networks, and NetworkX Graph Analysis
          </Typography>
        </Box>
      </Container>
    </Box>
  );
}
