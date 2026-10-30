import { Box, Button, Grid, Typography } from '@mui/material';
import { Download, FileCheck2, ScrollText } from 'lucide-react';
import { AUDIT_EVENTS } from '../../unified/platformData';
import { DemoBanner, Meter, Panel, Tag } from '../../unified/ui';
import { downloadText } from '../../unified/download';
import { ACCENT } from '../../theme';

const RESULT_TONE: Record<string, 'accent' | 'danger' | 'warn' | 'grey'> = {
  allowed: 'grey', blocked: 'danger', approved: 'accent', flagged: 'warn',
};

function auditCsv(): string {
  const rows = [['time', 'actor', 'actor_type', 'action', 'target', 'result'].join(',')];
  AUDIT_EVENTS.forEach((e) => rows.push([e.time, `"${e.actor}"`, e.actorType, `"${e.action}"`, `"${e.target}"`, e.result].join(',')));
  return rows.join('\n');
}

function complianceReport(kind: 'DPDP' | 'CERT-In'): string {
  return [
    `KAISEN UNIFIED — ${kind} COMPLIANCE SUMMARY (DEMO DATA)`,
    `Generated: ${new Date().toLocaleString('en-IN')}`,
    `Workspace server: vps-blr-01 · Agent: Northwind Support Agent`,
    ``,
    kind === 'CERT-In'
      ? `Log retention: day 132 of 180 (CERT-In direction: logs retained 180 days).`
      : `Personal-data access is logged per agent action with actor, target and result — the DPDP accountability trail.`,
    `Incidents in period: INC-1042 (open), INC-1051 (contained), INC-1057 (contained), INC-1033 (review).`,
    `Blocked actions in period: 24 · Operator approvals recorded: 3 · Exports generated: this file.`,
    ``,
    `Audit events (today):`,
    ...AUDIT_EVENTS.map((e) => `- ${e.time} · ${e.actor} · ${e.action} → ${e.target} · ${e.result}`),
    ``,
    `Note: exhibition build — figures are demo data shaped to the real report format.`,
  ].join('\n');
}

// AUDIT & COMPLIANCE — the DPDP / CERT-In story. Exports generate REAL
// downloadable files from the demo data on screen.
export default function AuditPage() {
  return (
    <Box>
      <Box sx={{ mb: 2.5, maxWidth: 780 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.25 }}>
          <ScrollText size={24} color={ACCENT} />
          <Typography variant="h4">Audit & Compliance</Typography>
        </Box>
        <Typography color="text.secondary" sx={{ mt: 0.75 }}>
          Who accessed what, when — agent, user, operator, or Kaisen itself. This is the log a DPDP
          auditor or a CERT-In incident report is built from, and it is kept for 180 days.
        </Typography>
      </Box>

      <DemoBanner />

      <Grid container spacing={2} sx={{ mb: 2 }}>
        <Grid item xs={12} md={4}>
          <Panel title="Log retention — CERT-In">
            <Meter label="Retention window" value={132} max={180} display="day 132 / 180" />
            <Typography variant="body2" color="text.secondary">
              CERT-In directions require 180 days of logs. On the Free plan retention is 7 days —
              this meter is exactly what upgrading buys.
            </Typography>
          </Panel>
        </Grid>
        <Grid item xs={12} md={4}>
          <Panel title="DPDP report">
            <FileCheck2 size={20} color={ACCENT} />
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1, mb: 1.75 }}>
              Personal-data access by every agent, with actor, target and outcome — the accountability
              trail the DPDP Act expects (core duties land 13 May 2027).
            </Typography>
            <Button variant="contained" size="small" startIcon={<Download size={13} />} onClick={() => downloadText('kaisen-dpdp-summary.txt', complianceReport('DPDP'))} sx={{ bgcolor: ACCENT, color: '#FCFFFF', fontWeight: 700, '&:hover': { bgcolor: '#4DB6E8' } }}>
              Export DPDP summary
            </Button>
          </Panel>
        </Grid>
        <Grid item xs={12} md={4}>
          <Panel title="CERT-In incident report">
            <FileCheck2 size={20} color={ACCENT} />
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1, mb: 1.75 }}>
              Incident summary in the shape CERT-In's 6-hour reporting expects — timeline, evidence,
              containment decision, approver.
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
              <Button variant="contained" size="small" startIcon={<Download size={13} />} onClick={() => downloadText('kaisen-certin-summary.txt', complianceReport('CERT-In'))} sx={{ bgcolor: ACCENT, color: '#FCFFFF', fontWeight: 700, '&:hover': { bgcolor: '#4DB6E8' } }}>
                Export CERT-In summary
              </Button>
              <Button variant="outlined" size="small" startIcon={<Download size={13} />} onClick={() => downloadText('kaisen-audit-log.csv', auditCsv(), 'text/csv')} sx={{ borderColor: 'rgba(255,255,255,0.2)', color: 'text.primary' }}>
                Audit log CSV
              </Button>
            </Box>
          </Panel>
        </Grid>
      </Grid>

      <Panel title="Audit log — today (demo data)">
        <Box sx={{ display: 'grid', gridTemplateColumns: '0.7fr 1.6fr 1.7fr 1.5fr 0.8fr', gap: 1.5, pb: 1.25, borderBottom: '1px solid rgba(255,255,255,0.09)' }}>
          {['Time', 'Actor', 'Action', 'Target', 'Result'].map((h) => (
            <Typography key={h} variant="caption" sx={{ textTransform: 'uppercase', letterSpacing: '0.11em', color: 'text.secondary', fontWeight: 650 }}>{h}</Typography>
          ))}
        </Box>
        {AUDIT_EVENTS.map((e, i) => (
          <Box key={i} className="kaisen-rise" sx={{ display: 'grid', gridTemplateColumns: '0.7fr 1.6fr 1.7fr 1.5fr 0.8fr', gap: 1.5, alignItems: 'center', py: 1.15, borderBottom: '1px solid rgba(255,255,255,0.05)', '&:last-child': { borderBottom: 'none' } }}>
            <Typography className="mono" variant="body2" color="text.secondary">{e.time}</Typography>
            <Box>
              <Typography variant="body2" sx={{ fontWeight: 560 }}>{e.actor}</Typography>
              <Typography variant="caption" color="text.secondary">{e.actorType}</Typography>
            </Box>
            <Typography variant="body2">{e.action}</Typography>
            <Typography variant="body2" className="mono" color="text.secondary" sx={{ fontSize: '0.8rem' }}>{e.target}</Typography>
            <Box><Tag tone={RESULT_TONE[e.result]}>{e.result.toUpperCase()}</Tag></Box>
          </Box>
        ))}
      </Panel>
    </Box>
  );
}
