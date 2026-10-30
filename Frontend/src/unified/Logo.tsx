import { Box } from '@mui/material';
import { ACCENT, HIGHLIGHT, FONT_DISPLAY } from '../theme';

// Kaisen logo — a stroke-drawn shield (the host/server) whose centre is a
// "K" monogram: a vertical stem with two arms that meet at a single
// Cantaloupe pulse point — the moment a prompt becomes an action and
// Kaisen sees it. Pure geometry, no fills except the one pulse dot, so it
// stays crisp from the 20px sidebar mark up to the 64px landing hero.
export function LogoMark({ size = 32 }: { size?: number }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 48 48"
      fill="none"
      aria-hidden
      focusable="false"
      style={{ display: 'block', flexShrink: 0 }}
    >
      <path
        d="M24 3.5 40 9.3v14.2c0 10.1-6.9 17.4-16 21-9.1-3.6-16-10.9-16-21V9.3L24 3.5Z"
        stroke={ACCENT}
        strokeWidth={3.2}
        strokeLinejoin="round"
      />
      <path d="M24 14v20" stroke="#FCFFFF" strokeWidth={3.2} strokeLinecap="round" />
      <path
        d="M31.5 15.5 24.8 23.2 32.5 33"
        stroke="#FCFFFF"
        strokeWidth={3.2}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <circle cx={24.8} cy={23.2} r={2.6} fill={HIGHLIGHT} />
    </svg>
  );
}

// Mark + wordmark. `stacked` = KAISEN over UNIFIED (sidebar);
// default = one-line "KAISEN UNIFIED" (onboarding headers).
export function LogoLockup({
  size = 32,
  stacked = false,
  fontSize,
}: {
  size?: number;
  stacked?: boolean;
  fontSize?: string;
}) {
  if (stacked) {
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.25 }}>
        <LogoMark size={size} />
        <Box sx={{ lineHeight: 1 }}>
          <Box
            component="span"
            sx={{
              display: 'block',
              fontFamily: FONT_DISPLAY,
              fontWeight: 700,
              fontSize: fontSize ?? '1.04rem',
              letterSpacing: '0.07em',
              color: '#FCFFFF',
            }}
          >
            KAISEN
          </Box>
          <Box
            component="span"
            sx={{
              display: 'block',
              fontFamily: FONT_DISPLAY,
              fontWeight: 600,
              fontSize: '0.6rem',
              letterSpacing: '0.34em',
              color: ACCENT,
              mt: 0.45,
            }}
          >
            UNIFIED
          </Box>
        </Box>
      </Box>
    );
  }
  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.25 }}>
      <LogoMark size={size} />
      <Box
        component="span"
        sx={{
          fontFamily: FONT_DISPLAY,
          fontWeight: 700,
          fontSize: fontSize ?? '1rem',
          letterSpacing: '0.07em',
          color: '#FCFFFF',
          whiteSpace: 'nowrap',
        }}
      >
        KAISEN <span style={{ color: ACCENT }}>UNIFIED</span>
      </Box>
    </Box>
  );
}
