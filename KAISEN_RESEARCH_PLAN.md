# Kaisen → Research Paper: 5-Day Execution Plan

**Audience for this document:** an AI coding agent (Claude Code / Cursor / etc.) operating on the Kaisen repo.
**Goal:** produce a submittable research paper (arXiv preprint + workshop/short-paper submission) with real
evaluation, real figures, and real math — not marketing copy.

**Non-goal:** revenue, product-market fit, production deployment. Every decision below optimizes for
"defensible under peer review," not "impressive to a customer."

---

## 0. The Honest Scope (read this before doing anything)

Kaisen today is two things stapled together:
1. An OS-layer DQN anomaly detector (CPU/mem/proc/net/failed-logins → Q-values → anomaly score)
2. An LLM-agent-session DQN monitor (tool-call rate, refusal rate, entropy → intervention Q-values)

Neither layer, alone, is novel — OS-level RL-for-IDS and LLM-jailbreak-detection both have prior work.
**The one thing you actually have that most published work doesn't** is the combination: a single
arbitration layer that reasons over *both* an infrastructure attack surface and an LLM-agent attack
surface simultaneously, with SHAP explanations gating both layers' interventions. This is the paper.
Everything below is built to support that specific claim. Do not let the paper become "we built an IDS
with a neural network" — that will get desk-rejected. It must be "we built and evaluated a dual-layer
detector for a threat model that spans OS and agent surfaces at once (a 'synchronized attack')."

**Definition of a synchronized attack (write this precisely in the paper):** an adversary who
compromises infrastructure (e.g., a container running an LLM agent) *and* simultaneously manipulates the
agent's session (prompt injection, jailbreak-for-privilege-escalation) such that neither telemetry
stream alone crosses its detection threshold, but the joint signal does. This is your hypothesis (H1)
and everything in the eval should be built to test it.

---

## 1. Target Venue Strategy

Day 5 output goes to two places simultaneously:
- **arXiv** (cs.CR) — no review, timestamp establishes priority, citable immediately.
- **One realistic short-paper/workshop target** — pick one and design the paper to its page limit:
  - IEEE CNS / IEEE S&P workshops (WOOT, DLS)
  - ACM CCS workshops (AISec, CPSS)
  - USENIX Security workshops
  - A regional/student research symposium if this is your first paper (lower bar, still peer-reviewed, faster turnaround)

Have the AI IDE check current CFPs for the two most relevant ones before Day 5 and pick whichever has
the nearest realistic deadline. Page limit target: **6–8 pages, 2-column, ACM/IEEE format** (short paper),
not a 20-page full paper. Do not scope-creep into full-paper length — it dilutes the eval you can
actually finish in 5 days.

---

## 2. Paper Skeleton (fill this in as you go — lock the structure Day 1)

```
Title: A Dual-Layer Reinforcement Learning Framework for Synchronized
       Infrastructure and LLM-Agent Intrusion Detection

1. Introduction
   - Threat model motivation: LLM agents now run with infra-level privileges
     (tool use, shell access, cloud APIs) → a compromise can span both layers
   - Gap: existing IDS = OS-only; existing jailbreak detectors = session-only; none joint
   - Contribution list (3 bullets, be specific, each must map to an experiment)

2. Threat Model & Problem Formulation
   - Formal definition of synchronized attack (see Section 0 above)
   - MDP formulation for each layer (state/action/reward) — full math, Section 4 below

3. System Design
   - Architecture diagram (your existing one, cleaned up)
   - OS-layer DQN: features, network, training
   - Agent-layer DQN: 12D state space, 5 actions, network, training
   - Arbitration logic: the actual decision rule combining both layers' Q-values/scores
     (THIS MUST BE A PRECISE FORMULA, not prose — see Section 4)
   - SHAP explainability integration

4. Evaluation
   - Datasets (real, not just your simulator — see Section 3 below)
   - Baselines (see Section 3 below)
   - Metrics: precision/recall/F1, AUC-ROC, detection latency, false-positive rate
     under three conditions: OS-attack-only, agent-attack-only, synchronized-attack
   - Ablation: arbitration layer on vs off (does joint detection beat max(layer1, layer2)?)
   - Sim-to-real gap analysis (you already do KL-divergence — use it, show the number)

5. Results
   - Tables + figures (Section 5 below has the exact list)
   - Statistical significance (paired test vs best baseline)

6. Limitations & Threat-to-Validity
   - Be upfront: synthetic attack scenarios, single-organization deployment scale,
     adversarial-robustness of the RL policy itself not evaluated
   - This section is what makes reviewers trust the rest of the paper. Do not skip it
     or hand-wave it.

7. Related Work
   - OS-level ML/RL IDS (cite CICIDS-based papers, DQN-for-IDS papers)
   - LLM jailbreak/agent-safety detection papers
   - Position: "to our knowledge, first to treat these as a joint detection problem"
     (verify this claim with a literature search before asserting it)

8. Conclusion
```

---

## 3. Data & Baselines (this is the part that makes or breaks credibility)

### 3.1 OS-layer evaluation data
Do **not** rely solely on your own attack simulator for the headline numbers. Use it for training/tuning,
but report test results on at least one public benchmark:
- **CICIDS2017 or CICIDS2018** (Canadian Institute for Cybersecurity) — has brute force, DoS, infiltration,
  botnet labeled flows. Map your 5–13 features onto the closest available fields (CPU/mem won't exist in
  these datasets — be explicit that you're evaluating the *network-behavior* subset of your feature space
  against them, and evaluate the full feature set only on your own simulated/testbed data. Say this
  plainly in the limitations section rather than fudging a match.)
- Optionally **NSL-KDD** as a second, well-understood baseline everyone in the field recognizes.

### 3.2 Agent-layer evaluation data
No standard public benchmark exists yet for "LLM agent session anomaly," so build one small labeled set
honestly:
- Generate N benign agent transcripts (normal tool use, e.g. via scripted tasks against a sandbox agent)
- Generate N adversarial transcripts using known jailbreak/prompt-injection patterns (use published
  jailbreak taxonomies — e.g. DAN-style, payload-splitting, role-play escalation — for *labeling*
  categories only; do not reproduce full jailbreak prompt text verbatim in the paper itself, describe
  categories instead)
- Have a second person (or a separate LLM judge with a fixed rubric) independently label a sample to
  report inter-rater agreement (Cohen's kappa) — reviewers will ask about label quality for a novel dataset
- Publish this dataset (even if small, 200–500 sessions) alongside the paper — a labeled dataset release
  is itself a citable contribution and strengthens acceptance odds

### 3.3 Baselines (mandatory — a paper with no baseline gets rejected)
- **OS layer:** Isolation Forest, One-Class SVM, simple z-score threshold rule (your "traditional SIEM"
  strawman from the README, formalized properly), and if time allows, an LSTM-autoencoder
- **Agent layer:** perplexity/entropy threshold baseline, a fine-tuned lightweight classifier (e.g.
  logistic regression on the same 12D features) — the RL agent should beat this or you need to explain why
  RL is worth the complexity
- **Joint layer:** max-score fusion (naive baseline for your arbitration layer) — this is the single most
  important baseline, because it's the direct competitor to your core contribution

---

## 4. Required Mathematical Content

Write these out properly in the paper (LaTeX). The AI IDE should produce these as actual typeset
equations, derived from your actual code, not invented after the fact.

1. **MDP formulation**, each layer:
   `S` (state space, list exact features + dimensionality), `A` (action space), `R(s,a,s')` (reward
   function — pull the actual function from `src/agent.py`), transition assumption (model-free).

2. **Bellman optimality equation** for Q-learning:
   `Q*(s,a) = E[r + γ max_a' Q*(s',a') | s,a]`

3. **DQN loss function** actually used:
   `L(θ) = E[(r + γ max_a' Q(s',a';θ⁻) − Q(s,a;θ))²]`
   with target network update rule, replay buffer size, γ, ε-decay schedule — pull real hyperparameters
   from the training config, don't guess.

4. **Anomaly score derivation** — the exact function mapping Q-values to a [0,1] anomaly score
   (softmax over actions? margin between top-2 Q-values? state it precisely — this is currently just
   prose in the README and needs to be a formula).

5. **Arbitration function** (this is your core novelty — it MUST be a formula):
   `A_joint(s_os, s_agent) = f(anomaly_os, anomaly_agent, correlation_term)`
   Define what the correlation term is (e.g., temporal co-occurrence within a window Δt, or a learned
   weight). If it's currently just an if/else in code, formalize it as a decision rule with a threshold
   derived from validation data — show the threshold-selection process (ROC-based) as a figure.

6. **SHAP value formula** (standard, but include it and explain what feature attribution means for a
   security operator reading the explanation).

7. Fix the existing inconsistency: OS-layer input is described as both 13 and 5 features in different
   places. Pick the real number from the code and use it everywhere.

---

## 5. Required Figures (matplotlib/seaborn — exact list, don't freelance beyond this list, time is tight)

1. **System architecture diagram** (can be a clean diagram, not matplotlib — redo the ASCII one properly)
2. **ROC curves** — OS layer, agent layer, joint layer, all baselines, on one plot per attack condition
   (3 plots total: OS-only, agent-only, synchronized)
3. **Precision-Recall curves** — same structure as above (PR is more informative than ROC under class
   imbalance, which you will have)
4. **Confusion matrices** (heatmap) — joint system vs best baseline, side by side
5. **Detection latency distribution** — box plot or violin plot, your system vs baselines, in seconds
   from attack-onset to alert
6. **Training curves** — reward per episode, loss per training step, for both DQN agents (shows real
   training happened, not just an inference wrapper)
7. **Ablation bar chart** — F1 score with: OS-only, agent-only, naive-max-fusion, full arbitration layer
   (this is the single most important figure in the paper — it's the evidence for your core claim)
8. **SHAP summary plot** (beeswarm) — feature importance for a sample of true-positive detections
9. **Sim-to-real gap** — KL-divergence plot you already compute, presented properly with axis labels and
   a caption explaining what "gap" means operationally
10. **Scalability plot** — detection latency vs number of monitored hosts (10/50/100/500), log-x axis

All figures: consistent color palette, readable font size for 2-column print (≥8pt effective), vector
format (PDF/SVG) not PNG where possible, captions that state the finding, not just the axis labels.

---

## 6. Statistical Rigor Checklist (reviewers check this first)

- [ ] Report mean ± std or 95% CI over ≥5 random seeds for every headline number, not single runs
- [ ] Paired statistical test (Wilcoxon signed-rank or paired t-test) between your system and best
      baseline on F1/AUC — report p-value
- [ ] Train/val/test split described explicitly, no data leakage between simulator-generated training
      episodes and test attack scenarios
- [ ] State exact hyperparameters and hardware used (for reproducibility section)
- [ ] Report false-positive rate at a fixed operating threshold, not just AUC (AUC can look great while
      FP rate is unusable in practice — your README's honesty about "45 false alerts/day before tuning"
      is actually a good thing to show as a real finding, not hide)

---

## 7. Day-by-Day Plan

### Day 1 — Formalize + Lock Scope
- [ ] Write Section 0's threat model as the paper's actual Section 2 (formal definitions, not prose)
- [ ] Pull real hyperparameters/feature counts from code; resolve the 13-vs-5 feature inconsistency
- [ ] Derive and LaTeX-typeset all 6 equations in Section 4 above, from actual code, not memory
- [ ] Pick the one target workshop/venue and confirm page limit + template (ACM/IEEE)
- [ ] Set up `paper/` directory with LaTeX template matching venue format
- [ ] Do the literature search needed to support the "first to treat this as a joint problem" claim —
      find 8–12 real citations (OS-RL-IDS papers, LLM jailbreak detection papers) and note what's missing
      from each that you cover

### Day 2 — Build the Evaluation Harness
- [ ] Download and preprocess CICIDS2017/2018 subset, map to your feature space, document the mapping
- [ ] Build the agent-layer labeled dataset (200–500 sessions, benign + adversarial categories)
- [ ] Get a second labeler (human or rubric-based LLM judge) for a subsample, compute Cohen's kappa
- [ ] Implement all baselines (Isolation Forest, One-Class SVM, threshold rule, naive max-fusion,
      logistic regression) — these are fast to implement, don't skip any
- [ ] Set up 5-seed experiment runner with fixed train/val/test splits

### Day 3 — Run Experiments
- [ ] Run OS-layer: your DQN vs baselines, all 5 seeds, 3 attack conditions
- [ ] Run agent-layer: your DQN vs baselines, all 5 seeds
- [ ] Run joint/arbitration: your system vs naive-max-fusion, all 5 seeds, on synchronized-attack scenarios
      specifically built to require joint detection (construct these test cases deliberately — this is
      your ablation and the paper's centerpiece)
- [ ] Compute SHAP values for a sample of detections
- [ ] Compute sim-to-real KL-divergence numbers
- [ ] Log everything to structured output (CSV/JSON) for figure generation — don't hand-copy numbers

### Day 4 — Figures + Stats + Writing
- [ ] Generate all 10 figures from Section 5 via a single reproducible script (`generate_figures.py`)
- [ ] Run statistical tests, build results tables
- [ ] Write Sections 3 (System Design), 4 (Evaluation setup), 5 (Results) — these are the sections that
      just report what you built and measured
- [ ] Write Section 6 (Limitations) honestly — list every corner cut this week
- [ ] Write Section 1 (Intro) and 7 (Related Work) last, once you know what your actual numbers say

### Day 5 — Polish + Submit
- [ ] Full read-through for the "so what" test: does every figure/table get referenced and interpreted
      in text? Does the abstract match the actual results (not the aspirational ones)?
- [ ] Check venue formatting requirements exactly (page limit, anonymization if double-blind, reference
      style)
- [ ] Push code + dataset to a public repo, cite it in the paper (reproducibility = higher acceptance odds)
- [ ] Submit to arXiv (cs.CR)
- [ ] Submit to chosen workshop/venue if the deadline lines up; if not, arXiv is still a real, citable
      publication — hold the workshop submission for their next cycle rather than rushing a bad fit

---

## 8. Instructions for the AI IDE (paste-ready)

> You are working in the Kaisen repository. Your job this week is NOT to add product features. It is to
> turn Kaisen into a research artifact with a defensible evaluation. Follow `KAISEN_RESEARCH_PLAN.md`
> exactly, in order. For every number that appears in the paper, there must be a script in `eval/` that
> reproduces it — no hand-typed numbers. Every figure must be generated by a script in `eval/figures/`,
> not manually assembled. When something in the plan can't be finished on schedule, do not silently drop
> it — write it into the Limitations section instead; a documented limitation is publishable, a silently
> missing evaluation is not. Resolve the 13-vs-5 feature-count inconsistency in the codebase before
> writing anything about it in the paper. Do not fabricate baseline results — if a baseline can't be
> implemented in time, say so in Limitations rather than inventing a number.

---

## 9. What "Done" Looks Like on Day 5

- [ ] A PDF paper, 6–8 pages, 2-column, following a real venue's LaTeX template
- [ ] Every number in every table traceable to a script output file
- [ ] 10 figures, each referenced and interpreted in the text
- [ ] A public code+data repo linked from the paper
- [ ] An arXiv submission (or submission-ready draft if arXiv mod queue is slow)
- [ ] A one-paragraph honest limitations section you would not be embarrassed to have a reviewer quote
      back at you
