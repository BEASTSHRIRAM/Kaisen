import { Box, Button, Grid, MenuItem, Select, TextField, Typography } from '@mui/material';
import { Settings as SettingsIcon, Users } from 'lucide-react';
import { useState } from 'react';
import { TEAM_MEMBERS } from '../../unified/platformData';
import { useAuth, PLAN_LABEL } from '../../unified/authStore';
import { DemoBanner, Panel, Tag } from '../../unified/ui';
import { ACCENT } from '../../theme';

// SETTINGS + TEAM/RBAC shell (Tier 3) — real UI over local state; role
// changes are demo-state (labelled), enforcement is a Team-plan feature.
const ROLES = ['Owner', 'Operator — can approve interventions', 'Viewer — read-only + exports'];

export default function SettingsPage() {
  const plan = useAuth((s) => s.plan) || 'pro';
  const [members, setMembers] = useState(TEAM_MEMBERS);
  const [workspace, setWorkspace] = useState('Northwind (demo workspace)');
  const [saved, setSaved] = useState(false);

  return (
    <Box>
      <Box sx={{ mb: 2.5 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.25 }}>
          <SettingsIcon size={24} color={ACCENT} />
          <Typography variant="h4">Settings</Typography>
        </Box>
        <Typography color="text.secondary" sx={{ mt: 0.5 }}>Workspace, team and roles. Role enforcement ships with the Team plan.</Typography>
      </Box>

      <DemoBanner />

      <Grid container spacing={2}>
        <Grid item xs={12} lg={5}>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <Panel title="Workspace">
              <TextField label="Workspace name" fullWidth value={workspace} onChange={(e) => setWorkspace(e.target.value)} sx={{ mb: 2 }} />
              <TextField label="Default server region" fullWidth defaultValue="India (Bengaluru)" sx={{ mb: 2 }} />
              <TextField label="Incident notification channel" fullWidth defaultValue="#kaisen-alerts (Slack — Pro)" />
              <Button variant="contained" sx={{ mt: 2.25, bgcolor: ACCENT, color: '#FCFFFF', fontWeight: 700, '&:hover': { bgcolor: '#4DB6E8' } }} onClick={() => { setSaved(true); setTimeout(() => setSaved(false), 2000); }}>
                {saved ? 'Saved (demo)' : 'Save settings'}
              </Button>
              <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1.5 }}>
                Demo build: settings persist for this session only.
              </Typography>
            </Panel>
            <Panel title="Plan & enforcement">
              <Typography variant="body2" sx={{ lineHeight: 1.65 }}>
                Current plan: <strong>{PLAN_LABEL[plan as 'free' | 'pro' | 'team']}</strong>.{' '}
                {plan === 'team'
                  ? 'RBAC is enforced on this plan: Viewers cannot approve interventions, Operators cannot change billing.'
                  : 'On Free and Pro, every signed-in member is an operator. Team adds seats + RBAC enforcement — that is the ₹4,999/mo difference.'}
              </Typography>
            </Panel>
          </Box>
        </Grid>

        <Grid item xs={12} lg={7}>
          <Panel title="Team & roles" >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1.5 }}>
              <Users size={16} color={ACCENT} />
              <Typography variant="body2" color="text.secondary">{members.length} members · role changes below are demo state</Typography>
              <Box sx={{ ml: 'auto' }}><Tag tone={plan === 'team' ? 'accent' : 'warn'}>{plan === 'team' ? 'RBAC ENFORCED' : 'RBAC — TEAM PLAN'}</Tag></Box>
            </Box>
            {members.map((m, i) => (
              <Box key={m.email} sx={{ display: 'grid', gridTemplateColumns: '1.3fr 1.5fr 1.6fr 0.7fr', gap: 1.5, alignItems: 'center', py: 1.3, borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.25 }}>
                  <Box sx={{ width: 30, height: 30, borderRadius: '50%', bgcolor: 'rgba(2,151,222,0.13)', color: ACCENT, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.68rem', fontWeight: 700 }}>
                    {m.name.split(' ').map((w) => w[0]).slice(0, 2).join('')}
                  </Box>
                  <Typography variant="body2" sx={{ fontWeight: 600 }}>{m.name}</Typography>
                </Box>
                <Typography variant="body2" className="mono" color="text.secondary" sx={{ fontSize: '0.78rem' }}>{m.email}</Typography>
                <Select
                  size="small"
                  value={m.role}
                  onChange={(e) => setMembers((prev) => prev.map((x, xi) => (xi === i ? { ...x, role: e.target.value } : x)))}
                  sx={{ fontSize: '0.8rem', '& .MuiOutlinedInput-notchedOutline': { borderColor: 'rgba(255,255,255,0.16)' } }}
                >
                  {ROLES.map((r) => <MenuItem key={r} value={r}>{r}</MenuItem>)}
                </Select>
                <Typography variant="caption" color="text.secondary">{m.lastActive}</Typography>
              </Box>
            ))}
            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1.5 }}>
              Who can do what is the whole point of RBAC in a security product: the person who sees an
              incident is not automatically the person who may isolate a production server.
            </Typography>
          </Panel>
        </Grid>
      </Grid>
    </Box>
  );
}
