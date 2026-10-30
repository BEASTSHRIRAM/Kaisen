# Kaisen Unified — Overview

*Added 30 Oct 2026. This is the current product direction; the rest of this site documents the original research platform it builds on.*

## What Kaisen Unified is

**Security for a business that runs AI agents on its own servers.** Kaisen watches the machine *and* the AI agent running on it, and correlates events across both layers into **one plain-English incident story** — a suspicious prompt, the unusual file or tool action it led to, and the host/network anomaly that followed — instead of three unrelated alerts.

> One attack. One story. Not three random alerts.

**Why the joint view matters:** a text/guardrail filter sees the conversation but not what the agent did on the machine afterwards; a host/network monitor sees the machine but not the prompt that caused it. Kaisen's original research design — mirrored host and LLM-agent layers with a cross-layer arbiter and an attack graph — was built exactly for this gap.

## Target and pricing (planned)

- **Who:** small companies / AI startups (roughly 5–200 people) that have deployed 1–2 AI chatbots or agents on a VPS or office server and have nothing watching them.
- **Plans:** Free (self-hosted, 1 server, 1 agent, 7-day logs) · **Pro ₹1,999 / server / month** (full Agent Cockpit, correlated incident stories, 180-day logs for CERT-In, Slack/webhook alerts, DPDP/CERT-In exports, human-approval response actions) · Team ₹4,999 / month (multi-server console, team seats/RBAC, priority support).
- Pricing is indicative and validated with design partners first; no payment is taken in the current build.

## The user journey

1. **Landing** — the Unified pitch, honestly stated.
2. **Login / Sign-up** — Continue with Google or email/password. *Current build: local demo auth (labelled in the UI); real Google OAuth + user database swap in behind the same screens.*
3. **Plans** — shown immediately after sign-in. The Free plan visibly limits services: Pro surfaces in the app carry a **PRO lock badge** on Free.
4. **Connect your server** — AWS-style onboarding: one copy-paste install command (or a Docker variant) to run on your own server, then a heartbeat state. *Current build: the connection is a labelled demo simulation — no server is contacted.*
5. **Command Center** — threat level, joint anomaly score, the correlated incident story as the hero element, a working attack graph, live host sparklines.

## The pages

| Area | Page | What it shows |
|---|---|---|
| Overview | Command Center | Incident story timeline (PROMPT → AGENT → HOST → CORRELATION), attack graph, live metrics, SHAP top signals |
| Overview | Incidents | Incident list + detail: story, graph mini-view, evidence from both layers, SHAP reasons, suggested action + approval state, Markdown report export (real download) |
| Overview | Attack Graph | The original attack-path graph (filename mismatch fixed — the API now falls back to the collector's `attack_graph.json`) |
| Agent | Agent Cockpit | The harness view: what the agent is doing now, **live tool-call feed**, files touched, **memory & context-window panel** (with injected content flagged), session & budget meters, **Lethal Trifecta meter**, SHAP-style explanation, approval-gated interventions (Pause / Terminate session / Isolate host) |
| Agent | Tool Registry & Policies | Every tool the agent may use, its risk level, and its permission mode (Allow / Ask human / Block); MCP hash-pinning story for tool rug-pulls |
| Agent | Memory Inspector | Episodic / long-term / working memory entries with provenance and trust labels; poisoned entries sit in quarantine |
| Platform | Fleet — Servers | Connected servers + agents, health, heartbeats, plan-limit meter |
| Platform | Attack Lab | Playable attack scenarios (below) — the exhibition centrepiece |
| Platform | Threat Intel | Attack classes mapped to MITRE / OWASP, how each works, and Kaisen's answer; uncovered classes are honestly marked **Roadmap** |
| Platform | Audit & Compliance | Audit log (which agent/user accessed what, when), CERT-In 180-day retention meter, DPDP + CERT-In export cards (real summary downloads) |
| Account | Plans / Billing & Usage / Settings | Current plan, usage meters, invoices, workspace + team/RBAC shell |
| Host monitors (original) | Host Dashboard, Alerts, Suspicious IPs, Logs | The original live host monitoring, fed by the real Python API |

## Attack Lab scenarios

Each scenario replays an attack chain end-to-end and watches Kaisen correlate it:

1. **Prompt Injection Chain** — injected instruction → out-of-scope profile read → first-touch of `customers_export.csv` → blocked `.env` read → blocked exfiltration → correlation → containment (operator-approved).
2. **Agent Memory Poisoning** — a poisoned long-term memory entry (MINJA / AgentPoison pattern) is planted, later retrieved, and quarantined from the Memory Inspector.
3. **Tool Poisoning (MCP)** — a tool description rug-pull (MCPTox pattern) is caught by the Tool Registry's pinning + permission policy.
4. **Brute Force → Ransomware** — the classic host chain from Kaisen's original simulators, chained after a foothold.
5. **Data Exfiltration via Tools** — data leaves through legitimate-looking tool calls; the joint view is what connects them.

Scenario patterns cite the research they are shaped from (InjecAgent, EchoLeak CVE-2025-32711, AgentFlayer, MCPTox, MINJA, AgentPoison; organised around Simon Willison's **Lethal Trifecta**, 2025: private-data access + untrusted content + external communication).

## Screenshots

The Kaisen Unified build (Oct 2026) — Midnight Black, Electric Blue, one Cantaloupe accent:

![Login — Continue with Google + email, demo-auth note visible](../imgs/unified/login.png)

![Plans — Free with locked lines, Pro ₹1,999 "Most Popular", Team ₹4,999](../imgs/unified/plans.png)

![Connect your server — connected after the (demo) heartbeat](../imgs/unified/setup-connected.png)

![Command Center — DEMO MODE banner, incident story, attack graph](../imgs/unified/incident-story.png)

![Agent Cockpit — live tool-call feed, memory & context window, Lethal Trifecta meter](../imgs/unified/agent-cockpit.png)

![Attack Lab — five playable attack scenarios](../imgs/unified/attack-lab.png)

## Design system

- **Benchmark:** the Wispr Flow desktop app — clean, premium, dark.
- **Palette:** Midnight Black `#02070A` background · Electric Blue `#0297DE` primary · Cantaloupe Orange `#FC734D` as the *single* sparing accent (incident highlight, Attack Lab launch, Pro "Most Popular"). Green/amber/red are small semantic status colours only.
- **Icons:** Lucide (professional icon set) — no emoji icons.
- **Type:** Inter (body), Space Grotesk (display), JetBrains Mono (data/commands).

## Honesty ledger — what is real today

| Part | Status |
|---|---|
| Host metrics, alerts, IPs, logs (original pages + Command Center with backend running) | **Real** — polled from the existing Python API |
| Attack graph via `/api/graph` | **Real** when the collector has exported one (fallback fix in this release) |
| Live detection method | **Rule-based thresholds** — the Double DQN / SHAP core is a *research* system trained and evaluated **in simulation**; it does not score live traffic today |
| Scenario replay, incident story, tool feed, memory panel during replay | **Scripted demo data** — a "DEMO MODE — scenario replay" banner is on screen whenever it drives a view |
| Sign-in | **Demo auth** (local only, labelled) — no Google OAuth or user DB yet |
| Setup heartbeat / server connection | **Demo simulation** (labelled) — the install command is the onboarding shape, not a live distribution endpoint yet |
| Agent telemetry | Follows the repo's `agent_telemetry` schema; a connector to a real agent framework is **Phase 1**, not yet wired |

## Roadmap

- **Phase 0 (done in this release):** graph fix, honest labelling of demo data, docs that match the code.
- **Phase 1:** one real agent-telemetry connector (one framework), SQLite storage + API auth, one alert integration (webhook/Slack) with dedup, one-command Docker install on a single server.
- **Phase 2:** validation with 3 design partners; MSP white-label channel; the follow-up research paper — *"Two Layers, One Chain"*: a paired-chain benchmark + correlation detector evaluated against single-layer baselines.
