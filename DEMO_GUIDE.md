# 🎯 KAISEN Live Demo Guide (5 minutes)

## Quick Start: Two-Part Demo

### Part 1: Inference Demo (2 min) - Model Detecting Attacks

Shows the DQN model in action with real-time anomaly detection.

**Run:**
```bash
cd c:\myprojects\Kaisen
python eval/demo_inference.py
```

**What you'll see:**
- ✅ Model loads successfully
- 📊 3 attack scenarios tested:
  1. **Normal Operation** - Low anomaly score (~0.15)
  2. **Synchronized Attack** - High joint score (~0.80)
  3. **DoS Attack** - Very high score (~0.90)
- 🔍 SHAP-style feature explanations (which features triggered alerts)
- ⏱️ Inference latency: ~2-3ms per prediction

**Key Output:**
```
🔴 CRITICAL - SYNCHRONIZED ATTACK
    OS-Layer Score:     0.823
    Agent-Layer Score:  0.795
    Joint Score:        0.809
    Inference Time:     2.1ms

SHAP Feature Attribution:
  • Jailbreak patterns: +0.32
  • Lateral movement: +0.25
  • CPU spike: +0.28
```

---

### Part 2: Live Dashboard (3 min) - Real-Time Alerts

Generates simulated attacks and streams them to the dashboard.

**Terminal 1: Start Simulator**
```bash
cd c:\myprojects\Kaisen
python eval/demo_dashboard_simulator.py
```

**Terminal 2: Start Backend API**
```bash
cd c:\myprojects\Kaisen\Backend\minip
python src/api_server.py
```

**Terminal 3: Start Frontend Dashboard**
```bash
cd c:\myprojects\Kaisen\Frontend
npm install  # (if not already done)
npm run dev
```

**Open browser:** http://localhost:5173

**What you'll see:**
- 🔴 Real-time alerts flowing in
- 📈 Metrics updating every 2 seconds
- 🗺️ Attack patterns visualized
- 📊 Dashboard showing:
  - Current CPU/Memory usage
  - Alert count (critical/high/medium)
  - Suspicious IPs detected
  - Attack timeline

---

## Demo Flow Explained

### Inference Demo Timeline:
```
[1] Load model (best_model.h5)
[2] Test 3 scenarios in sequence:
    ├─ Scenario 1: Normal (benign behavior)
    ├─ Scenario 2: Synchronized Attack (OS + Agent layers)
    └─ Scenario 3: DoS Attack (resource exhaustion)
[3] For each: Show anomaly scores, SHAP explanations, recommendations
[4] Summary: Detection performance across all scenarios
```

### Dashboard Timeline:
```
Cycle 1-2:  Normal operation (benign metrics)
Cycle 3-5:  Synchronized attack detected
            ├─ Alert: "SYNCHRONIZED ATTACK DETECTED"
            ├─ Anomaly Score: 0.80+
            └─ Action: BLOCK & INVESTIGATE
Cycle 6-8:  DoS attack detected
            ├─ Alert: "DENIAL OF SERVICE"
            ├─ CPU/Memory: >85%
            └─ Action: RATE LIMIT
Cycle 9-11: Port scanning detected
            ├─ Alert: "RECONNAISSANCE ACTIVITY"
            ├─ Port scan score: 0.75+
            └─ Action: BLOCK IPS
[Loop repeats]
```

---

## What to Highlight

### Technical Proof:
- ✅ DQN model correctly identifies all 3 attack types
- ✅ Joint detection (OS+Agent) > single-layer detection
- ✅ Sub-3ms latency suitable for real-time deployment
- ✅ SHAP explanations make alerts interpretable

### Business Value:
- 🔍 Detects attacks that hide from traditional IDS
- ⚡ Real-time response (2.3ms average)
- 📊 Unified monitoring (infrastructure + LLM safety)
- 🎯 Actionable alerts with explanations

---

## Troubleshooting

**Model not found:**
```bash
# Check available models
ls c:\myprojects\Kaisen\Backend\minip\models\
```
Expected files: `best_model.h5`, `best_model_target.h5`

**API connection errors:**
```bash
# Ensure logs directory exists
mkdir c:\myprojects\Kaisen\Backend\minip\logs
```

**Frontend won't start:**
```bash
cd c:\myprojects\Kaisen\Frontend
npm install
npm run dev
```

---

## Key Metrics to Reference

| Metric | Benchmark | KAISEN |
|--------|-----------|--------|
| F1-Score (Synchronized Attack) | 0.918 (baseline) | **0.948** |
| AUC-ROC | 0.951 (baseline) | **0.965** |
| Detection Latency | 18.5ms (LSTM) | **2.3ms** |
| False Positive Rate | 8.2% (SVM) | **5.5%** |

---

## Next Steps After Demo

1. **Paper Discussion**: Share paper2.pdf showing research methodology
2. **Scalability**: "How does this scale to 100+ hosts?"
3. **Real-World Deployment**: "Can this run on production systems?"
4. **Customization**: "Can we tune for specific attack types?"

---

**Questions to Prepare For:**
- "How accurate is the synchronized attack detection?"
- "What's the false positive rate?"
- "How does it compare to standard IDS?"
- "Can it defend against adversarial attacks?"
- "How do we integrate with existing security tools?"

---

**Demo Status:** ✅ Ready for presentation
**Estimated Time:** 5 minutes
**Audience:** Technical (researchers, engineers, security teams)
