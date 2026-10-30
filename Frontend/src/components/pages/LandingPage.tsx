import { useNavigate } from 'react-router-dom';
import { LogoMark } from '../../unified/Logo';
import { Box, Typography, Button, Container, Grid, Card, CardContent } from '@mui/material';
import {
  SmartToy as AgentIcon,
  AccountTree as StoryIcon,
  FactCheck as ExplainIcon,
  ReceiptLong as AuditIcon,
} from '@mui/icons-material';

export default function LandingPage() {
  const navigate = useNavigate();

  const features = [
    {
      icon: <StoryIcon sx={{ fontSize: 40 }} />,
      title: 'One incident, one story',
      description:
        'A suspicious prompt, the file the agent opened because of it, and the host anomaly that followed — correlated into a single cause → effect story, not four separate alerts.',
    },
    {
      icon: <AgentIcon sx={{ fontSize: 40 }} />,
      title: 'Agent Cockpit',
      description:
        'Watch the agent itself: what it is doing right now, every tool call it makes, what sits in its memory and context window, and what the session is costing.',
    },
    {
      icon: <ExplainIcon sx={{ fontSize: 40 }} />,
      title: 'Reasons, in plain language',
      description:
        'Every flag ships with a SHAP-style explanation of the signals that drove it — system-prompt extraction attempts, prompt-length spikes, failed tool retries — so a human can judge it.',
    },
    {
      icon: <AuditIcon sx={{ fontSize: 40 }} />,
      title: 'Audit log built for India',
      description:
        'Which agent accessed what data, when, and who approved each intervention — exportable for DPDP and CERT-In reporting.',
    },
  ];

  return (
    <Box
      sx={{
        minHeight: '100vh',
        bgcolor: '#02070A',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        py: 8,
        overflowY: 'auto',
      }}
    >
      <Container maxWidth="lg">
        <Box sx={{ textAlign: 'center', mb: 7 }}>
          <Box sx={{ display: 'flex', justifyContent: 'center', mb: 2.5 }}>
            <LogoMark size={64} />
          </Box>
          <Typography variant="h2" sx={{ fontWeight: 750, letterSpacing: '0.04em', mb: 1.5, fontSize: '3.2rem' }}>
            KAISEN <span style={{ color: '#0297DE' }}>UNIFIED</span>
          </Typography>
          <Typography variant="h5" sx={{ mb: 2.5, fontWeight: 550 }}>
            Security for businesses running AI agents on their own servers
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 4.5, maxWidth: 640, mx: 'auto', lineHeight: 1.65 }}>
            Guardrails only see the prompt. Network monitors only see the machine. Kaisen watches{' '}
            <strong style={{ color: '#FCFFFF' }}>both together</strong> — and connects an attack across them.
            Kaisen recommends; a human always approves.
          </Typography>
          <Box sx={{ display: 'flex', gap: 1.5, justifyContent: 'center', flexWrap: 'wrap' }}>
            <Button
              variant="contained"
              size="large"
              onClick={() => navigate('/login')}
              sx={{ px: 4.5, py: 1.6, bgcolor: 'primary.main', color: '#FCFFFF', fontWeight: 650, '&:hover': { bgcolor: '#4DB6E8' } }}
            >
              Launch Kaisen — sign in
            </Button>
            <Button
              variant="outlined"
              size="large"
              onClick={() => navigate('/signup')}
              sx={{ px: 4.5, py: 1.6, borderColor: 'rgba(255,255,255,0.2)', color: 'text.primary' }}
            >
              Create a free account
            </Button>
          </Box>
        </Box>

        <Grid container spacing={2.5}>
          {features.map((feature) => (
            <Grid item xs={12} sm={6} md={3} key={feature.title}>
              <Card sx={{ height: '100%', transition: 'border-color 0.25s', '&:hover': { borderColor: 'rgba(2,151,222,0.45)' } }}>
                <CardContent sx={{ p: 3 }}>
                  <Box sx={{ color: 'primary.main', mb: 1.75 }}>{feature.icon}</Box>
                  <Typography variant="h6" sx={{ mb: 1, fontSize: '1.02rem' }}>
                    {feature.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ lineHeight: 1.6 }}>
                    {feature.description}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>

        <Box sx={{ textAlign: 'center', mt: 7 }}>
          <Typography variant="caption" color="text.secondary">
            Research core: Double DQN incident-response agents trained on CICIDS2017 / CERT-grounded simulators, with SHAP
            explainability — live host detection today is rule-based and labelled as such in the app.
          </Typography>
        </Box>
      </Container>
    </Box>
  );
}
