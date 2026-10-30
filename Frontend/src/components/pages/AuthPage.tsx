import { FormEvent, useState } from 'react';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import { Box, Button, Divider, TextField, Typography } from '@mui/material';
import { useAuth } from '../../unified/authStore';
import { LogoMark } from '../../unified/Logo';
import { ACCENT } from '../../theme';

// Login / Sign-up — exhibition build.
// HONESTY: there is no backend user DB yet. Both the Google button and the
// email form complete a LOCAL demo sign-in (persisted in localStorage on
// this machine, no network call). The UI is final-shaped so real Google
// OAuth + a user DB can be swapped in behind useAuth.signIn later.
export default function AuthPage({ mode }: { mode: 'login' | 'signup' }) {
  const navigate = useNavigate();
  const signIn = useAuth((s) => s.signIn);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');

  const afterSignIn = () => {
    const { plan, onboarded } = useAuth.getState();
    if (!plan) navigate('/welcome/plans');
    else if (!onboarded) navigate('/welcome/setup');
    else navigate('/app/command');
  };

  const submit = (e: FormEvent) => {
    e.preventDefault();
    signIn(email.trim() || 'demo@kaisen.dev', mode === 'signup' ? name.trim() || undefined : undefined);
    afterSignIn();
  };

  const google = () => {
    // Demo flow only — no Google OAuth request is made in this build.
    signIn('demo@kaisen.dev', 'Demo Operator');
    afterSignIn();
  };

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default', display: 'flex', alignItems: 'center', justifyContent: 'center', p: 3, overflowY: 'auto' }}>
      <Box className="kaisen-rise" sx={{ width: '100%', maxWidth: 408 }}>
        <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', mb: 3.5 }}>
          <Box sx={{ mb: 2 }}>
            <LogoMark size={46} />
          </Box>
          <Typography variant="h5" sx={{ fontWeight: 700, letterSpacing: '-0.01em' }}>
            {mode === 'signup' ? 'Create your Kaisen account' : 'Welcome back'}
          </Typography>
          <Typography color="text.secondary" variant="body2" sx={{ mt: 0.75, textAlign: 'center' }}>
            {mode === 'signup'
              ? 'Security for the AI agents running on your servers.'
              : 'Sign in to your Kaisen Unified console.'}
          </Typography>
        </Box>

        <Box sx={{ bgcolor: 'background.paper', border: '1px solid rgba(255,255,255,0.09)', borderRadius: '16px', p: 3.25, boxShadow: '0 1px 2px rgba(0,0,0,0.45), 0 16px 40px rgba(0,0,0,0.35)' }}>
          <Button
            fullWidth
            onClick={google}
            sx={{
              bgcolor: '#ffffff', color: '#1f2328', fontWeight: 600, py: 1.25, borderRadius: '10px',
              '&:hover': { bgcolor: '#e8eaed' }, display: 'flex', gap: 1.25, textTransform: 'none',
            }}
          >
            <svg width="18" height="18" viewBox="0 0 48 48" aria-hidden>
              <path fill="#FFC107" d="M43.6 20.1H42V20H24v8h11.3C33.7 32.7 29.2 36 24 36c-6.6 0-12-5.4-12-12s5.4-12 12-12c3.1 0 5.8 1.2 8 3l5.7-5.7C34.3 6.1 29.3 4 24 4 13 4 4 13 4 24s9 20 20 20 20-9 20-20c0-1.3-.1-2.7-.4-3.9z"/>
              <path fill="#FF3D00" d="M6.3 14.7l6.6 4.8C14.7 15.1 19 12 24 12c3.1 0 5.8 1.2 8 3l5.7-5.7C34.3 6.1 29.3 4 24 4 16.3 4 9.7 8.3 6.3 14.7z"/>
              <path fill="#4CAF50" d="M24 44c5.2 0 9.9-2 13.4-5.2l-6.2-5.2C29.2 35.1 26.7 36 24 36c-5.2 0-9.6-3.3-11.3-8l-6.5 5C9.5 39.6 16.2 44 24 44z"/>
              <path fill="#1976D2" d="M43.6 20.1H42V20H24v8h11.3c-.8 2.2-2.2 4.2-4.1 5.6l6.2 5.2C36.9 39.2 44 34 44 24c0-1.3-.1-2.7-.4-3.9z"/>
            </svg>
            Continue with Google
          </Button>

          <Divider sx={{ my: 2.5 }}>
            <Typography variant="caption" color="text.secondary">or continue with email</Typography>
          </Divider>

          <Box component="form" onSubmit={submit} sx={{ display: 'grid', gap: 1.75 }}>
            {mode === 'signup' && (
              <TextField label="Full name" value={name} onChange={(e) => setName(e.target.value)} fullWidth autoComplete="name" placeholder="Ada Lovelace" />
            )}
            <TextField label="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} fullWidth autoComplete="email" placeholder="you@company.com" />
            <TextField label="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} fullWidth autoComplete={mode === 'signup' ? 'new-password' : 'current-password'} placeholder="••••••••" />
            <Button type="submit" variant="contained" fullWidth sx={{ bgcolor: ACCENT, color: '#FCFFFF', fontWeight: 700, py: 1.3, borderRadius: '10px', '&:hover': { bgcolor: '#4DB6E8' } }}>
              {mode === 'signup' ? 'Create account' : 'Sign in'}
            </Button>
          </Box>

          <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 2.25, lineHeight: 1.55, textAlign: 'center' }}>
            Exhibition build: sign-in is a local demo — no account is created on a
            server and no data leaves this machine. Real Google OAuth + user
            database plug in behind this same UI next.
          </Typography>
        </Box>

        <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', mt: 3 }}>
          {mode === 'signup' ? (
            <>Already have an account?{' '}<RouterLink to="/login" style={{ color: ACCENT, fontWeight: 600, textDecoration: 'none' }}>Sign in</RouterLink></>
          ) : (
            <>New to Kaisen?{' '}<RouterLink to="/signup" style={{ color: ACCENT, fontWeight: 600, textDecoration: 'none' }}>Create an account</RouterLink></>
          )}
        </Typography>
        <Typography variant="caption" color="text.secondary" sx={{ display: 'block', textAlign: 'center', mt: 1.5 }}>
          <RouterLink to="/" style={{ color: '#5D7280', textDecoration: 'none' }}>← Back to kaisen.dev</RouterLink>
        </Typography>
      </Box>
    </Box>
  );
}
