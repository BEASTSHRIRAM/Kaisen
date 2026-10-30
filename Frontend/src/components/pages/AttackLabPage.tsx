import { Box, Button, Grid, Typography } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { FlaskConical, Play, ShieldCheck } from 'lucide-react';
import { LAB_SCENARIO_LIST } from '../../unified/scenario';
import { useCockpit } from '../../unified/cockpitStore';
import { DemoBanner, Panel, Tag } from '../../unified/ui';
import { ACCENT, HIGHLIGHT, HIGHLIGHT_LIGHT, HIGHLIGHT_TEXT } from '../../theme';

// ATTACK LAB — the exhibition wow page. Visitors pick a real 2025–26 agent
// attack pattern and watch Kaisen catch it in the Command Center / Cockpit.
// Every scenario is a labelled DEMO replay shaped from the repo's own
// simulators — nothing here claims to be a live attack or live detection.
export default function AttackLabPage() {
  const navigate = useNavigate();
  const { launchScenario, demoActive, scenarioId } = useCockpit();

  const launch = (id: (typeof LAB_SCENARIO_LIST)[number]['id']) => {
    launchScenario(id);
    navigate('/app/cockpit');
  };

  return (
    <Box>
      <Box sx={{ mb: 2.5, maxWidth: 780 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.25 }}>
          <FlaskConical size={26} color={ACCENT} />
          <Typography variant="h4">Attack Lab</Typography>
        </Box>
        <Typography color="text.secondary" sx={{ mt: 0.75 }}>
          Pick an attack. Watch Kaisen catch it — live, in the Agent Cockpit.
          These are the patterns hitting real AI agents in 2025–26 (surveyed in our attack-landscape research): prompt-injection chains,
          MCP tool poisoning, memory poisoning, tool-based exfiltration, and the classic
          brute-force → ransomware path from Kaisen's original research.
        </Typography>
      </Box>

      <DemoBanner />

      <Grid container spacing={2}>
        {LAB_SCENARIO_LIST.map((s) => {
          const playing = demoActive && scenarioId === s.id;
          return (
            <Grid item xs={12} md={6} xl={4} key={s.id}>
              <Panel sx={{ height: '100%' }}>
                <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%', minHeight: 250 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 1 }}>
                    <Typography sx={{ fontWeight: 680, fontSize: '1.08rem', lineHeight: 1.25 }}>{s.name}</Typography>
                    <Tag tone={s.severity === 'CRITICAL' ? 'danger' : 'warn'}>{s.severity}</Tag>
                  </Box>
                  <Typography variant="caption" className="mono" color="text.secondary" sx={{ mt: 0.5 }}>{s.tactic}</Typography>
                  <Typography variant="caption" sx={{ color: 'primary.main', mt: 0.35 }}>{s.pattern}</Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 1.25, lineHeight: 1.6, flex: 1 }}>
                    {s.tagline}
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 0.6, flexWrap: 'wrap', mt: 1.5, mb: 2 }}>
                    {s.stages.map((stage, i) => (
                      <span key={stage} style={{ fontSize: '0.68rem', color: '#93A8B5', border: '1px solid rgba(255,255,255,0.12)', borderRadius: 999, padding: '3px 8px' }}>
                        {i + 1} · {stage}
                      </span>
                    ))}
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <Typography variant="caption" color="text.secondary">
                      {s.incidentId} · ~{Math.round(s.frames.length * 1.6)} s replay
                    </Typography>
                    <Button
                      variant="contained"
                      size="small"
                      startIcon={<Play size={14} />}
                      onClick={() => launch(s.id)}
                      sx={{ bgcolor: HIGHLIGHT, color: HIGHLIGHT_TEXT, fontWeight: 700, '&:hover': { bgcolor: HIGHLIGHT_LIGHT } }}
                    >
                      {playing ? 'Restart replay' : 'Launch attack'}
                    </Button>
                  </Box>
                </Box>
              </Panel>
            </Grid>
          );
        })}

        <Grid item xs={12} md={6} xl={4}>
          <Panel sx={{ height: '100%', borderStyle: 'dashed' }}>
            <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%', minHeight: 250 }}>
              <ShieldCheck size={22} color={ACCENT} />
              <Typography sx={{ fontWeight: 680, fontSize: '1.08rem', mt: 1.25 }}>How Kaisen catches these</Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1, lineHeight: 1.65, flex: 1 }}>
                No single signal is trusted. The cross-layer arbiter fires only when the{' '}
                <strong style={{ color: '#FCFFFF' }}>agent layer</strong> (prompts, tools, memory) and the{' '}
                <strong style={{ color: '#FCFFFF' }}>host layer</strong> (files, network, processes) breach
                together inside one window — then a human approves the response. That is the whole product,
                and it is why these replays end in one story instead of a wall of alerts.
              </Typography>
              <Button size="small" onClick={() => navigate('/app/command')} sx={{ alignSelf: 'flex-start', color: 'primary.main', px: 0 }}>
                Open the Command Center →
              </Button>
            </Box>
          </Panel>
        </Grid>
      </Grid>
    </Box>
  );
}
