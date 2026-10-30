import { createTheme } from '@mui/material/styles';

// Kaisen Unified design system — design reference: Wispr Flow desktop.
// Palette (locked 30 Oct 2026, from @niki.aroca's "one unexpected accent"
// reel — combo 2, hex-verified from the reel frames):
//   Background  Midnight Black  #02070A  (panels a step lighter)
//   Primary     Electric Blue   #0297DE  (buttons, active states, links,
//                                         charts, agent-live indicators)
//   Accent      Cantaloupe      #FC734D  (SPARINGLY — threat/incident
//                                         highlight, Attack Lab launch,
//                                         Pro "Most Popular", hero numbers)
//   Text        off-white #FCFFFF headings, muted grey-blue body.
// Green/amber/red are semantic status colours ONLY. No pink, no cyan,
// no gradients. Hairline borders in muted blue-grey, floating panels.
export const ACCENT = '#0297DE';
export const ACCENT_LIGHT = '#4DB6E8';
export const HIGHLIGHT = '#FC734D';
export const HIGHLIGHT_LIGHT = '#FF8B6B';
export const HIGHLIGHT_TEXT = '#200D04';
export const BG = '#02070A';

// Type system (fonts are bundled locally via fontsource in main.tsx —
// no CDN, works offline). Body/UI = Inter Variable; display (headings,
// page titles, KPI numbers, wordmark) = Space Grotesk; data/code =
// JetBrains Mono.
export const FONT_BODY =
  '"Inter Variable", "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif';
export const FONT_DISPLAY =
  '"Space Grotesk", "Inter Variable", "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
export const FONT_MONO =
  '"JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Courier New", monospace';
export const PANEL = '#060D12';
export const PANEL_RAISED = '#0A1218';
export const HAIRLINE = 'rgba(148,184,205,0.13)';

export const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: { main: ACCENT, light: ACCENT_LIGHT, dark: '#0173B0' },
    secondary: { main: '#93A8B5', light: '#d4d4d8', dark: '#5D7280' },
    background: { default: BG, paper: PANEL },
    error: { main: '#f04b5d' },
    warning: { main: '#f5a524' },
    success: { main: '#34d399' },
    info: { main: '#93A8B5' },
    text: { primary: '#FCFFFF', secondary: '#8FA3B0' },
    divider: HAIRLINE,
  },
  typography: {
    fontFamily: FONT_BODY,
    h1: { fontFamily: FONT_DISPLAY, fontWeight: 700, letterSpacing: '-0.02em' },
    h2: { fontFamily: FONT_DISPLAY, fontWeight: 700, letterSpacing: '-0.015em' },
    h3: { fontFamily: FONT_DISPLAY, fontWeight: 650, letterSpacing: '-0.015em' },
    h4: { fontFamily: FONT_DISPLAY, fontWeight: 650, letterSpacing: '-0.02em' },
    h5: { fontFamily: FONT_DISPLAY, fontWeight: 650, letterSpacing: '-0.015em' },
    h6: { fontFamily: FONT_DISPLAY, fontWeight: 600, letterSpacing: '-0.01em' },
    body1: { fontSize: '0.925rem' },
    body2: { fontSize: '0.85rem' },
    caption: { fontSize: '0.72rem', letterSpacing: '0.01em' },
    button: { fontWeight: 550 },
  },
  shape: { borderRadius: 10 },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
          backgroundColor: PANEL,
          borderRadius: 12,
          border: `1px solid ${HAIRLINE}`,
          boxShadow: '0 1px 2px rgba(0,0,0,0.45), 0 10px 30px rgba(0,0,0,0.25)',
        },
      },
    },
    MuiPaper: {
      styleOverrides: { root: { backgroundImage: 'none', boxShadow: 'none' } },
    },
    MuiButton: {
      styleOverrides: {
        root: { textTransform: 'none', borderRadius: 8, boxShadow: 'none' },
        contained: { boxShadow: 'none', '&:hover': { boxShadow: 'none' } },
      },
    },
    MuiChip: {
      styleOverrides: { root: { borderRadius: 6, fontWeight: 550 } },
    },
    MuiLinearProgress: {
      styleOverrides: {
        root: { backgroundColor: 'rgba(255,255,255,0.08)', borderRadius: 999 },
        bar: { borderRadius: 999, transition: 'transform 600ms cubic-bezier(0.22,1,0.36,1)' },
      },
    },
  },
});
