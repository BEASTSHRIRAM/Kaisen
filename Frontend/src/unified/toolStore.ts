import { create } from 'zustand';
import { INITIAL_TOOLS, PermissionMode, ToolRecord } from './platformData';

// Tool Registry policy state (demo): permission-mode changes apply to this
// local store immediately so visitors can govern the agent live; a real
// deployment writes the same changes to the gateway policy file.
interface ToolState {
  tools: ToolRecord[];
  setMode: (name: string, mode: PermissionMode) => void;
}

export const useTools = create<ToolState>((set) => ({
  tools: INITIAL_TOOLS,
  setMode: (name, mode) =>
    set((s) => ({ tools: s.tools.map((t) => (t.name === name ? { ...t, mode } : t)) })),
}));
