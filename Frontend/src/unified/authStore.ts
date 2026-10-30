import { create } from 'zustand';

// ─────────────────────────────────────────────────────────────────────────────
// Kaisen Unified — local/demo auth + onboarding state (exhibition build).
//
// There is NO backend user database yet. Sign-in (email/password or the
// "Continue with Google" button) completes locally and persists to
// localStorage on this machine only — no network call is made and nothing
// is sent anywhere. The store's shape (user / plan / onboarded) is the
// contract a real Google OAuth + DB swap-in will implement later without
// any UI redesign.
// ─────────────────────────────────────────────────────────────────────────────

export type PlanId = 'free' | 'pro' | 'team';

export interface DemoUser {
  name: string;
  email: string;
}

interface AuthState {
  user: DemoUser | null;
  plan: PlanId | null;
  onboarded: boolean; // setup heartbeat completed
  serverName: string | null;

  signIn: (email: string, name?: string) => void;
  signOut: () => void;
  selectPlan: (plan: PlanId) => void;
  completeSetup: (serverName: string) => void;
  resetJourney: () => void;
}

const STORAGE_KEY = 'kaisen-unified-auth-v1';

function loadInitial(): Pick<AuthState, 'user' | 'plan' | 'onboarded' | 'serverName'> {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      const parsed = JSON.parse(raw);
      return {
        user: parsed.user ?? null,
        plan: parsed.plan ?? null,
        onboarded: Boolean(parsed.onboarded),
        serverName: parsed.serverName ?? null,
      };
    }
  } catch {
    // corrupted storage → start clean
  }
  return { user: null, plan: null, onboarded: false, serverName: null };
}

export const useAuth = create<AuthState>((set, get) => ({
  ...loadInitial(),

  signIn: (email, name) => {
    const fallbackName = email.split('@')[0]?.replace(/[._-]+/g, ' ') || 'Operator';
    set({
      user: {
        email,
        name: name || fallbackName.replace(/\b\w/g, (c) => c.toUpperCase()),
      },
    });
  },

  signOut: () => set({ user: null, plan: null, onboarded: false, serverName: null }),

  selectPlan: (plan) => set({ plan }),

  completeSetup: (serverName) => set({ onboarded: true, serverName }),

  resetJourney: () => get().signOut(),
}));

useAuth.subscribe((state) => {
  try {
    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({
        user: state.user,
        plan: state.plan,
        onboarded: state.onboarded,
        serverName: state.serverName,
      }),
    );
  } catch {
    // storage unavailable (private mode) — session still works in-memory
  }
});

export const PLAN_LABEL: Record<PlanId, string> = {
  free: 'Free · Self-hosted',
  pro: 'Pro · ₹1,999/server/mo',
  team: 'Team · ₹4,999/mo',
};
