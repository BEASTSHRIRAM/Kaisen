import { useState } from 'react';
import { Box, Button, Grid, Typography } from '@mui/material';
import { Brain, ShieldAlert } from 'lucide-react';
import { MEMORY_ENTRIES } from '../../unified/platformData';
import { DemoBanner, Panel, Tag } from '../../unified/ui';
import { ACCENT } from '../../theme';

const TRUST_TONE: Record<string, 'accent' | 'warn' | 'danger'> = {
  trusted: 'accent', unverified: 'warn', quarantined: 'danger',
};

// MEMORY INSPECTOR (Tier 3) — every memory the agent carries, where it came
// from, and the quarantined poisoned entry from INC-1051. Demo entries.
export default function MemoryPage() {
  const [quarantineLifted, setQuarantineLifted] = useState(false);
  const poisoned = MEMORY_ENTRIES.find((m) => m.trust === 'quarantined')!;

  return (
    <Box>
      <Box sx={{ mb: 2.5, maxWidth: 800 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.25 }}>
          <Brain size={24} color={ACCENT} />
          <Typography variant="h4">Memory Inspector</Typography>
        </Box>
        <Typography color="text.secondary" sx={{ mt: 0.75 }}>
          An agent's memory is an attack surface: plant a rule today, it fires next week.
          Kaisen records where every memory came from — and a memory from an unverified source
          can never authorise a sensitive action.
        </Typography>
      </Box>

      <DemoBanner />

      <Box sx={{ mb: 2, p: 2, borderRadius: '12px', border: '1px solid rgba(240,75,93,0.5)', bgcolor: 'rgba(240,75,93,0.06)', display: 'flex', gap: 2, flexWrap: 'wrap', alignItems: 'center' }}>
        <ShieldAlert size={22} color="#f04b5d" style={{ flexShrink: 0 }} />
        <Box sx={{ flex: 1, minWidth: 280 }}>
          <Typography sx={{ fontWeight: 680, color: 'error.main' }}>
            {quarantineLifted ? 'Quarantine lifted by operator (demo action, audit-logged)' : '1 memory quarantined — INC-1051'}
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 0.35 }}>
            {poisoned.text} Written at {poisoned.written} from {poisoned.source}. It tried to make the agent
            export customer profiles. It is inert while quarantined.
          </Typography>
        </Box>
        {!quarantineLifted ? (
          <Button variant="outlined" color="error" onClick={() => setQuarantineLifted(true)}>
            Lift quarantine (demo)
          </Button>
        ) : (
          <Button variant="outlined" onClick={() => setQuarantineLifted(false)} sx={{ borderColor: 'rgba(255,255,255,0.2)', color: 'text.primary' }}>
            Re-quarantine
          </Button>
        )}
      </Box>

      <Grid container spacing={2}>
        {MEMORY_ENTRIES.map((m) => {
          const isPoisoned = m.trust === 'quarantined';
          return (
            <Grid item xs={12} md={6} key={m.id}>
              <Panel sx={{ height: '100%', border: isPoisoned && !quarantineLifted ? '1px solid rgba(240,75,93,0.45)' : undefined }}>
                <Box sx={{ display: 'flex', gap: 0.75, alignItems: 'center', flexWrap: 'wrap' }}>
                  <Typography className="mono" variant="caption" color="text.secondary">{m.id}</Typography>
                  <Tag>{m.kind.toUpperCase()}</Tag>
                  <Tag tone={TRUST_TONE[m.trust]}>{isPoisoned && quarantineLifted ? 'QUARANTINE LIFTED' : m.trust.toUpperCase()}</Tag>
                  <Typography variant="caption" color="text.secondary" sx={{ ml: 'auto' }}>written {m.written}</Typography>
                </Box>
                <Typography sx={{ mt: 1.5, lineHeight: 1.6, fontWeight: isPoisoned ? 600 : 400 }}>{m.text}</Typography>
                <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1.25 }}>
                  Source: {m.source}
                </Typography>
              </Panel>
            </Grid>
          );
        })}
      </Grid>
    </Box>
  );
}
