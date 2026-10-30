import { ReactNode, useEffect, useRef, useState } from 'react';
import { Box, Button, Card, CardContent, Typography } from '@mui/material';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import PauseIcon from '@mui/icons-material/Pause';
import RestartAltIcon from '@mui/icons-material/RestartAlt';
import { Lock } from 'lucide-react';

// ——— "Pro" lock badge: shown when the signed-in plan is Free and a Pro ———
// feature is on screen (plan gating is visible, per the product spec).
export function ProLock({ label = 'PRO' }: { label?: string }) {
  return (
    <Box component="span" sx={{ display: 'inline-flex', alignItems: 'center', gap: 0.5, px: 0.85, py: 0.3, borderRadius: '6px', border: '1px solid rgba(2,151,222,0.45)', backgroundColor: 'rgba(2,151,222,0.09)', color: ACCENT, fontSize: '0.66rem', fontWeight: 700, letterSpacing: '0.06em', whiteSpace: 'nowrap' }}>
      <Lock size={11} strokeWidth={2.6} /> {label}
    </Box>
  );
}
import { ACCENT } from '../theme';
import { AttackGraph } from '../types';
import { useCockpit } from './cockpitStore';

// ——— scenario replay transport controls (shared by Command Center + Cockpit) ———
export function ScenarioControls({ size = 'medium' }: { size?: 'small' | 'medium' }) {
  const { demoActive, playing, startDemo, togglePlay, resetDemo, sessionTerminated } = useCockpit();
  if (!demoActive) {
    return (
      <Button variant="contained" size={size} startIcon={<PlayArrowIcon />} onClick={startDemo} sx={{ bgcolor: ACCENT, color: '#FCFFFF', '&:hover': { bgcolor: '#4DB6E8' }, fontWeight: 650 }}>
        Replay incident scenario
      </Button>
    );
  }
  return (
    <Box sx={{ display: 'flex', gap: 1 }}>
      <Button variant="outlined" size={size} startIcon={playing ? <PauseIcon /> : <PlayArrowIcon />} onClick={togglePlay} disabled={sessionTerminated} sx={{ borderColor: 'rgba(255,255,255,0.2)', color: 'text.primary' }}>
        {playing ? 'Pause replay' : 'Resume replay'}
      </Button>
      <Button variant="text" size={size} startIcon={<RestartAltIcon />} onClick={resetDemo} sx={{ color: 'text.secondary' }}>
        Reset
      </Button>
    </Box>
  );
}

// ——— animated counter (live-feel motion, rAF, no deps) ———
export function useAnimatedNumber(value: number, duration = 550): number {
  const [display, setDisplay] = useState(value);
  const prev = useRef(value);
  useEffect(() => {
    const from = prev.current;
    const to = value;
    if (from === to) return;
    let raf = 0;
    const start = performance.now();
    const step = (now: number) => {
      const p = Math.min(1, (now - start) / duration);
      const eased = 1 - Math.pow(1 - p, 3);
      setDisplay(from + (to - from) * eased);
      if (p < 1) raf = requestAnimationFrame(step);
      else prev.current = to;
    };
    raf = requestAnimationFrame(step);
    return () => cancelAnimationFrame(raf);
  }, [value, duration]);
  return display;
}

export function AnimatedNumber({
  value,
  decimals = 0,
  prefix = '',
  suffix = '',
}: {
  value: number;
  decimals?: number;
  prefix?: string;
  suffix?: string;
}) {
  const v = useAnimatedNumber(value);
  return (
    <span>
      {prefix}
      {v.toLocaleString('en-IN', {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals,
      })}
      {suffix}
    </span>
  );
}

// ——— panel primitives ———
export function Panel({
  title,
  right,
  children,
  sx,
}: {
  title?: string;
  right?: ReactNode;
  children: ReactNode;
  sx?: object;
}) {
  return (
    <Card sx={{ height: '100%', ...sx }}>
      <CardContent sx={{ p: 2.25, '&:last-child': { pb: 2.25 } }}>
        {(title || right) && (
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1.75 }}>
            {title && (
              <Typography
                variant="caption"
                sx={{ textTransform: 'uppercase', letterSpacing: '0.12em', color: 'text.secondary', fontWeight: 650 }}
              >
                {title}
              </Typography>
            )}
            {right}
          </Box>
        )}
        {children}
      </CardContent>
    </Card>
  );
}

export function Tag({
  children,
  tone = 'grey',
}: {
  children: ReactNode;
  tone?: 'grey' | 'accent' | 'danger' | 'warn';
}) {
  const colors = {
    grey: { c: '#93A8B5', b: 'rgba(255,255,255,0.14)', bg: 'rgba(255,255,255,0.04)' },
    accent: { c: ACCENT, b: 'rgba(2,151,222,0.4)', bg: 'rgba(2,151,222,0.08)' },
    danger: { c: '#f04b5d', b: 'rgba(240,75,93,0.45)', bg: 'rgba(240,75,93,0.09)' },
    warn: { c: '#f5a524', b: 'rgba(245,165,36,0.45)', bg: 'rgba(245,165,36,0.09)' },
  }[tone];
  return (
    <Box
      component="span"
      sx={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: 0.5,
        px: 0.85,
        py: 0.3,
        borderRadius: '6px',
        border: `1px solid ${colors.b}`,
        backgroundColor: colors.bg,
        color: colors.c,
        fontSize: '0.68rem',
        fontWeight: 600,
        letterSpacing: '0.04em',
        whiteSpace: 'nowrap',
      }}
    >
      {children}
    </Box>
  );
}

export function Meter({
  label,
  value,
  max,
  display,
  dangerAbove,
}: {
  label: string;
  value: number;
  max: number;
  display: string;
  dangerAbove?: number;
}) {
  const pct = Math.min(100, (value / max) * 100);
  const danger = dangerAbove !== undefined && pct >= dangerAbove;
  return (
    <Box sx={{ mb: 1.6 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.6 }}>
        <Typography variant="caption" color="text.secondary">
          {label}
        </Typography>
        <Typography variant="caption" className="mono" sx={{ color: danger ? 'error.main' : 'text.primary', fontWeight: 600 }}>
          {display}
        </Typography>
      </Box>
      <Box sx={{ height: 6, borderRadius: 999, bgcolor: 'rgba(255,255,255,0.08)', overflow: 'hidden' }}>
        <Box
          sx={{
            height: '100%',
            width: `${pct}%`,
            borderRadius: 999,
            bgcolor: danger ? 'error.main' : ACCENT,
            transition: 'width 650ms cubic-bezier(0.22,1,0.36,1)',
          }}
        />
      </Box>
    </Box>
  );
}

// ——— tiny SVG sparkline ———
export function Sparkline({
  data,
  height = 44,
  color = ACCENT,
}: {
  data: number[];
  height?: number;
  color?: string;
}) {
  if (data.length < 2) data = [...data, ...data];
  const w = 220;
  const max = Math.max(...data, 1);
  const min = Math.min(...data, 0);
  const range = max - min || 1;
  const pts = data.map((v, i) => [
    (i / (data.length - 1)) * w,
    height - 4 - ((v - min) / range) * (height - 8),
  ]);
  const line = pts.map((p) => p.map((n) => n.toFixed(1)).join(',')).join(' ');
  return (
    <svg viewBox={`0 0 ${w} ${height}`} width="100%" height={height} preserveAspectRatio="none" aria-hidden>
      <polygon points={`0,${height} ${line} ${w},${height}`} fill={color} opacity={0.1} />
      <polyline points={line} fill="none" stroke={color} strokeWidth={1.8} strokeLinejoin="round" strokeLinecap="round" />
      <circle cx={pts[pts.length - 1][0]} cy={pts[pts.length - 1][1]} r={3} fill={color} />
    </svg>
  );
}

// ——— attack graph (deterministic layout; same renderer for live + demo) ———
const FIXED_POS: Record<string, [number, number]> = {
  attacker: [70, 70],
  agent: [225, 150],
  csv: [225, 255],
  host: [395, 80],
  exfil: [505, 205],
};

export function AttackGraphSvg({ graph, height = 300 }: { graph: AttackGraph; height?: number }) {
  const W = 560;
  const H = 300;
  const pos = new Map<string, [number, number]>();
  graph.nodes.forEach((n, i) => {
    if (FIXED_POS[n.id]) pos.set(n.id, FIXED_POS[n.id]);
    else {
      const angle = (i / Math.max(1, graph.nodes.length)) * Math.PI * 2;
      pos.set(n.id, [W / 2 + Math.cos(angle) * 170, H / 2 + Math.sin(angle) * 95]);
    }
  });
  const nodeColor = (s: number) => (s > 0.7 ? '#f04b5d' : s > 0.5 ? '#f5a524' : ACCENT);
  return (
    <svg viewBox={`0 0 ${W} ${H}`} width="100%" height={height} role="img" aria-label="Attack graph">
      <defs>
        <marker id="ku-arrow" viewBox="0 -5 10 10" refX={22} refY={0} markerWidth={6} markerHeight={6} orient="auto">
          <path d="M0,-5L10,0L0,5" fill="#667E8D" />
        </marker>
      </defs>
      {graph.edges.map((e, i) => {
        const a = pos.get(typeof e.source === 'string' ? e.source : (e.source as any).id);
        const b = pos.get(typeof e.target === 'string' ? e.target : (e.target as any).id);
        if (!a || !b) return null;
        return (
          <line key={i} x1={a[0]} y1={a[1]} x2={b[0]} y2={b[1]} stroke="#24343F" strokeWidth={1.4} markerEnd="url(#ku-arrow)" />
        );
      })}
      {graph.nodes.map((n) => {
        const p = pos.get(n.id)!;
        const label = (n.metadata?.label as string) || n.id;
        const sub = (n.metadata?.sub as string) || n.type;
        const r = n.type === 'machine' ? 17 : n.type === 'external_ip' ? 14 : 12;
        return (
          <g key={n.id}>
            <circle cx={p[0]} cy={p[1]} r={r + 6} fill={nodeColor(n.anomaly_score)} opacity={0.12} />
            <circle cx={p[0]} cy={p[1]} r={r} fill="#0A1218" stroke={nodeColor(n.anomaly_score)} strokeWidth={1.8} />
            <text x={p[0]} y={p[1] + r + 16} textAnchor="middle" fill="#FCFFFF" fontSize={11} fontWeight={600}>
              {label}
            </text>
            <text x={p[0]} y={p[1] + r + 30} textAnchor="middle" fill="#8FA3B0" fontSize={9.5}>
              {sub}
            </text>
          </g>
        );
      })}
    </svg>
  );
}

// ——— DEMO MODE banner: must be visible whenever replay data drives a view ———
export function DemoBanner({ compact = false }: { compact?: boolean }) {
  return (
    <Box
      className="kaisen-rise"
      sx={{
        display: 'flex',
        alignItems: 'center',
        gap: 1.25,
        px: 1.75,
        py: compact ? 0.8 : 1.1,
        mb: compact ? 2 : 2,
        borderRadius: '10px',
        border: '1px solid rgba(245,165,36,0.5)',
        backgroundColor: 'rgba(245,165,36,0.08)',
      }}
      role="status"
    >
      <Box className="kaisen-blink" sx={{ width: 8, height: 8, borderRadius: '50%', bgcolor: 'warning.main', flexShrink: 0 }} />
      <Typography variant="body2" sx={{ fontWeight: 650, color: 'warning.main', letterSpacing: '0.03em' }}>
        DEMO MODE — scenario replay
      </Typography>
      <Typography variant="body2" color="text.secondary">
        Scripted incident shaped from Kaisen's own simulators. Simulated data — not live detection.
      </Typography>
    </Box>
  );
}
