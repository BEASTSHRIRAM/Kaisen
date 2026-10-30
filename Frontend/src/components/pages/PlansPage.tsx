import { useNavigate } from 'react-router-dom';
import { Box, Button, Card, CardContent, Grid, Typography } from '@mui/material';
import { Check, Lock } from 'lucide-react';
import { Tag } from '../../unified/ui';
import { LogoLockup } from '../../unified/Logo';
import { ACCENT, HIGHLIGHT, FONT_DISPLAY } from '../../theme';
import { PlanId, useAuth } from '../../unified/authStore';

interface Tier {
  id: PlanId;
  name: string;
  price: string;
  per: string;
  blurb: string;
  features: string[];
  locked?: string[];
  featured?: boolean;
}

const TIERS: Tier[] = [
  {
    id: 'free',
    name: 'Free',
    price: '₹0',
    per: 'self-hosted',
    blurb: 'Enough to watch one agent on one server — limited services, on purpose.',
    features: [
      '1 server · 1 AI agent',
      'Host + agent monitoring',
      'Basic incident alerts',
      '7-day log retention',
    ],
    locked: ['No Slack / webhook alerts', 'No DPDP / CERT-In compliance exports', 'Summary cockpit — no tool-call feed or memory panels'],
  },
  {
    id: 'pro',
    name: 'Pro',
    price: '₹1,999',
    per: 'per server / month',
    blurb: 'The full Unified product for startups and small companies running agents in production.',
    features: [
      'Full Agent Cockpit — tool-call feed, memory & context panels',
      'Correlated incident stories (prompt → action → host)',
      '180-day log retention (CERT-In)',
      'Slack / webhook alerts with dedup',
      'DPDP / CERT-In report exports',
      'Human-approval response actions',
    ],
    featured: true,
  },
  {
    id: 'team',
    name: 'Team',
    price: '₹4,999',
    per: 'per month',
    blurb: 'For teams protecting several servers and agents, with people and permissions.',
    features: [
      'Everything in Pro',
      'Multi-server console — every server, one view',
      'Team seats + role-based access (RBAC)',
      'Priority support',
    ],
  },
];

export default function PlansPage({ onboarding = false }: { onboarding?: boolean }) {
  const navigate = useNavigate();
  const { plan, selectPlan } = useAuth();

  const choose = (id: PlanId) => {
    selectPlan(id);
    if (onboarding) navigate('/welcome/setup');
  };

  return (
    <Box sx={onboarding ? { minHeight: '100vh', bgcolor: 'background.default', py: 6, px: 3, overflowY: 'auto' } : undefined}>
      <Box sx={onboarding ? { maxWidth: 1060, mx: 'auto' } : undefined}>
        {onboarding && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.25, mb: 4 }}>
            <LogoLockup size={34} />
            <Typography variant="caption" color="text.secondary" sx={{ ml: 'auto' }}>Step 1 of 2 — plan · then connect your server</Typography>
          </Box>
        )}

        <Box sx={{ mb: 3, maxWidth: 720 }}>
          <Typography variant="h4">{onboarding ? 'Choose your plan' : 'Plans'}</Typography>
          <Typography color="text.secondary" sx={{ mt: 0.75 }}>
            You pay for the servers Kaisen protects — not per seat, not per alert.
            {onboarding ? ' Pick now, change anytime; the plan visibly shapes what the console unlocks.' : ' Your current selection is shown below; switching takes effect immediately in this demo.'}
          </Typography>
        </Box>

        <Grid container spacing={2} alignItems="stretch">
          {TIERS.map((tier) => {
            const current = plan === tier.id;
            return (
              <Grid item xs={12} md={4} key={tier.id}>
                <Card sx={{ height: '100%', border: current ? `1px solid ${ACCENT}` : tier.featured ? '1px solid rgba(252,115,77,0.6)' : '1px solid rgba(255,255,255,0.08)', bgcolor: tier.featured ? '#0A1218' : 'background.paper', position: 'relative' }}>
                  <CardContent sx={{ p: 3, display: 'flex', flexDirection: 'column', height: '100%' }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Typography variant="h6">{tier.name}</Typography>
                      {current ? <Tag tone="accent">CURRENT PLAN</Tag> : tier.featured ? (
                        <Box component="span" sx={{ display: 'inline-flex', alignItems: 'center', px: 0.85, py: 0.3, borderRadius: '6px', bgcolor: HIGHLIGHT, color: '#200D04', fontSize: '0.66rem', fontWeight: 800, letterSpacing: '0.06em', whiteSpace: 'nowrap' }}>
                          MOST POPULAR
                        </Box>
                      ) : null}
                    </Box>
                    <Box sx={{ display: 'flex', alignItems: 'baseline', gap: 1, mt: 2 }}>
                      <Typography sx={{ fontFamily: FONT_DISPLAY, fontSize: '2.3rem', fontWeight: 700, letterSpacing: '-0.03em', lineHeight: 1, color: tier.featured ? HIGHLIGHT : undefined }}>{tier.price}</Typography>
                      <Typography variant="body2" color="text.secondary">{tier.per}</Typography>
                    </Box>
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 1.5, minHeight: 58 }}>{tier.blurb}</Typography>
                    <Box sx={{ mt: 1, mb: 1, flex: 1 }}>
                      {tier.features.map((f) => (
                        <Box key={f} sx={{ display: 'flex', gap: 1.25, py: 0.6 }}>
                          <Check size={16} color={ACCENT} style={{ marginTop: 2, flexShrink: 0 }} />
                          <Typography variant="body2">{f}</Typography>
                        </Box>
                      ))}
                      {tier.locked?.map((f) => (
                        <Box key={f} sx={{ display: 'flex', gap: 1.25, py: 0.6, opacity: 0.62 }}>
                          <Lock size={14} color="#5D7280" style={{ marginTop: 3, flexShrink: 0 }} />
                          <Typography variant="body2" color="text.secondary">{f}</Typography>
                        </Box>
                      ))}
                    </Box>
                    <Button
                      variant={tier.featured || current ? 'contained' : 'outlined'}
                      fullWidth
                      onClick={() => choose(tier.id)}
                      sx={tier.featured || current
                        ? { bgcolor: ACCENT, color: '#FCFFFF', fontWeight: 700, '&:hover': { bgcolor: '#4DB6E8' } }
                        : { borderColor: 'rgba(255,255,255,0.18)', color: 'text.primary' }}
                    >
                      {current && !onboarding ? 'Current plan' : onboarding ? `Select ${tier.name}` : `Switch to ${tier.name}`}
                    </Button>
                  </CardContent>
                </Card>
              </Grid>
            );
          })}
        </Grid>

        <Box sx={{ mt: 3, p: 2.25, borderRadius: '12px', border: '1px solid rgba(255,255,255,0.08)', bgcolor: 'background.paper', display: 'flex', justifyContent: 'space-between', gap: 2, flexWrap: 'wrap' }}>
          <Box>
            <Typography sx={{ fontWeight: 650 }}>Coming later: MSP white-label</Typography>
            <Typography variant="body2" color="text.secondary" sx={{ maxWidth: 640 }}>
              Managed service providers will be able to resell Kaisen Unified under their own brand,
              across all their clients — that's a later channel, not a plan you pick today.
            </Typography>
          </Box>
          <Typography variant="caption" color="text.secondary" sx={{ maxWidth: 300 }}>
            Pricing is the indicative launch pricing from the Kaisen Unified concept (locked 30 Oct 2026), being validated with first design partners. No payment is taken in this demo.
          </Typography>
        </Box>
      </Box>
    </Box>
  );
}
