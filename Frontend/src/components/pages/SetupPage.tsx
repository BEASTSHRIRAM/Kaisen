import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Box, Button, CircularProgress, Typography } from '@mui/material';
import { Check, Copy, Server, Terminal } from 'lucide-react';
import { LogoLockup } from '../../unified/Logo';
import { useAuth, PLAN_LABEL } from '../../unified/authStore';
import { Tag } from '../../unified/ui';
import { ACCENT } from '../../theme';

// Initial Setup / onboarding — AWS-style "connect your server".
// HONESTY: the install command is the product's real onboarding shape, but
// in this exhibition build nothing is downloaded and no server connects —
// the heartbeat below is a labelled DEMO simulation.
type Phase = 'idle' | 'waiting' | 'connected';

export default function SetupPage() {
  const navigate = useNavigate();
  const { user, plan, completeSetup } = useAuth();
  const [tab, setTab] = useState<'shell' | 'docker'>('shell');
  const [copied, setCopied] = useState(false);
  const [phase, setPhase] = useState<Phase>('idle');

  const token = useMemo(() => {
    const seed = (user?.email || 'kaisen').split('').reduce((a, c) => a + c.charCodeAt(0), 0);
    const part = (n: number) => ((seed * (n + 7) * 2654435761) >>> 0).toString(16).toUpperCase().padStart(4, '0').slice(0, 4);
    return `KS-${part(1)}-${part(2)}`;
  }, [user]);

  const shellCmd = `curl -fsSL https://get.kaisen.dev/install.sh | sudo bash -s -- --token ${token}`;
  const dockerCmd = `docker run -d --name kaisen-agent --restart unless-stopped -e KAISEN_TOKEN=${token} -v /var/log:/host/log:ro kaisen/agent:latest`;
  const command = tab === 'shell' ? shellCmd : dockerCmd;

  useEffect(() => {
    if (!user) navigate('/login');
    else if (!plan) navigate('/welcome/plans');
  }, [user, plan, navigate]);

  useEffect(() => {
    if (phase !== 'waiting') return;
    const id = setTimeout(() => setPhase('connected'), 3600);
    return () => clearTimeout(id);
  }, [phase]);

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(command);
    } catch {
      const ta = document.createElement('textarea');
      ta.value = command;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand('copy');
      document.body.removeChild(ta);
    }
    setCopied(true);
    setTimeout(() => setCopied(false), 1800);
  };

  const steps = [
    { n: 1, title: 'Pick your plan', body: plan ? `Selected: ${PLAN_LABEL[plan]}` : 'Choose Free, Pro or Team.', done: Boolean(plan) },
    { n: 2, title: 'Run one command on your server', body: 'The Kaisen agent installs as a lightweight service, starts monitoring this server and the AI agents on it, and phones home with the token below — nothing else is exposed.', done: phase === 'connected' },
    { n: 3, title: 'First heartbeat unlocks your console', body: 'The moment your server checks in, the Command Center lights up with its live telemetry.', done: phase === 'connected' },
  ];

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default', py: 6, px: 3, overflowY: 'auto' }}>
      <Box sx={{ maxWidth: 760, mx: 'auto' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.25, mb: 4 }}>
          <LogoLockup size={34} />
          <Box sx={{ ml: 'auto' }}><Tag tone="warn">DEMO MODE — simulated connection</Tag></Box>
        </Box>

        <Typography variant="h4" sx={{ mb: 1 }}>Connect your server</Typography>
        <Typography color="text.secondary" sx={{ mb: 4, maxWidth: 620 }}>
          One command installs the agent on the server your AI runs on. Kaisen then watches the
          machine <em>and</em> the agent — together.
        </Typography>

        <Box sx={{ display: 'grid', gap: 2 }}>
          {steps.map((s) => (
            <Box key={s.n} sx={{ display: 'flex', gap: 2, p: 2.5, borderRadius: '14px', bgcolor: 'background.paper', border: '1px solid rgba(255,255,255,0.09)', boxShadow: '0 1px 2px rgba(0,0,0,0.45), 0 10px 30px rgba(0,0,0,0.25)', opacity: s.n === 3 && phase === 'idle' ? 0.75 : 1 }}>
              <Box sx={{ width: 30, height: 30, borderRadius: '50%', flexShrink: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, fontSize: '0.85rem', bgcolor: s.done ? ACCENT : 'rgba(255,255,255,0.07)', color: s.done ? '#FCFFFF' : '#FCFFFF', border: '1px solid rgba(255,255,255,0.14)' }}>
                {s.done ? <Check size={16} strokeWidth={3} /> : s.n}
              </Box>
              <Box sx={{ flex: 1, minWidth: 0 }}>
                <Typography sx={{ fontWeight: 650 }}>{s.title}</Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mt: 0.4 }}>{s.body}</Typography>

                {s.n === 2 && (
                  <Box sx={{ mt: 2 }}>
                    <Box sx={{ display: 'flex', gap: 0.75, mb: 1.25 }}>
                      {(['shell', 'docker'] as const).map((t) => (
                        <Button key={t} size="small" onClick={() => setTab(t)} startIcon={<Terminal size={14} />}
                          sx={tab === t
                            ? { bgcolor: 'rgba(2,151,222,0.12)', color: ACCENT, border: '1px solid rgba(2,151,222,0.4)' }
                            : { color: 'text.secondary', border: '1px solid rgba(255,255,255,0.12)' }}>
                          {t === 'shell' ? 'Shell install' : 'Docker'}
                        </Button>
                      ))}
                    </Box>
                    <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1, bgcolor: '#02070A', border: '1px solid rgba(255,255,255,0.12)', borderRadius: '10px', p: 1.75 }}>
                      <Typography className="mono" sx={{ flex: 1, fontSize: '0.8rem', lineHeight: 1.6, wordBreak: 'break-all', color: '#e4e4e7' }}>
                        <span style={{ color: ACCENT }}>$ </span>{command}
                      </Typography>
                      <Button size="small" onClick={copy} startIcon={copied ? <Check size={14} /> : <Copy size={14} />}
                        sx={{ flexShrink: 0, color: copied ? 'success.main' : 'text.secondary', border: '1px solid rgba(255,255,255,0.14)' }}>
                        {copied ? 'Copied' : 'Copy'}
                      </Button>
                    </Box>
                    <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
                      Your token identifies this server to your account. Treat it like a password.
                    </Typography>
                  </Box>
                )}

                {s.n === 3 && (
                  <Box sx={{ mt: 2 }}>
                    {phase === 'idle' && (
                      <Button variant="contained" onClick={() => setPhase('waiting')} sx={{ bgcolor: ACCENT, color: '#FCFFFF', fontWeight: 700, '&:hover': { bgcolor: '#4DB6E8' } }}>
                        I've run the command — check for my server
                      </Button>
                    )}
                    {phase === 'waiting' && (
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                        <CircularProgress size={18} sx={{ color: ACCENT }} />
                        <Typography variant="body2">Waiting for your server's first heartbeat…</Typography>
                        <Typography variant="caption" color="text.secondary">(demo: simulated, ~4 seconds)</Typography>
                      </Box>
                    )}
                    {phase === 'connected' && (
                      <Box className="kaisen-rise">
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.25, p: 1.5, borderRadius: '10px', border: '1px solid rgba(52,211,153,0.45)', bgcolor: 'rgba(52,211,153,0.07)', mb: 1.75 }}>
                          <Server size={19} color="#34d399" />
                          <Box>
                            <Typography sx={{ fontWeight: 650, color: 'success.main' }}>Server connected — vps-blr-01</Typography>
                            <Typography variant="caption" color="text.secondary">
                              First heartbeat received · agent v0.9.2 · 1 AI agent detected on this host · DEMO simulation — no server was contacted
                            </Typography>
                          </Box>
                        </Box>
                        <Button variant="contained" onClick={() => { completeSetup('vps-blr-01'); navigate('/app/command'); }} sx={{ bgcolor: ACCENT, color: '#FCFFFF', fontWeight: 700, '&:hover': { bgcolor: '#4DB6E8' } }}>
                          Open the Command Center →
                        </Button>
                      </Box>
                    )}
                  </Box>
                )}
              </Box>
            </Box>
          ))}
        </Box>

        <Typography variant="caption" color="text.secondary" sx={{ display: 'block', textAlign: 'center', mt: 4 }}>
          Stuck? The agent needs outbound HTTPS only — no inbound ports, no VPN.
        </Typography>
      </Box>
    </Box>
  );
}
