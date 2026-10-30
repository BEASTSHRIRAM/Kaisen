import { Box, Button, Grid, Typography } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { Plus, Server } from 'lucide-react';
import { FLEET, PLAN_LIMITS } from '../../unified/platformData';
import { useAuth, PLAN_LABEL } from '../../unified/authStore';
import { DemoBanner, Meter, Panel, Tag } from '../../unified/ui';
import { ACCENT } from '../../theme';

const STATUS: Record<string, { label: string; tone: 'accent' | 'warn' | 'danger'; dot: string }> = {
  online: { label: 'ONLINE', tone: 'accent', dot: '#34d399' },
  degraded: { label: 'DEGRADED', tone: 'warn', dot: '#f5a524' },
  offline: { label: 'OFFLINE', tone: 'danger', dot: '#f04b5d' },
};

// FLEET / SERVERS — every connected server + its agents, tied to the plan
// limit so the subscription gating is visible here too. Demo fleet.
export default function FleetPage() {
  const navigate = useNavigate();
  const plan = useAuth((s) => s.plan) || 'pro';
  const limit = PLAN_LIMITS[plan];
  const used = FLEET.length;
  const overLimit = used > limit.servers;

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2.5, flexWrap: 'wrap', gap: 2 }}>
        <Box sx={{ maxWidth: 700 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.25 }}>
            <Server size={24} color={ACCENT} />
            <Typography variant="h4">Fleet — Servers & Agents</Typography>
          </Box>
          <Typography color="text.secondary" sx={{ mt: 0.75 }}>
            Every server running the Kaisen agent, and every AI agent Kaisen watches on it.
          </Typography>
        </Box>
        <Button variant="contained" startIcon={<Plus size={15} />} onClick={() => navigate('/welcome/setup')} sx={{ bgcolor: ACCENT, color: '#FCFFFF', fontWeight: 700, '&:hover': { bgcolor: '#4DB6E8' } }}>
          Connect a server
        </Button>
      </Box>

      <DemoBanner />

      <Panel sx={{ mb: 2 }}>
        <Box sx={{ maxWidth: 520 }}>
          <Meter
            label={`Plan limit — ${PLAN_LABEL[plan as 'free' | 'pro' | 'team']}`}
            value={used}
            max={Math.max(limit.servers, used)}
            display={`${used} / ${limit.servers} servers`}
            dangerAbove={100}
          />
        </Box>
        <Typography variant="body2" color={overLimit ? 'error.main' : 'text.secondary'}>
          {overLimit
            ? `This demo fleet has ${used} servers but the ${limit.label} plan covers ${limit.servers}. In production the extra servers pause monitoring until the plan is upgraded — that is the Free plan's limit doing its job.`
            : `${limit.label} covers up to ${limit.servers} servers. Each new server is one install command away (Setup).`}
        </Typography>
      </Panel>

      <Grid container spacing={2}>
        {FLEET.map((s) => {
          const st = STATUS[s.status];
          return (
            <Grid item xs={12} md={6} xl={4} key={s.name}>
              <Panel sx={{ height: '100%' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.25, mb: 1.5 }}>
                  <Box sx={{ width: 9, height: 9, borderRadius: '50%', bgcolor: st.dot, flexShrink: 0 }} className={s.status === 'online' ? 'kaisen-dot-live' : undefined} />
                  <Typography className="mono" sx={{ fontWeight: 700, fontSize: '1.02rem' }}>{s.name}</Typography>
                  <Box sx={{ ml: 'auto' }}><Tag tone={st.tone}>{st.label}</Tag></Box>
                </Box>
                <Typography variant="body2" color="text.secondary">{s.os}</Typography>
                <Typography variant="caption" className="mono" color="text.secondary">{s.agentVersion} · heartbeat {s.lastHeartbeat}</Typography>
                <Box sx={{ mt: 2 }}>
                  <Meter label="CPU" value={s.cpu} max={100} display={`${s.cpu}%`} dangerAbove={85} />
                  <Meter label="Memory" value={s.mem} max={100} display={`${s.mem}%`} dangerAbove={85} />
                </Box>
                <Box sx={{ mt: 1, pt: 1.5, borderTop: '1px solid rgba(255,255,255,0.07)' }}>
                  <Typography variant="caption" sx={{ textTransform: 'uppercase', letterSpacing: '0.11em', color: 'text.secondary', fontWeight: 650 }}>Agents on this host</Typography>
                  {s.agents.map((a) => (
                    <Box key={a.name} sx={{ mt: 1 }}>
                      <Typography variant="body2" sx={{ fontWeight: 600 }}>{a.name}</Typography>
                      <Typography variant="caption" color="text.secondary">{a.sessionsToday} sessions today · {a.state}</Typography>
                    </Box>
                  ))}
                </Box>
              </Panel>
            </Grid>
          );
        })}
      </Grid>
    </Box>
  );
}
