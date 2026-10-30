import { useState } from 'react';
import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  Grid,
  Typography,
} from '@mui/material';
import PauseCircleOutlineIcon from '@mui/icons-material/PauseCircleOutline';
import PlayCircleOutlineIcon from '@mui/icons-material/PlayCircleOutline';
import BlockIcon from '@mui/icons-material/Block';
import ShieldOutlinedIcon from '@mui/icons-material/ShieldOutlined';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';
import { useCockpit, currentFrame, isContained, InterventionKind } from '../../unified/cockpitStore';
import { CONTEXT_LIMIT, SESSION, TOKEN_BUDGET, TOOL_BUDGET } from '../../unified/scenario';
import { AnimatedNumber, DemoBanner, Meter, Panel, ProLock, ScenarioControls, Tag } from '../../unified/ui';
import { useAuth } from '../../unified/authStore';
import { ACCENT, FONT_DISPLAY } from '../../theme';

const RESULT_TONE: Record<string, 'accent' | 'warn' | 'danger' | 'grey'> = {
  ok: 'accent',
  flagged: 'warn',
  failed: 'warn',
  blocked: 'danger',
};

const KIND_LABEL: Record<string, string> = {
  system: 'SYSTEM',
  user: 'USER',
  memory: 'MEMORY',
  file: 'FILE',
  'tool-result': 'TOOL RESULT',
};

export default function AgentCockpit() {
  const cockpit = useCockpit();
  const frame = currentFrame(cockpit);
  const contained = isContained(cockpit);
  const demo = cockpit.demoActive;
  const [confirm, setConfirm] = useState<InterventionKind | null>(null);
  const trifectaLegs = {
    privateData: frame.filesTouched.length > 0 || frame.contextItems.some((c) => c.kind === 'file'),
    untrusted: frame.contextItems.some((c) => c.flagged) || frame.toolCalls.some((tc) => tc.result === 'flagged'),
    external: frame.toolCalls.some((tc) => tc.tool === 'http_post' || tc.tool === 'send_email'),
  };
  const trifectaCount = [trifectaLegs.privateData, trifectaLegs.untrusted, trifectaLegs.external].filter(Boolean).length;
  const trifectaState = trifectaCount >= 3 ? 'LETHAL TRIFECTA' : trifectaCount === 2 ? 'EXPOSED' : 'SAFE';
  const isFree = useAuth((s) => s.plan) === 'free';

  const status = cockpit.sessionTerminated
    ? { label: 'TERMINATED', tone: 'danger' as const, dot: '#f04b5d' }
    : cockpit.agentPaused
      ? { label: 'PAUSED BY OPERATOR', tone: 'warn' as const, dot: '#f5a524' }
      : demo
        ? frame.threat === 'CRITICAL'
          ? { label: 'UNDER ATTACK — ESCALATED', tone: 'danger' as const, dot: '#f04b5d' }
          : { label: 'ACTIVE — WORKING', tone: 'accent' as const, dot: ACCENT }
        : { label: 'IDLE — NO LIVE SESSION', tone: 'grey' as const, dot: '#5D7280' };

  const confirmCopy: Record<InterventionKind, { title: string; body: string; cta: string }> = {
    pause: {
      title: cockpit.agentPaused ? 'Resume the agent?' : 'Pause the agent?',
      body: cockpit.agentPaused
        ? 'The agent will resume the session from where it stopped. This approval is written to the audit log.'
        : 'The agent stops taking new actions immediately. Its context and session state are preserved. This approval is written to the audit log.',
      cta: cockpit.agentPaused ? 'Approve — resume agent' : 'Approve — pause agent',
    },
    terminate: {
      title: 'Terminate this session?',
      body: `Session ${SESSION.sessionId} ends now and cannot be resumed. The user is disconnected and the full transcript is sealed into the audit log. This approval is written to the audit log.`,
      cta: 'Approve — terminate session',
    },
    isolate: {
      title: 'Isolate host vps-blr-01?',
      body: 'All non-management network traffic to and from the host is cut. Other services on this server go offline until you lift isolation. This approval is written to the audit log.',
      cta: 'Approve — isolate host',
    },
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', mb: 2.5, flexWrap: 'wrap', gap: 2 }}>
        <Box>
          <Typography variant="h4">Agent Cockpit</Typography>
          <Typography color="text.secondary" sx={{ mt: 0.5 }}>
            The harness view — what the agent is doing, which tools it used, what it remembers, and what it costs. Live.
          </Typography>
        </Box>
        <ScenarioControls />
      </Box>

      {demo && <DemoBanner />}
      {!demo && (
        <Box sx={{ mb: 2, p: 1.75, borderRadius: '10px', border: '1px solid rgba(255,255,255,0.1)', bgcolor: 'rgba(255,255,255,0.03)' }}>
          <Typography variant="body2" color="text.secondary">
            No live agent session is connected right now. The panels below fill with real session telemetry
            (the repo's <span className="mono">agent_telemetry</span> schema) once an agent is wired to Kaisen —
            or press <strong style={{ color: '#FCFFFF' }}>Replay incident scenario</strong> to watch a full session unfold.
          </Typography>
        </Box>
      )}

      <Grid container spacing={2}>
        {/* ——— left: agent identity + right now ——— */}
        <Grid item xs={12} lg={3}>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <Panel title="Agent">
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 1.5 }}>
                <Box className={status.tone === 'accent' ? 'kaisen-dot-live' : status.tone === 'danger' ? 'kaisen-dot-danger' : undefined}
                  sx={{ width: 12, height: 12, borderRadius: '50%', bgcolor: status.dot, flexShrink: 0 }} />
                <Box>
                  <Typography sx={{ fontFamily: FONT_DISPLAY, fontWeight: 680, fontSize: '1.05rem', lineHeight: 1.2 }}>{SESSION.agentName}</Typography>
                  <Typography variant="caption" color="text.secondary">{SESSION.agentRole}</Typography>
                </Box>
              </Box>
              <Tag tone={status.tone}>{status.label}</Tag>
              <Box sx={{ mt: 2, display: 'grid', gap: 0.9 }}>
                {[
                  ['Session', SESSION.sessionId],
                  ['Host', SESSION.nodeId],
                  ['Model', SESSION.model],
                  ['Session started', SESSION.startedAt],
                  ['Jailbreak phase', demo ? frame.phase : '—'],
                  ['Scenario clock', demo ? frame.clock : '—'],
                ].map(([k, v]) => (
                  <Box key={k} sx={{ display: 'flex', justifyContent: 'space-between', gap: 1 }}>
                    <Typography variant="caption" color="text.secondary">{k}</Typography>
                    <Typography variant="caption" className="mono" sx={{ fontWeight: 600, textAlign: 'right' }}>{v}</Typography>
                  </Box>
                ))}
              </Box>
              <Box sx={{ mt: 2, display: 'flex', gap: 0.75, flexWrap: 'wrap' }}>
                {cockpit.agentPaused && <Tag tone="warn">PAUSED</Tag>}
                {cockpit.sessionTerminated && <Tag tone="danger">SESSION TERMINATED</Tag>}
                {cockpit.hostIsolated && <Tag tone="danger">HOST ISOLATED</Tag>}
                {contained && <Tag tone="accent">INCIDENT CONTAINED</Tag>}
              </Box>
            </Panel>

            <Panel title="Right now">
              <Typography sx={{ fontWeight: 620, mb: 0.75 }}>{demo ? frame.currentTask : 'Waiting for a session…'}</Typography>
              <Typography variant="body2" color="text.secondary" className={demo ? 'kaisen-rise' : undefined} key={frame.narrative}>
                {demo ? frame.narrative : 'When a monitored agent starts working, its current task and a plain-language narration of its latest action appear here.'}
              </Typography>
            </Panel>

            <Panel title="Session & budget">
              <Meter label="Tokens used (session budget)" value={demo ? frame.tokensUsed : 0} max={TOKEN_BUDGET} display={`${(demo ? frame.tokensUsed : 0).toLocaleString('en-IN')} / ${TOKEN_BUDGET.toLocaleString('en-IN')}`} dangerAbove={80} />
              <Meter label="Tool calls (session budget)" value={demo ? frame.toolCallsUsed : 0} max={TOOL_BUDGET} display={`${demo ? frame.toolCallsUsed : 0} / ${TOOL_BUDGET}`} dangerAbove={80} />
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 0.5 }}>
                <Typography variant="caption" color="text.secondary">Estimated session cost</Typography>
                <Typography className="mono" sx={{ fontWeight: 680 }}>
                  ₹<AnimatedNumber value={demo ? frame.sessionCostInr : 0} decimals={1} />
                </Typography>
              </Box>
              <Typography variant="caption" color="text.secondary">
                Budgets are enforced by the gateway — a runaway or hijacked agent hits the cap, not your wallet.
              </Typography>
            </Panel>
          </Box>
        </Grid>

        {/* ——— centre: tool-call feed + files ——— */}
        <Grid item xs={12} lg={5}>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <Panel title={`Live tool-call feed ${demo ? `· ${frame.toolCalls.length} calls` : ''}`} right={demo ? <Tag tone="warn">DEMO DATA</Tag> : undefined}>
              {frame.toolCalls.length === 0 || !demo ? (
                <Typography variant="body2" color="text.secondary" sx={{ py: 2 }}>
                  No tool calls yet. Every tool the agent invokes — name, arguments, result, duration — streams here in order.
                </Typography>
              ) : (
                <Box sx={{ display: 'flex', flexDirection: 'column' }}>
                  {[...frame.toolCalls].reverse().map((tc) => (
                    <Box key={tc.id} className="kaisen-rise" sx={{ display: 'flex', gap: 1.5, py: 1.1, borderBottom: '1px solid rgba(255,255,255,0.06)', '&:last-child': { borderBottom: 'none' } }}>
                      <Typography className="mono" variant="caption" color="text.secondary" sx={{ pt: 0.3, minWidth: 52 }}>{tc.time}</Typography>
                      <Box sx={{ flex: 1, minWidth: 0 }}>
                        <Box sx={{ display: 'flex', gap: 1, alignItems: 'center', flexWrap: 'wrap' }}>
                          <Typography className="mono" sx={{ fontWeight: 680, fontSize: '0.85rem' }}>{tc.tool}</Typography>
                          <Tag tone={RESULT_TONE[tc.result]}>{tc.result.toUpperCase()}</Tag>
                          <Typography variant="caption" color="text.secondary" className="mono">{tc.durationMs} ms</Typography>
                        </Box>
                        <Typography variant="caption" className="mono" color="text.secondary" sx={{ display: 'block', mt: 0.3, wordBreak: 'break-all' }}>
                          {tc.args}
                        </Typography>
                      </Box>
                    </Box>
                  ))}
                </Box>
              )}
            </Panel>

            <Panel title="Files the agent touched">
              {!demo || frame.filesTouched.length === 0 ? (
                <Typography variant="body2" color="text.secondary">No file access in this session yet.</Typography>
              ) : (
                frame.filesTouched.map((f) => (
                  <Box key={f.path} className="kaisen-rise" sx={{ display: 'flex', justifyContent: 'space-between', gap: 1, py: 0.9, borderBottom: '1px solid rgba(255,255,255,0.06)', '&:last-child': { borderBottom: 'none' } }}>
                    <Typography className="mono" variant="body2" sx={{ color: f.flagged ? 'error.main' : 'text.primary', fontWeight: f.flagged ? 650 : 400 }}>{f.path}</Typography>
                    <Typography variant="caption" color="text.secondary" sx={{ textAlign: 'right' }}>{f.action}</Typography>
                  </Box>
                ))
              )}
            </Panel>
          </Box>
        </Grid>

        {/* ——— right: memory, SHAP, interventions ——— */}
        <Grid item xs={12} lg={4}>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <Panel title="Memory & context window" right={isFree ? <ProLock /> : demo ? <Tag tone="warn">DEMO DATA</Tag> : undefined}>
              <Meter
                label="Context window usage"
                value={demo ? frame.contextTokens : 0}
                max={CONTEXT_LIMIT}
                display={`${(demo ? frame.contextTokens : 0).toLocaleString('en-IN')} / ${CONTEXT_LIMIT.toLocaleString('en-IN')} tok`}
                dangerAbove={75}
              />
              {!demo ? (
                <Typography variant="body2" color="text.secondary">Context items appear here as the agent loads them.</Typography>
              ) : (
                frame.contextItems.map((item) => (
                  <Box key={item.id} className="kaisen-rise" sx={{ display: 'flex', justifyContent: 'space-between', gap: 1, py: 0.85, px: 1, mb: 0.75, borderRadius: '8px', border: `1px solid ${item.flagged ? 'rgba(240,75,93,0.45)' : 'rgba(255,255,255,0.07)'}`, bgcolor: item.flagged ? 'rgba(240,75,93,0.05)' : 'rgba(255,255,255,0.02)' }}>
                    <Box sx={{ minWidth: 0 }}>
                      <Tag tone={item.flagged ? 'danger' : 'grey'}>{KIND_LABEL[item.kind]}</Tag>
                      <Typography variant="body2" sx={{ mt: 0.5, fontWeight: item.flagged ? 620 : 400 }}>{item.label}</Typography>
                    </Box>
                    <Typography variant="caption" className="mono" color="text.secondary" sx={{ whiteSpace: 'nowrap', pt: 0.4 }}>
                      {item.tokens.toLocaleString('en-IN')} tok
                    </Typography>
                  </Box>
                ))
              )}
            </Panel>

            <Panel title="Lethal trifecta — this session" right={demo ? <Tag tone={trifectaState === 'LETHAL TRIFECTA' ? 'danger' : trifectaState === 'EXPOSED' ? 'warn' : 'accent'}>{trifectaState}</Tag> : undefined}>
              {!demo ? (
                <Typography variant="body2" color="text.secondary">
                  Willison's lethal trifecta (2025): an agent session is exploitable when it combines private-data
                  access, untrusted input, and external communication. Kaisen scores all three, live, per session.
                </Typography>
              ) : (
                <>
                  {[
                    ['Access to private data', trifectaLegs.privateData, 'files / records touched'],
                    ['Exposure to untrusted content', trifectaLegs.untrusted, 'flagged prompt, tool output or memory'],
                    ['External communication', trifectaLegs.external, 'outbound tool calls attempted'],
                  ].map(([label, on, sub]) => (
                    <Box key={label as string} sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', py: 0.7, borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                      <Box>
                        <Typography variant="body2" sx={{ fontWeight: 560 }}>{label}</Typography>
                        <Typography variant="caption" color="text.secondary">{sub}</Typography>
                      </Box>
                      <Tag tone={on ? 'danger' : 'grey'}>{on ? 'PRESENT' : 'absent'}</Tag>
                    </Box>
                  ))}
                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1.25 }}>
                    {trifectaState === 'LETHAL TRIFECTA'
                      ? 'All three legs are present in one session — this is the exact configuration almost every 2025 agent breach needed.'
                      : trifectaState === 'EXPOSED'
                        ? 'Two legs present. One more and this session becomes fully exploitable — Kaisen is watching the third.'
                        : 'The full trifecta has not formed in this session yet.'}
                  </Typography>
                </>
              )}
            </Panel>

            <Panel title="Why — SHAP-style explanation" right={isFree ? <ProLock /> : undefined}>
              <Typography variant="body2" sx={{ mb: 1.5 }}>
                {demo ? frame.shapReason : 'Every intervention ships with the signals that drove it, in plain language.'}
              </Typography>
              {demo && frame.shap.map((f) => (
                <Box key={f.feature} sx={{ mb: 1.1 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="caption">{f.description}</Typography>
                    <Typography variant="caption" className="mono" sx={{ fontWeight: 650, color: f.value >= 0 ? 'error.main' : 'text.secondary' }}>
                      {f.value >= 0 ? '+' : ''}{f.value.toFixed(2)}
                    </Typography>
                  </Box>
                  <Box sx={{ height: 5, borderRadius: 999, bgcolor: 'rgba(255,255,255,0.07)', mt: 0.4 }}>
                    <Box sx={{ height: '100%', width: `${Math.min(100, (Math.abs(f.value) / 0.35) * 100)}%`, borderRadius: 999, bgcolor: f.value >= 0 ? 'error.main' : '#546A77', transition: 'width 650ms cubic-bezier(0.22,1,0.36,1)' }} />
                  </Box>
                  <Typography variant="caption" className="mono" color="text.secondary">{f.feature}</Typography>
                </Box>
              ))}
            </Panel>

            <Panel title="Interventions — human approval required" right={isFree ? <ProLock /> : undefined}>
              {demo && frame.suggestedAction && !contained && (
                <Box sx={{ mb: 1.5, p: 1.25, borderRadius: '8px', border: '1px solid rgba(240,75,93,0.45)', bgcolor: 'rgba(240,75,93,0.06)' }}>
                  <Typography variant="body2" sx={{ fontWeight: 650, color: 'error.main' }}>Recommended by Kaisen</Typography>
                  <Typography variant="body2" color="text.secondary">{frame.suggestedAction}</Typography>
                </Box>
              )}
              <Box sx={{ display: 'grid', gap: 1 }}>
                <Button variant="outlined" startIcon={cockpit.agentPaused ? <PlayCircleOutlineIcon /> : <PauseCircleOutlineIcon />} onClick={() => setConfirm('pause')} disabled={!demo || cockpit.sessionTerminated} sx={{ justifyContent: 'flex-start', borderColor: 'rgba(255,255,255,0.18)', color: 'text.primary' }}>
                  {cockpit.agentPaused ? 'Resume agent' : 'Pause agent'}
                </Button>
                <Button variant="outlined" color="error" startIcon={<BlockIcon />} onClick={() => setConfirm('terminate')} disabled={!demo || cockpit.sessionTerminated} sx={{ justifyContent: 'flex-start' }}>
                  {cockpit.sessionTerminated ? 'Session terminated' : 'Terminate session'}
                </Button>
                <Button variant="outlined" color="error" startIcon={<ShieldOutlinedIcon />} onClick={() => setConfirm('isolate')} disabled={!demo || cockpit.hostIsolated} sx={{ justifyContent: 'flex-start' }}>
                  {cockpit.hostIsolated ? 'Host isolated' : 'Isolate host'}
                </Button>
              </Box>
              <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1.25 }}>
                Kaisen recommends. A human approves. Nothing here fires automatically.
              </Typography>
              {cockpit.interventions.length > 0 && (
                <Box sx={{ mt: 1.5, pt: 1.5, borderTop: '1px solid rgba(255,255,255,0.08)' }}>
                  <Typography variant="caption" sx={{ textTransform: 'uppercase', letterSpacing: '0.1em', color: 'text.secondary', fontWeight: 650 }}>Audit log</Typography>
                  {cockpit.interventions.map((iv) => (
                    <Box key={iv.id} className="kaisen-rise" sx={{ display: 'flex', gap: 1, alignItems: 'center', mt: 1 }}>
                      <CheckCircleOutlineIcon sx={{ fontSize: 16, color: 'primary.main' }} />
                      <Typography variant="body2">{iv.label}</Typography>
                      <Typography variant="caption" className="mono" color="text.secondary">{iv.time} · {iv.approvedBy}</Typography>
                    </Box>
                  ))}
                </Box>
              )}
            </Panel>
          </Box>
        </Grid>
      </Grid>

      <Dialog open={confirm !== null} onClose={() => setConfirm(null)} PaperProps={{ sx: { bgcolor: '#060D12', border: '1px solid rgba(255,255,255,0.12)', borderRadius: '14px' } }}>
        {confirm && (
          <>
            <DialogTitle sx={{ fontWeight: 680 }}>{confirmCopy[confirm].title}</DialogTitle>
            <DialogContent>
              <DialogContentText color="text.secondary">{confirmCopy[confirm].body}</DialogContentText>
            </DialogContent>
            <DialogActions sx={{ px: 3, pb: 2.5 }}>
              <Button onClick={() => setConfirm(null)} sx={{ color: 'text.secondary' }}>Cancel</Button>
              <Button
                variant="contained"
                color={confirm === 'pause' ? 'primary' : 'error'}
                onClick={() => { cockpit.applyIntervention(confirm); setConfirm(null); }}
              >
                {confirmCopy[confirm].cta}
              </Button>
            </DialogActions>
          </>
        )}
      </Dialog>
    </Box>
  );
}
