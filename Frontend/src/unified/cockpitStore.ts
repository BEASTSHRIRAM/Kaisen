import { create } from 'zustand';
import {
  LAB_SCENARIOS,
  LabScenario,
  LabScenarioId,
  ScenarioFrame,
} from './scenario';
import { AttackGraph } from '../types';

export type InterventionKind = 'pause' | 'terminate' | 'isolate';

export interface Intervention {
  id: string;
  time: string;
  kind: InterventionKind;
  label: string;
  approvedBy: string;
}

interface CockpitState {
  demoActive: boolean;
  playing: boolean;
  scenarioId: LabScenarioId;
  frameIndex: number;
  agentPaused: boolean;
  sessionTerminated: boolean;
  hostIsolated: boolean;
  interventions: Intervention[];

  startDemo: () => void;
  launchScenario: (id: LabScenarioId) => void;
  togglePlay: () => void;
  tick: () => void;
  resetDemo: () => void;
  applyIntervention: (kind: InterventionKind) => void;
}

const LABELS: Record<InterventionKind, string> = {
  pause: 'Agent paused by operator',
  terminate: 'Session terminated by operator',
  isolate: 'Host isolated by operator',
};

const FRESH = {
  demoActive: true,
  playing: true,
  frameIndex: 0,
  agentPaused: false,
  sessionTerminated: false,
  hostIsolated: false,
  interventions: [] as Intervention[],
};

export const useCockpit = create<CockpitState>((set, get) => ({
  demoActive: false,
  playing: false,
  scenarioId: 'prompt-injection',
  frameIndex: 0,
  agentPaused: false,
  sessionTerminated: false,
  hostIsolated: false,
  interventions: [],

  startDemo: () => set((s) => ({ ...FRESH, scenarioId: s.scenarioId })),

  launchScenario: (id) => set({ ...FRESH, scenarioId: id }),

  togglePlay: () => set((s) => ({ playing: !s.playing })),

  tick: () => {
    const { frameIndex, playing, scenarioId } = get();
    if (!playing) return;
    const last = LAB_SCENARIOS[scenarioId].frames.length - 1;
    if (frameIndex >= last) {
      set({ playing: false });
      return;
    }
    set({ frameIndex: frameIndex + 1 });
  },

  resetDemo: () =>
    set({
      demoActive: false,
      playing: false,
      frameIndex: 0,
      agentPaused: false,
      sessionTerminated: false,
      hostIsolated: false,
      interventions: [],
    }),

  applyIntervention: (kind) =>
    set((s) => {
      const frame = LAB_SCENARIOS[s.scenarioId].frames[s.frameIndex];
      const entry: Intervention = {
        id: `${kind}-${s.interventions.length}`,
        time: frame.clock,
        kind,
        label: LABELS[kind],
        approvedBy: 'Operator (you)',
      };
      return {
        interventions: [...s.interventions, entry],
        agentPaused: kind === 'pause' ? !s.agentPaused : s.agentPaused,
        sessionTerminated: kind === 'terminate' ? true : s.sessionTerminated,
        hostIsolated: kind === 'isolate' ? true : s.hostIsolated,
        playing: kind === 'terminate' ? false : s.playing,
      };
    }),
}));

export function currentScenario(state: CockpitState): LabScenario {
  return LAB_SCENARIOS[state.scenarioId];
}

export function currentFrame(state: CockpitState): ScenarioFrame {
  const frames = LAB_SCENARIOS[state.scenarioId].frames;
  return frames[Math.min(state.frameIndex, frames.length - 1)];
}

export function currentGraph(state: CockpitState): AttackGraph {
  return LAB_SCENARIOS[state.scenarioId].graph;
}

export function isContained(state: CockpitState): boolean {
  return state.sessionTerminated && state.hostIsolated;
}
