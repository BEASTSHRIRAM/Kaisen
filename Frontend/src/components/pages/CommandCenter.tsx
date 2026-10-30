import { Box, Button, Grid, Typography } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useStore } from '../../store/useStore';
import { useAuth } from '../../unified/authStore';
import { useCockpit, currentFrame, currentGraph, currentScenario, isContained } from '../../unified/cockpitStore';
import {
  AnimatedNumber,
  ProLock,
  AttackGraphSvg,
  DemoBanner,
  Panel,
  ScenarioControls,
  Sparkline,
  Tag,
} from '../../unified/ui';
import { ACCENT, HIGHLIGHT, FONT_DISPLAY } from '../../theme';

const LAYER_TONE: Record<string, 'grey' | 'accent' | 'danger' | 'warn'> = {
  PROMPT: 'warn',
  AGENT: 'warn',
  HOST: 'danger',
  CORRELATION: 'danger',
};

export default function CommandCenter() {
  const navigate = useNavigate();
  const cockpit = useCockpit();
  const { currentMetrics, metricsHistory, alerts, attackGraph, connectionStatus } = useStore();
  const frame = currentFrame(cockpit);
  const contained = isContained(cockpit);
  const demo = cockpit.demoActive;
  const isFree = useAuth((s) => s.plan) === 'free';

  // Live backend data wins when connected and the replay is not running.
  const liveSeries = metricsHistory.slice(-24);
  const scenario = currentScenario(cockpit);
  const playedFrames = scenario.frames.slice(0, cockpit.frameIndex + 1);
  const cpuSeries = demo ? playedFrames.map((f) => f.metric.cpu) : liveSeries.map((m) => m.cpu_usage);
  const connSeries = demo ? playedFrames.map((f) => f.metric.connections) : liveSeries.map((m) => m.network_connections);

  const anomaly = demo ? frame.anomalyScore : currentMetrics?.anomaly_score ?? 0;
  const threat = contained ? 'CONTAINED' : demo ? frame.threat : anomaly >= 0.7 ? 'CRITICAL' : anomaly >= 0.4 ? 'ELEVATED' : 'LOW';
  const threatTone = threat === 'CRITICAL' ? 'danger' : threat === 'CONTAINED' ? 'accent' : threat === 'ELEVATED' || threat === 'GUARDED' ? 'warn' : 'accent';
  const graph = demo ? currentGraph(cockpit) : attackGraph;

  const stats: { label: string; value: React.ReactNode; sub: string }[] = [
    {
      label: 'Threat level',
      value: <span style={{ color: threat === 'CRITICAL' ? '#f04b5d' : threat === 'CONTAINED' ? ACCENT : '#FCFFFF' }}>{threat}</span>,
      sub: demo ? `Jailbreak phase: ${frame.phase}` : connectionStatus.connected ? 'Live host telemetry' : 'Backend offline',
    },
    {
      label: 'Joint anomaly score',
      value: <span style={{ color: demo && anomaly >= 0.7 && !contained ? HIGHLIGHT : undefined }}><AnimatedNumber value={anomaly} decimals={2} /></span>,
      sub: 'Agent layer × host layer (arbiter)',
    },
    {
      label: demo ? 'Incident' : 'Open alerts',
      value: demo ? scenario.incidentId : <AnimatedNumber value={alerts.length} />,
      sub: demo ? `Attack Lab · ${scenario.name}` : 'From the live alert engine',
    },
    {
      label: 'Host · vps-blr-01',
      value: cockpit.hostIsolated ? 'ISOLATED' : 'MONITORED',
      sub: demo ? `Connections ${frame.metric.connections} · CPU ${frame.metric.cpu}%` : currentMetrics ? `CPU ${currentMetrics.cpu_usage.toFixed(0)}% · ${currentMetrics.network_connections} connections` : 'Waiting for collector',
    },
  ];

  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', mb: 2.5, flexWrap: 'wrap', gap: 2 }}>
        <Box>
          <Typography variant="h4">Command Center</Typography>
          <Typography color="text.secondary" sx={{ mt: 0.5 }}>
            One attack. One story. Kaisen watches the AI agent <em>and</em> the machine it runs on — together.
          </Typography>
        </Box>
        <ScenarioControls />
      </Box>

      {demo && <DemoBanner />}

      {/* status strip */}
      <Grid container spacing={2} sx={{ mb: 2 }}>
        {stats.map((s) => (
          <Grid item xs={12} sm={6} lg={3} key={s.label}>
            <Panel>
              <Typography variant="caption" sx={{ textTransform: 'uppercase', letterSpacing: '0.12em', color: 'text.secondary', fontWeight: 650 }}>
                {s.label}
              </Typography>
              <Typography sx={{ fontFamily: FONT_DISPLAY, fontSize: '1.7rem', fontWeight: 680, letterSpacing: '-0.02em', mt: 0.75, lineHeight: 1.1 }}>
                {s.value}
              </Typography>
              <Typography variant="caption" color="text.secondary">{s.sub}</Typography>
            </Panel>
          </Grid>
        ))}
      </Grid>

      <Grid container spacing={2}>
        {/* hero: correlated incident story */}
        <Grid item xs={12} lg={7}>
          <Panel
            title="Correlated incident story"
            sx={demo && frame.incidentSteps.length > 0 && !contained ? { border: '1px solid rgba(252,115,77,0.45)' } : undefined}
            right={<Box sx={{ display: 'flex', gap: 0.75 }}>{isFree && <ProLock />}{demo ? (contained ? <Tag tone={threatTone as any}>{'CONTAINED — operator approved'}</Tag> : (
              <Box component="span" sx={{ display: 'inline-flex', alignItems: 'center', px: 0.85, py: 0.3, borderRadius: '6px', border: '1px solid rgba(252,115,77,0.55)', backgroundColor: 'rgba(252,115,77,0.1)', color: HIGHLIGHT, fontSize: '0.68rem', fontWeight: 700, letterSpacing: '0.04em', whiteSpace: 'nowrap' }}>
                {scenario.incidentId} · {threat}
              </Box>
            )) : <Tag>Live</Tag>}</Box>}
          >
            {frame.incidentSteps.length === 0 && (
              <Box sx={{ py: 1 }}>
                <Typography variant="h6" sx={{ mb: 1 }}>No correlated incident right now.</Typography>
                <Typography color="text.secondary" sx={{ mb: 2, maxWidth: 560 }}>
                  Kaisen only raises an incident when a suspicious <strong>agent</strong> event and a suspicious{' '}
                  <strong>host</strong> event land in the same window — so one real attack becomes one story,
                  not a wall of unrelated alerts. Run the replay to watch a full
                  prompt-injection → file-access → exfiltration chain get correlated live.
                </Typography>
                {!demo && <ScenarioControls size="small" />}
                {demo && (
                  <Typography color="text.secondary">Replay running — the agent is working normally… for now.</Typography>
                )}
              </Box>
            )}
            <Box sx={{ position: 'relative', pl: 0.5 }}>
              {frame.incidentSteps.map((step, i) => (
                <Box key={step.id} className="kaisen-rise" sx={{ display: 'flex', gap: 2, pb: i === frame.incidentSteps.length - 1 ? 0 : 2.5, position: 'relative' }}>
                  {i < frame.incidentSteps.length - 1 && (
                    <Box sx={{ position: 'absolute', left: 15, top: 34, bottom: 0, width: '1px', bgcolor: 'rgba(255,255,255,0.12)' }} />
                  )}
                  <Box
                    className={step.layer === 'CORRELATION' ? 'kaisen-dot-danger' : undefined}
                    sx={{
                      width: 31, height: 31, borderRadius: '50%', flexShrink: 0, zIndex: 1,
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      border: step.layer === 'CORRELATION' ? `1px solid ${HIGHLIGHT}` : '1px solid rgba(255,255,255,0.2)',
                      bgcolor: step.layer === 'CORRELATION' ? HIGHLIGHT : '#0A1218',
                      color: step.layer === 'CORRELATION' ? '#200D04' : undefined,
                      fontSize: '0.72rem', fontWeight: 700,
                    }}
                  >
                    {i + 1}
                  </Box>
                  <Box sx={{ pt: 0.4 }}>
                    <Box sx={{ display: 'flex', gap: 1, alignItems: 'center', flexWrap: 'wrap' }}>
                      <Typography className="mono" variant="caption" color="text.secondary">{step.time}</Typography>
                      <Tag tone={LAYER_TONE[step.layer]}>{step.layer}</Tag>
                      <Typography sx={{ fontWeight: 620 }}>{step.title}</Typography>
                    </Box>
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 0.6, maxWidth: 640 }}>
                      {step.detail}
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 0.75, mt: 0.9, flexWrap: 'wrap' }}>
                      {step.signals.map((sig) => (
                        <span key={sig} className="mono" style={{ fontSize: '0.68rem', color: '#93A8B5', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 6, padding: '2px 7px' }}>
                          {sig}
                        </span>
                      ))}
                    </Box>
                  </Box>
                </Box>
              ))}
            </Box>
            {demo && frame.suggestedAction && !contained && (
              <Box className="kaisen-rise" sx={{ mt: 2, p: 1.75, borderRadius: '10px', border: '1px solid rgba(240,75,93,0.5)', bgcolor: 'rgba(240,75,93,0.07)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 2, flexWrap: 'wrap' }}>
                <Box>
                  <Typography sx={{ fontWeight: 650, color: 'error.main' }}>Suggested action — needs a human</Typography>
                  <Typography variant="body2" color="text.secondary">{frame.suggestedAction}. Kaisen never acts on its own.</Typography>
                </Box>
                <Button variant="contained" color="error" onClick={() => navigate('/app/cockpit')}>
                  Review in Agent Cockpit →
                </Button>
              </Box>
            )}
            {contained && (
              <Box className="kaisen-rise" sx={{ mt: 2, p: 1.75, borderRadius: '10px', border: '1px solid rgba(2,151,222,0.5)', bgcolor: 'rgba(2,151,222,0.07)' }}>
                <Typography sx={{ fontWeight: 650, color: 'primary.main' }}>Incident contained</Typography>
                <Typography variant="body2" color="text.secondary">
                  Session terminated and host isolated — both approved by the operator in the Cockpit. The full chain is in the audit log.
                </Typography>
              </Box>
            )}
          </Panel>
        </Grid>

        {/* right column: graph + live metrics */}
        <Grid item xs={12} lg={5}>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <Panel title="Attack graph" right={demo ? <Tag tone="warn">DEMO DATA</Tag> : <Tag>{graph ? 'Live' : 'No data'}</Tag>}>
              {graph && graph.nodes.length > 0 ? (
                <AttackGraphSvg graph={graph} height={290} />
              ) : (
                <Box sx={{ py: 4, textAlign: 'center' }}>
                  <Typography color="text.secondary">
                    No graph yet. When the collector exports a graph — or the replay runs — the attack path renders here.
                  </Typography>
                </Box>
              )}
            </Panel>
            <Panel title="Live metrics" right={demo ? <Tag tone="warn">DEMO DATA</Tag> : undefined}>
              <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2 }}>
                <Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="caption" color="text.secondary">CPU %</Typography>
                    <Typography variant="caption" className="mono" sx={{ fontWeight: 650 }}>
                      <AnimatedNumber value={demo ? frame.metric.cpu : currentMetrics?.cpu_usage ?? 0} decimals={0} />
                    </Typography>
                  </Box>
                  <Sparkline data={cpuSeries.length ? cpuSeries : [0]} />
                </Box>
                <Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="caption" color="text.secondary">CONNECTIONS</Typography>
                    <Typography variant="caption" className="mono" sx={{ fontWeight: 650 }}>
                      <AnimatedNumber value={demo ? frame.metric.connections : currentMetrics?.network_connections ?? 0} />
                    </Typography>
                  </Box>
                  <Sparkline data={connSeries.length ? connSeries : [0]} color="#93A8B5" />
                </Box>
              </Box>
              <Typography variant="caption" color="text.secondary">
                {demo
                  ? 'Replay telemetry — shaped from the repo\'s host collector fields + jailbreak simulator.'
                  : connectionStatus.connected
                    ? 'Polling the Kaisen API every 2 seconds.'
                    : 'Backend offline. Start the Python API, or use the demo replay for the exhibition.'}
              </Typography>
            </Panel>
            <Panel title="Why Kaisen flagged it — top signals">
              {(demo ? frame.shap : []).slice(0, 3).map((f) => (
                <Box key={f.feature} sx={{ display: 'flex', justifyContent: 'space-between', py: 0.55 }}>
                  <Typography variant="body2">{f.description}</Typography>
                  <Typography variant="body2" className="mono" sx={{ color: f.value >= 0 ? 'error.main' : 'text.secondary', fontWeight: 650 }}>
                    SHAP {f.value >= 0 ? '+' : ''}{f.value.toFixed(2)}
                  </Typography>
                </Box>
              ))}
              {!demo && (
                <Typography variant="body2" color="text.secondary">
                  SHAP-style explanations attach to every intervention. Start the replay to see one build up,
                  or open the Agent Cockpit.
                </Typography>
              )}
              <Button size="small" sx={{ mt: 1, color: 'primary.main', px: 0 }} onClick={() => navigate('/app/cockpit')}>
                Open the Agent Cockpit →
              </Button>
            </Panel>
          </Box>
        </Grid>
      </Grid>
    </Box>
  );
}
