import { Box, Button, Grid, Typography } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { Globe2, Play } from 'lucide-react';
import { THREAT_INTEL } from '../../unified/platformData';
import { LAB_SCENARIOS, LabScenarioId } from '../../unified/scenario';
import { useCockpit } from '../../unified/cockpitStore';
import { DemoBanner, Panel, Tag } from '../../unified/ui';
import { ACCENT } from '../../theme';

// THREAT INTEL (Tier 3) — the attack classes Kaisen covers, mapped to
// MITRE-style tactics, each linked to its playable Attack Lab scenario.
// Coverage claims are deliberately conservative: one entry is Roadmap.
export default function ThreatIntelPage() {
  const navigate = useNavigate();
  const launchScenario = useCockpit((s) => s.launchScenario);

  return (
    <Box>
      <Box sx={{ mb: 2.5, maxWidth: 800 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.25 }}>
          <Globe2 size={24} color={ACCENT} />
          <Typography variant="h4">Threat Intel — what Kaisen covers</Typography>
        </Box>
        <Typography color="text.secondary" sx={{ mt: 0.75 }}>
          The organising idea (Willison, 2025): an agent is exploitable when one session combines
          private data + untrusted content + external communication — the "lethal trifecta". Guardrails
          watch the text; host monitors watch the machine; Kaisen watches the moment the three legs meet.
          Below: each attack class, its MITRE-style mapping, Kaisen's answer, and a playable replay.
          If it says Roadmap, it is not claimed as covered.
        </Typography>
      </Box>

      <DemoBanner />

      <Grid container spacing={2}>
        {THREAT_INTEL.map((t) => (
          <Grid item xs={12} md={6} key={t.attack}>
            <Panel sx={{ height: '100%' }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', gap: 1, alignItems: 'flex-start' }}>
                <Typography sx={{ fontWeight: 680, fontSize: '1.05rem', lineHeight: 1.3 }}>{t.attack}</Typography>
                <Tag tone={t.coverage === 'Roadmap' ? 'grey' : 'accent'}>{t.coverage.toUpperCase()}</Tag>
              </Box>
              <Typography variant="caption" className="mono" color="text.secondary">{t.tactic}</Typography>
              <Typography variant="body2" sx={{ mt: 1.25, lineHeight: 1.6 }}>
                <span style={{ color: '#8FA3B0' }}>How it works — </span>{t.how}
              </Typography>
              <Typography variant="body2" sx={{ mt: 0.9, lineHeight: 1.6 }}>
                <span style={{ color: '#8FA3B0' }}>Kaisen's answer — </span>{t.defence}
              </Typography>
              {t.labScenarioId && (
                <Button
                  size="small"
                  startIcon={<Play size={13} />}
                  onClick={() => { launchScenario(t.labScenarioId as LabScenarioId); navigate('/app/cockpit'); }}
                  sx={{ mt: 1.5, color: 'primary.main', px: 0 }}
                >
                  Watch Kaisen catch it — {LAB_SCENARIOS[t.labScenarioId as LabScenarioId].name}
                </Button>
              )}
            </Panel>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}
