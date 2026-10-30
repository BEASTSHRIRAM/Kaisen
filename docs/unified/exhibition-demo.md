# Exhibition Demo Guide — Kaisen Unified

*For the college Open Day, 31 Oct 2026. The full product story (what is real vs demo) lives in the [Unified Overview](overview.md#honesty-ledger-what-is-real-today) — never claim more than that page says.*

## Run it

```bash
cd Frontend
npm install          # once
npm run dev          # browser demo → http://localhost:5173   (recommended)
# or the desktop app, same UI:
npm run electron:dev
```

The Unified journey and the Attack Lab replay work **without** the Python backend — the top bar honestly shows "BACKEND OFFLINE" and everything still demos. To also show real host data on the original pages, start the repo's existing Python API + collector per the main README (API on `:8000`).

> The packaged installer (`electron:build`) was not built on the build machine; `electron:dev` / browser mode above are the verified paths. The packaged (unpacked) build was smoke-tested and renders on hash routes.

## The 3-minute click-through

1. **Landing → Launch Kaisen — sign in.**
2. **Continue with Google** (demo sign-in; any email + password also works).
3. **Plans → pick Pro.** Always demo on Pro so the full Cockpit, memory panels, SHAP and interventions show without PRO lock badges. (Pick Free only if a visitor asks "what's free?" — show the lock badges in the Cockpit, then switch back via sidebar → Plans.)
4. **Setup → show the install command + Copy button** (mention the Docker tab) → **I've run the command** → heartbeat → **Server connected** → **Open the Command Center**.
5. **Command Center → Replay incident scenario** (~18 s). Narrate the story timeline as it builds: *injected prompt → agent reads the wrong customer's profile → first touch of `customers_export.csv` → `.env` read blocked → exfiltration blocked → host connections spike → Kaisen correlates it into INC-1042 CRITICAL.*
6. **Review in Agent Cockpit** — walk the tool-call feed and the memory/context panel (the injected instruction block is outlined in red; watch the **Lethal Trifecta** meter flip to LETHAL) → approve **Terminate session** and **Isolate host** in the dialogs → the incident shows **CONTAINED** back on the Command Center.
7. **Sidebar → Plans** for the subscription close: ₹1,999 per server per month.

**Between visitors:** sidebar **sign-out** resets the whole journey; top-bar **Reset** resets the replay.

## The 30-second visitor demo (Attack Lab)

Sidebar → **Attack Lab** → **Prompt Injection Chain → Launch attack.** You land in the Agent Cockpit *as the attack plays*: narrate the tool feed → memory panel → Trifecta meter → SHAP reasons → approve Terminate + Isolate. Then sidebar → **Incidents** → the same incident, documented, with **Export report** downloading a real file.

For the next visitor, launch **Agent Memory Poisoning** from the Lab — a different feed and a different story on the same engine.

## If a technical visitor pushes

- **"Is the ML live?"** — No, and we say so: live detection today is rule-based; the Double DQN + SHAP system is the research core, trained and evaluated in simulation on CICIDS2017/CERT-derived data. Kaisen Unified is the product direction that connects the two layers for real (Phase 1: one real agent connector).
- **"What stops this from being just another dashboard?"** — The correlation: guardrails see only text, host monitors see only the machine. Kaisen's incident is the *chain* across both, with a plain-English reason and a human approving every response action.
- **"Why will a small company pay?"** — They are deploying AI agents right now with nobody watching them, and DPDP/CERT-In expect logs and incident reporting. ₹1,999/server/month buys the watch + the audit trail.
