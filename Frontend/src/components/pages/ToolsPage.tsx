import { Box, MenuItem, Select, Typography } from '@mui/material';
import { Wrench } from 'lucide-react';
import { useTools } from '../../unified/toolStore';
import { PermissionMode, RiskLevel } from '../../unified/platformData';
import { DemoBanner, Panel, Tag } from '../../unified/ui';
import { ACCENT } from '../../theme';

const RISK_TONE: Record<RiskLevel, 'accent' | 'grey' | 'warn' | 'danger'> = {
  Low: 'accent', Medium: 'grey', High: 'warn', Critical: 'danger',
};

// TOOL REGISTRY & POLICIES — agent harness governance: every tool the agent
// may use, its risk, and who gets the final say. Mode changes apply to the
// local policy store immediately (demo state, labelled).
export default function ToolsPage() {
  const { tools, setMode } = useTools();
  const counts = {
    Allow: tools.filter((t) => t.mode === 'Allow').length,
    'Ask human': tools.filter((t) => t.mode === 'Ask human').length,
    Block: tools.filter((t) => t.mode === 'Block').length,
    blocked: tools.reduce((a, t) => a + t.blockedToday, 0),
  };

  return (
    <Box>
      <Box sx={{ mb: 2.5, maxWidth: 780 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.25 }}>
          <Wrench size={24} color={ACCENT} />
          <Typography variant="h4">Tool Registry & Policies</Typography>
        </Box>
        <Typography color="text.secondary" sx={{ mt: 0.75 }}>
          The agent can only do what its tools allow. Every tool is registered with a risk level and a
          permission mode — <strong style={{ color: '#FCFFFF' }}>Allow</strong>,{' '}
          <strong style={{ color: '#FCFFFF' }}>Ask human</strong>, or{' '}
          <strong style={{ color: '#FCFFFF' }}>Block</strong> — and MCP tools are hash-pinned at approval,
          so a server that silently edits a tool description gets caught (see INC-1057 in the Attack Lab).
          Change a mode and the gateway policy updates with it.
        </Typography>
      </Box>

      <DemoBanner />

      <Box sx={{ display: 'flex', gap: 1.25, mb: 2, flexWrap: 'wrap' }}>
        <Tag tone="accent">{counts.Allow} tools · Allow</Tag>
        <Tag tone="warn">{counts['Ask human']} tools · Ask human</Tag>
        <Tag tone="danger">{counts.Block} tools · Block</Tag>
        <Tag>{counts.blocked} calls blocked today (demo data)</Tag>
      </Box>

      <Panel>
        <Box sx={{ display: 'grid', gridTemplateColumns: '2.1fr 1.4fr 0.8fr 1.1fr 0.8fr 0.8fr', gap: 1.5, pb: 1.25, borderBottom: '1px solid rgba(255,255,255,0.09)' }}>
          {['Tool', 'Source', 'Risk', 'Permission mode', 'Calls today', 'Blocked'].map((h) => (
            <Typography key={h} variant="caption" sx={{ textTransform: 'uppercase', letterSpacing: '0.11em', color: 'text.secondary', fontWeight: 650 }}>{h}</Typography>
          ))}
        </Box>
        {tools.map((t) => (
          <Box key={t.name} className="kaisen-rise" sx={{ display: 'grid', gridTemplateColumns: '2.1fr 1.4fr 0.8fr 1.1fr 0.8fr 0.8fr', gap: 1.5, alignItems: 'center', py: 1.3, borderBottom: '1px solid rgba(255,255,255,0.05)', '&:last-child': { borderBottom: 'none' } }}>
            <Box>
              <Typography className="mono" sx={{ fontWeight: 650, fontSize: '0.86rem' }}>{t.name}</Typography>
              <Typography variant="caption" color="text.secondary">last used {t.lastUsed}</Typography>
            </Box>
            <Typography variant="body2" color="text.secondary">{t.source}</Typography>
            <Box><Tag tone={RISK_TONE[t.risk]}>{t.risk.toUpperCase()}</Tag></Box>
            <Select
              size="small"
              value={t.mode}
              onChange={(e) => setMode(t.name, e.target.value as PermissionMode)}
              sx={{
                fontSize: '0.8rem', fontWeight: 600,
                color: t.mode === 'Block' ? 'error.main' : t.mode === 'Ask human' ? 'warning.main' : 'primary.main',
                '& .MuiOutlinedInput-notchedOutline': { borderColor: 'rgba(255,255,255,0.16)' },
              }}
            >
              <MenuItem value="Allow">Allow</MenuItem>
              <MenuItem value="Ask human">Ask human</MenuItem>
              <MenuItem value="Block">Block</MenuItem>
            </Select>
            <Typography className="mono" variant="body2">{t.callsToday.toLocaleString('en-IN')}</Typography>
            <Typography className="mono" variant="body2" sx={{ color: t.blockedToday > 0 ? 'error.main' : 'text.secondary', fontWeight: t.blockedToday > 0 ? 650 : 400 }}>
              {t.blockedToday}
            </Typography>
          </Box>
        ))}
        <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1.75 }}>
          Demo build: mode changes apply to this console's policy store immediately. In production the same
          change is written to the gateway policy and audit-logged (see Audit & Compliance).
        </Typography>
      </Panel>
    </Box>
  );
}
