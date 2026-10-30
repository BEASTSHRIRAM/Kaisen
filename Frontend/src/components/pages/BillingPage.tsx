import { Box, Button, Grid, Typography } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { CreditCard } from 'lucide-react';
import { INVOICES, PLAN_LIMITS } from '../../unified/platformData';
import { useAuth, PLAN_LABEL } from '../../unified/authStore';
import { DemoBanner, Meter, Panel, Tag } from '../../unified/ui';
import { ACCENT, FONT_DISPLAY } from '../../theme';

// BILLING & USAGE — closes the subscription story: current plan, what the
// workspace actually used, invoices, upgrade path. Demo billing data.
export default function BillingPage() {
  const navigate = useNavigate();
  const plan = useAuth((s) => s.plan) || 'pro';
  const limit = PLAN_LIMITS[plan];

  return (
    <Box>
      <Box sx={{ mb: 2.5 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.25 }}>
          <CreditCard size={24} color={ACCENT} />
          <Typography variant="h4">Billing & Usage</Typography>
        </Box>
        <Typography color="text.secondary" sx={{ mt: 0.5 }}>
          What you're on, what you've used, what it costs. No per-seat, no per-alert surprises.
        </Typography>
      </Box>

      <DemoBanner />

      <Grid container spacing={2}>
        <Grid item xs={12} lg={5}>
          <Panel title="Current plan" sx={{ height: '100%' }}>
            <Typography sx={{ fontFamily: FONT_DISPLAY, fontSize: '1.6rem', fontWeight: 700, letterSpacing: '-0.02em' }}>{PLAN_LABEL[plan as 'free' | 'pro' | 'team']}</Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 0.75, lineHeight: 1.65 }}>
              {plan === 'free' && 'Self-hosted, 1 server, basic alerts, 7-day logs. The full Cockpit, compliance exports and Slack alerts unlock on Pro.'}
              {plan === 'pro' && 'Full Agent Cockpit, correlated incident stories, 180-day CERT-In retention, Slack/webhook alerts, DPDP/CERT-In exports, human-approval actions — per protected server.'}
              {plan === 'team' && 'Everything in Pro, across a multi-server console, with team seats and role-based access.'}
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, mt: 2.25, flexWrap: 'wrap' }}>
              <Button variant="contained" onClick={() => navigate('/app/plans')} sx={{ bgcolor: ACCENT, color: '#FCFFFF', fontWeight: 700, '&:hover': { bgcolor: '#4DB6E8' } }}>
                {plan === 'free' ? 'Upgrade to Pro' : 'Change plan'}
              </Button>
              <Button variant="outlined" onClick={() => navigate('/welcome/setup')} sx={{ borderColor: 'rgba(255,255,255,0.2)', color: 'text.primary' }}>
                Connect another server
              </Button>
            </Box>
            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 2 }}>
              Demo build: no payment is taken and no card is stored. Billing goes live with the hosted launch.
            </Typography>
          </Panel>
        </Grid>

        <Grid item xs={12} lg={7}>
          <Panel title="Usage this period (demo data)" sx={{ height: '100%' }}>
            <Meter label="Servers protected" value={3} max={Math.max(limit.servers, 3)} display={`3 / ${limit.servers}`} dangerAbove={100} />
            <Meter label="Agent sessions monitored" value={842} max={1000} display="842 sessions" />
            <Meter label="Incidents correlated" value={14} max={20} display="14 incidents · 4 critical/high" />
            <Meter label="Log retention" value={plan === 'free' ? 7 : 180} max={180} display={plan === 'free' ? '7 days (Free)' : '180 days (CERT-In)'} />
            <Meter label="Blocked tool actions" value={24} max={30} display="24 blocked · 0 false-positive escalations" />
          </Panel>
        </Grid>

        <Grid item xs={12}>
          <Panel title="Invoices">
            <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1.2fr 1.6fr 0.8fr 0.7fr', gap: 1.5, pb: 1.25, borderBottom: '1px solid rgba(255,255,255,0.09)' }}>
              {['Invoice', 'Period', 'Plan', 'Amount', 'Status'].map((h) => (
                <Typography key={h} variant="caption" sx={{ textTransform: 'uppercase', letterSpacing: '0.11em', color: 'text.secondary', fontWeight: 650 }}>{h}</Typography>
              ))}
            </Box>
            {INVOICES.map((inv) => (
              <Box key={inv.id} sx={{ display: 'grid', gridTemplateColumns: '1fr 1.2fr 1.6fr 0.8fr 0.7fr', gap: 1.5, py: 1.3, borderBottom: '1px solid rgba(255,255,255,0.05)', alignItems: 'center' }}>
                <Typography className="mono" variant="body2">{inv.id}</Typography>
                <Typography variant="body2">{inv.period}</Typography>
                <Typography variant="body2" color="text.secondary">{inv.plan}</Typography>
                <Typography variant="body2" sx={{ fontWeight: 650 }}>{inv.amount}</Typography>
                <Box><Tag tone="accent">{inv.status.toUpperCase()}</Tag></Box>
              </Box>
            ))}
          </Panel>
        </Grid>
      </Grid>
    </Box>
  );
}
