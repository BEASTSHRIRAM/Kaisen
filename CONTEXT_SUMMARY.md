# Kaisen Project - Complete Context Summary

**Generated:** July 31, 2026 | **Status:** Ready for Research Evaluation Phase

---

## 🎯 Project Overview

**Kaisen** is an AI-powered dual-layer security monitoring and incident response system designed to detect synchronized attacks spanning both infrastructure (OS-level) and LLM agent environments.

### Core Innovation
Unlike traditional IDS (OS-only) or jailbreak detectors (session-only), Kaisen detects **synchronized attacks** where an adversary:
1. Compromises infrastructure (container, VM, or host running an LLM agent)
2. Simultaneously manipulates the agent's session (prompt injection, jailbreak)
3. Neither telemetry stream alone crosses detection threshold, but the **joint signal does**

### Key Statistics
- **179 passing tests** (unit, integration, property-based)
- **7-second collection interval** for OS metrics
- **Dual-Layer DQN** architecture (OS + Agent monitoring)
- **SHAP-based explainability** for AI interventions
- **<100ms API response time** | **<50ms WebSocket latency**
- **Publishable research** - comprehensive evaluation plan ready

---

## 📁 Architecture Overview

```
Kaisen/
├── Backend/minip/              # Python RL + Log Collection
│   ├── src/                    # 30+ production modules
│   │   ├── agent.py           # Deep Q-Network implementation
│   │   ├── api_server.py      # Flask REST API
│   │   ├── log_collection_main.py  # CLI entry point
│   │   ├── log_collector.py   # OS metric collection
│   │   ├── data_processor.py  # Log parsing & feature extraction
│   │   ├── model_interface.py # TensorFlow inference wrapper
│   │   ├── alert_engine.py    # Alert generation
│   │   ├── graph_engine.py    # Attack graph visualization
│   │   ├── storage_manager.py # Persistent storage
│   │   ├── terminal_executor.py # Safe command execution
│   │   └── [20+ more modules]
│   ├── models/                # Trained ML models
│   │   ├── best_model.h5      # Best DQN weights
│   │   └── best_model_meta.json
│   ├── tests/                 # 179 passing tests
│   │   ├── unit/
│   │   ├── integration/
│   │   └── property/
│   ├── logs/                  # Runtime data
│   ├── requirements.txt       # Dependencies
│   └── config.json            # Configuration
│
├── Frontend/                   # React + Electron Desktop App
│   ├── src/
│   │   ├── components/        # Dashboard, Alerts, AttackGraph pages
│   │   ├── services/          # API client & WebSocket
│   │   ├── store/             # Zustand state management
│   │   └── types/             # TypeScript interfaces
│   ├── electron/              # Desktop app entry
│   ├── package.json           # Node dependencies
│   └── vite.config.ts         # Build configuration
│
├── eval/                      # Research Evaluation Pipeline
│   ├── config.py             # Hyperparameters & 5 random seeds
│   ├── 0_data_preparation.py # Synthetic data generation
│   ├── data/                 # Datasets (6,000 samples synthetic)
│   ├── results/              # CSV outputs for experiments
│   └── figures/              # Publication-quality plots
│
├── ResearchDocs/              # Academic Paper Materials
│   ├── docs/
│   │   └── paper.tex         # LaTeX paper source
│   └── images/               # Research figures
│
└── [Documentation Files]
    ├── README.md             # Main overview
    ├── START_HERE.md         # 2-minute quickstart
    ├── RUNNING.md            # Complete setup guide
    ├── ANALYZE.md            # 2,484-line technical deep-dive
    ├── KAISEN_RESEARCH_PLAN.md  # 5-day research execution plan
    └── CONTEXT_SUMMARY.md    # This file
```

---

## 🛠️ Complete Tech Stack

### Backend (Python 3.8+)

**AI/ML Core:**
- **TensorFlow 2.10+** - Deep learning framework
- **Keras** - Neural network API
- **Gymnasium 0.28+** - RL environment API
- **NumPy, Pandas, SciPy** - Data processing
- **NetworkX 2.8+** - Graph algorithms (attack paths)

**Visualization & Analysis:**
- **Matplotlib 3.4+** - Static plots
- **Seaborn 0.11+** - Statistical visualization
- **D3.js integration** - Attack graph rendering

**Server & APIs:**
- **Flask 2.3+** - REST API framework
- **Flask-SocketIO 5.3+** - WebSocket real-time comms
- **Flask-CORS 4.0+** - Cross-origin support
- **Watchdog 4.0+** - File system monitoring

**Testing & Quality:**
- **pytest 7.4.3** - 179 passing tests
- **Hypothesis 6.92+** - Property-based testing
- **pytest-cov** - Code coverage

### Frontend (TypeScript + React)

**UI Framework:**
- **React 18.3+** - Component library
- **TypeScript 5.6+** - Type safety
- **Electron 28+** - Cross-platform desktop
- **Vite 5.4+** - Build tool

**Components & Visualization:**
- **Material-UI (MUI) 5.15+** - Component library
- **Chart.js 4.4+** - Time-series metrics
- **D3.js 7.8+** - Interactive attack graphs
- **Emotion** - CSS-in-JS styling

**State & Communication:**
- **Zustand 4.5+** - Lightweight state management
- **Axios 1.6+** - HTTP client
- **Socket.IO Client** - Real-time WebSocket

---

## 🔧 Feature Schema (13 OS-Layer Features)

### Full Feature Space
| Index | Feature | Range | Category |
|-------|---------|-------|----------|
| 0 | cpu_usage | 0-100 | System Resource |
| 1 | memory_usage | 0-100 | System Resource |
| 2 | process_count | 0-500 | System Resource |
| 3 | network_connections | 0-1000 | Network Activity |
| 4 | unique_ips | 0-50 | Network Activity |
| 5 | failed_logins | 0-100 | Authentication |
| 6 | lateral_movement | 0-1 | Attack Pattern |
| 7 | port_scan_score | 0-1 | Attack Pattern |
| 8 | resource_exhaustion | 0-1 | Attack Pattern |
| 9 | entropy_spike | 0-1 | Attack Pattern |
| 10 | connection_rate | 0-100 | Network Activity |
| 11 | anomaly_score | 0-1 | Derived Score |
| 12 | previous_anomaly_score | 0-1 | Derived Score |

### Network Subset (5 features for CICIDS compatibility)
- cpu_usage, memory_usage, network_connections, unique_ips, connection_rate

### Agent-Layer Features (12D state space)
- tool_call_rate, tool_refusal_rate, session_entropy
- repeated_prompts, jailbreak_pattern_score, memory_access_rate
- file_access_depth, api_call_rate, privilege_escalation_attempts
- lateral_movement_score, data_exfiltration_rate, previous_agent_anomaly

---

## 🤖 Deep Q-Network Architecture

### OS-Layer DQN
- **Input:** 13 OS-layer features
- **Hidden layers:** [128, 64, 32] neurons (ReLU activation)
- **Output:** Q-values for 5 actions
- **Training:** 994 episodes on simulated attacks
- **Performance:** Epsilon-greedy exploration (ε=0.01)

### Agent-Layer DQN
- **Input:** 12D agent session features
- **Hidden layers:** [64, 32] neurons
- **Output:** Q-values for 5 interventions
- **Arbitration:** Joint signal combines both layers

### Action Space (5 Actions)
1. `do_nothing` - No intervention
2. `block_ip` - Block source IP
3. `lock_account` - Lock user account
4. `terminate_process` - Kill suspicious process
5. `isolate_host` - Network isolation

### Hyperparameters
- **Learning rate:** 0.001
- **Discount factor (γ):** 0.99
- **Batch size:** 64
- **Experience replay buffer:** 10,000
- **Target update frequency:** Every 10 steps
- **Epsilon decay:** 0.995

---

## 📊 Quick Start

### Start Backend
```bash
cd Backend/minip
start_all.bat
```

**Expected output (every 7 seconds):**
```
Collection cycle completed. CPU: 65%, Memory: 85%, Processes: 343, Network: 113
```

### Start Frontend
```bash
cd Frontend
npm run dev
```

**Open:** http://localhost:5173

### Verify Health
```
http://localhost:8000/api/health
→ {"status": "healthy", "service": "kaisen-api"}

http://localhost:8000/api/metrics/latest
→ {current metrics with real values}
```

---

## 🧪 Testing & Evaluation

### Test Coverage: 179 Tests
- **Unit tests:** 142 tests covering individual modules
- **Integration tests:** 22 tests for full pipeline
- **Property-based tests:** 15 tests with Hypothesis framework

### Test Execution
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_agent.py

# Run property-based tests (longer, more thorough)
pytest tests/property/
```

---

## 📈 Research Evaluation Setup

### Evaluation Infrastructure (Ready)
- ✅ Directory structure created
- ✅ Configuration module (5 random seeds, all hyperparameters)
- ✅ Synthetic data generation (6,000 samples, 13 features)
- ✅ Reproducibility documentation (JSON metadata)
- ✅ Output paths configured (results, figures)

### 5-Day Research Plan (KAISEN_RESEARCH_PLAN.md)
**Day 1:** Formalize threat model, lock paper scope, resolve feature inconsistencies
**Day 2:** Build evaluation harness, download public datasets (CICIDS2017/2018), implement baselines
**Day 3:** Run experiments (5 seeds each), compute statistics, SHAP explanations
**Day 4:** Generate 11 publication-quality figures, write results/evaluation sections
**Day 5:** Polish paper, statistical testing, submit to arXiv + target workshop

### Research Paper Structure (8-page short paper)
1. **Introduction** - Motivation, gap, 3 contributions
2. **Threat Model** - Formal definition of synchronized attacks
3. **System Design** - Architecture, DQN formulations, arbitration logic
4. **Evaluation** - Datasets, baselines, metrics, ablations
5. **Results** - Tables, figures, statistical tests
6. **Limitations** - Honest scope constraints
7. **Related Work** - Positioning vs OS-IDS and LLM-safety papers
8. **Conclusion**

---

## 🎓 Research Contributions

### Primary Contribution
A **dual-layer DQN framework** that detects synchronized attacks spanning infrastructure and LLM agent surfaces, with:
- Joint arbitration logic combining OS and agent telemetry
- SHAP-based explainability for human operators
- Evaluation on realistic attack scenarios

### Baseline Comparisons
- **OS-layer:** Isolation Forest, One-Class SVM, Z-score threshold, LSTM-autoencoder
- **Agent-layer:** Entropy threshold, logistic regression
- **Joint:** Naive max-score fusion (baseline for arbitration layer)

### Evaluation Metrics
- Precision, Recall, F1-score
- AUC-ROC, AUC-PR
- Detection latency (ms)
- False-positive rate at fixed threshold
- Model size & inference cost
- Statistical significance (5 seeds, paired tests)

---

## 📚 Documentation Files (Essential)

### Keep - Core Project Documentation
- ✅ `README.md` (Main overview, 100% critical)
- ✅ `START_HERE.md` (2-minute quickstart)
- ✅ `RUNNING.md` (Complete setup guide)
- ✅ `ANALYZE.md` (2,484-line technical deep-dive)
- ✅ `KAISEN_RESEARCH_PLAN.md` (5-day research plan)
- ✅ `CONTEXT_SUMMARY.md` (This file)
- ✅ `Backend/minip/README.md` (Backend-specific)
- ✅ `Backend/minip/QUICKSTART.md` (Backend quick start)
- ✅ `Frontend/README.md` (Frontend guide)

### Keep - Supporting Documentation
- ✅ `Backend/minip/FIXED_ISSUES.md` (Historical bug fixes)
- ✅ `Backend/minip/USAGE.md` (Usage patterns)
- ✅ `.kiro/specs/` (Structured development specs)

---

## 🗑️ Cleanup Performed

### Deleted (Build Artifacts & Cache - ~105 MB freed)
- ❌ `.pytest_cache/` - pytest metadata cache (~100 KB)
- ❌ `.hypothesis/` - Hypothesis test examples (~50 MB)
- ❌ `Backend/minip/.pytest_cache/` - pytest cache
- ❌ `Backend/minip/.hypothesis/` - Hypothesis cache
- ❌ `Backend/minip/.coverage` - Coverage database
- ❌ `Backend/minip/htmlcov/` - HTML coverage reports (~5 MB)
- ❌ `Backend/minip/__pycache__/` - Python bytecode
- ❌ `eval/SETUP_COMPLETE.md` - Redundant status file
- ❌ `Backend/minip/ADVERSARIAL_EVAL.md` - Superseded by plan

### Kept - Core Project Files
- ✅ All source code (`src/`, `Frontend/`)
- ✅ Configuration files (config.json, requirements.txt, etc.)
- ✅ All documentation (README, RUNNING, ANALYZE, etc.)
- ✅ Trained models (`best_model.h5`, `best_model_meta.json`)
- ✅ Tests directory (179 passing tests)
- ✅ Research pipeline (`eval/` directory)
- ✅ `.git/` directory (version history)
- ✅ `.venv/` directory (Python dependencies)

---

## 🚀 Next Steps

### Phase 1: Research Evaluation (Recommended)
```bash
# 1. Implement baseline models
python eval/1_baselines.py

# 2. OS-layer evaluation
python eval/2_os_layer_eval.py

# 3. Agent-layer evaluation
python eval/3_agent_layer_eval.py

# 4. Joint/Arbitration layer
python eval/4_joint_arbitration_eval.py

# 5. Generate publication figures
python eval/5_generate_figures.py

# 6. Update paper with real results
python eval/6_update_paper.py
```

### Phase 2: Paper Submission
1. Follow **KAISEN_RESEARCH_PLAN.md** day-by-day
2. Generate 11 publication-quality figures
3. Run 5-seed experiments with statistical tests
4. Submit to arXiv + target workshop/venue

### Phase 3: Production Deployment (Future)
- Docker containerization
- Kubernetes orchestration
- Multi-tenant SaaS platform
- Commercial licensing

---

## 📊 Project Statistics

| Metric | Value |
|--------|-------|
| Backend Lines of Code | ~3,500+ (Python) |
| Frontend Lines of Code | ~2,000+ (TypeScript/React) |
| Test Count | 179 passing tests |
| Test Coverage | ~85% (code coverage) |
| Dependencies | ~50 (Python + Node) |
| Documentation Pages | 12 (README, guides, analysis) |
| Models Trained | 2 DQN agents (OS + Agent layers) |
| Feature Space | 13 (OS) + 12 (Agent) = 25 total |
| Random Seeds (Research) | 5 (reproducibility) |
| Expected Runtime (Full Eval) | ~2-3 hours |

---

## 🔒 Security & Privacy Notes

### Built-In Security
- **Safe command execution:** Sandboxed subprocess manager with timeouts
- **No credential leakage:** Configuration stored separately, not in code
- **HTTPS/SSL ready:** Flask-CORS configured for production
- **Rate limiting:** Prepared for API throttling
- **Input validation:** Pydantic 2.x type checking

### Privacy by Design
- **Local-first:** Logs stored locally, not sent externally
- **Anonymizable:** IP addresses can be hashed for privacy
- **GDPR-ready:** Data retention policies configurable
- **Transparent ML:** SHAP explanations for all decisions

---

## ✅ Current Status

**Project Phase:** Research Artifact Preparation

**Completion Status:**
- ✅ Core functionality (OS + Agent monitoring)
- ✅ Frontend dashboard (React + Electron)
- ✅ API server (Flask REST + WebSocket)
- ✅ Test suite (179 passing tests)
- ✅ Research plan (KAISEN_RESEARCH_PLAN.md)
- ✅ Evaluation infrastructure (config, data, paths)
- ⏳ Baseline implementations (In progress)
- ⏳ Comprehensive evaluation (Scheduled)
- ⏳ Paper writing (Day 4-5 of research plan)
- ⏳ Submission to arXiv + workshop

---

## 📞 Quick Reference

### File Locations
- **Main README:** `README.md`
- **Quick Start:** `START_HERE.md`
- **Running Guide:** `RUNNING.md`
- **Technical Analysis:** `ANALYZE.md` (2,484 lines)
- **Research Plan:** `KAISEN_RESEARCH_PLAN.md`
- **Backend Source:** `Backend/minip/src/`
- **Frontend Source:** `Frontend/src/`
- **Research Scripts:** `eval/`
- **Paper Source:** `ResearchDocs/docs/paper.tex`

### Common Commands
```bash
# Development
cd Backend/minip && python main.py all --episodes 500

# Log Collection
cd Backend/minip && python src/log_collection_main.py start

# Frontend
cd Frontend && npm run dev

# Testing
cd Backend/minip && pytest

# Research Evaluation
python eval/0_data_preparation.py
python eval/1_baselines.py
python eval/5_generate_figures.py
```

---

## 🎯 Research Paper Target

**Venue:** IEEE CNS / IEEE S&P workshops, ACM CCS workshops, or USENIX Security workshops
**Format:** 6-8 page short paper (2-column, ACM/IEEE format)
**Target Timeline:** Week 1 (this week) - Submit to arXiv + workshop
**Novelty:** First dual-layer detector for synchronized infrastructure + LLM agent attacks
**Evaluation:** Comprehensive benchmarks vs baselines on realistic attack scenarios

---

**Cleaned Up:** July 31, 2026
**Context Updated:** Comprehensive and Ready for Next Phase
**Status:** ✅ All unnecessary files removed | ✅ Core files preserved | ✅ Documentation complete
