# Kaisen - Automated Data center Security Incident and  Response System

A comprehensive security monitoring and incident response system combining reinforcement learning-based anomaly detection with real-time log collection and attack graph modeling.

## 🎯 Project Overview

Kaisen consists of two main components:

### 1. RL-Based Anomaly Detection 
A reinforcement learning agent that:
- Observes noisy behavioral metrics (login rates, file access patterns, CPU usage, **rate-of-change features**)
- Learns to select defensive actions (block IP, lock account, terminate process, isolate host)
- Responds to attacks early while minimizing false positives
- Operates under uncertainty without knowing the true attack state

### 2. Log Collection Backend 
A cross-platform log collection and analysis system that:
- Collects system logs from Windows and Linux machines (local and remote)
- Extracts and tracks IP addresses from network connections
- Processes raw logs into structured feature vectors
- Uses the pre-trained RL model for real-time anomaly detection
- Builds attack graphs to visualize potential attack paths
- Generates alerts with suspicious IP identification
- Provides CLI interface for monitoring and management

**Quick Start (Log Collection):**
```bash
# Start continuous log collection
python src/log_collection_main.py start

# Single collection cycle
python src/log_collection_main.py collect-once

# Export attack graph
python src/log_collection_main.py export-graph
```

## 📁 Project Structure

```
Backend/minip/
├── main.py                         # RL training entry point
├── config.json                     # Log collection configuration
├── requirements.txt                # Python dependencies
├── data/                           # Training datasets
│   ├── Monday-WorkingHours.pcap_ISCX.csv
│   ├── Tuesday-WorkingHours.pcap_ISCX.csv
│   └── file.csv
├── src/
│   # RL Components
│   ├── config.py                   # RL configuration
│   ├── preprocess.py               # Data preprocessing
│   ├── attack_simulator.py         # Attack simulation
│   ├── incident_env.py             # OpenAI Gym environment
│   ├── agent.py                    # DQN agent
│   ├── train.py                    # Training script
│   ├── evaluate.py                 # Evaluation & visualization
│   # Log Collection Components (New)
│   ├── collection_config.py        # Log collection config
│   ├── data_models.py              # Data structures
│   ├── terminal_executor.py        # Safe command execution
│   ├── data_processor.py           # Log parsing & IP extraction
│   ├── log_collector.py            # Local log collection
│   ├── remote_log_collector.py     # Remote log fetching
│   ├── model_interface.py          # Anomaly detection interface
│   ├── alert_engine.py             # Alert generation
│   ├── graph_engine.py             # Attack graph modeling
│   ├── storage_manager.py          # Data persistence
│   └── log_collection_main.py      # Log collection CLI
├── models/                         # Saved model checkpoints
├── logs/                           # Collected logs & alerts
│   ├── history.json                # System metrics history
│   ├── alerts.json                 # Generated alerts
│   └── application.log             # Application logs
└── tests/                          # Unit & property tests
    ├── unit/
    └── property/
```

## 🚀 Quick Start

### RL Training

#### 1. Install Dependencies

```bash
cd Backend/minip
pip install -r requirements.txt
```

#### 2. Run Complete Pipeline

```bash
python main.py all --episodes 500
```

This will:
1. Preprocess the datasets
2. Train the RL agent for 500 episodes
3. Generate training visualizations
4. Run a demo showing the trained agent

#### 3. Individual Commands

```bash
# Preprocess datasets
python main.py preprocess

# Train the agent (with all enhancements)
python main.py train --episodes 1000 --n-step --dueling --compare

# Evaluate trained model
python main.py evaluate --analyze-policy

# Generate visualizations
python main.py visualize

# Run interactive demo
python main.py demo --interactive
```

### Log Collection System

#### 1. Configure

Edit `config.json` to set:
- Collection interval (default: 7 seconds)
- Anomaly threshold (default: 0.7)
- Remote endpoints (optional)
- Log file paths

#### 2. Run Log Collection

```bash
# Start continuous monitoring
python src/log_collection_main.py start

# Single collection cycle (for testing)
python src/log_collection_main.py collect-once

# Export attack graph to JSON
python src/log_collection_main.py export-graph
```

#### 3. View Results

```bash
# View collected logs
cat logs/history.json

# View generated alerts
cat logs/alerts.json

# View application logs
cat logs/application.log
```

## 🔍 Log Collection Features

### Cross-Platform Support
- **Windows**: Uses `wmic`, `tasklist`, `netstat`, `wevtutil`
- **Linux**: Uses `top`, `ps`, `free`, `netstat`/`ss`, `journalctl`
- Automatic OS detection at startup

### IP Address Tracking
- Extracts source and destination IPs from network connections
- Tracks connection counts per IP
- Monitors failed login attempts per IP
- Identifies suspicious IPs exhibiting abnormal behavior
- Includes suspicious IPs in generated alerts

### Attack Graph Modeling
- Builds directed graphs using NetworkX
- Nodes: machines, processes, services, external IPs
- Edges: network connections, process spawns, IP connections
- Risk score propagation with decay factor (0.7)
- Identifies highest-risk attack paths
- JSON export for visualization

### Remote Log Collection
- Fetch logs from remote machines via HTTP/HTTPS APIs
- Support for API key and bearer token authentication
- Automatic retry with exponential backoff
- Merge remote and local logs in unified pipeline

### Real-Time Anomaly Detection
- Uses pre-trained RL model (`best_model.h5`)
- Processes logs every 5-10 seconds
- Generates alerts when anomaly score > threshold
- Includes suspected reason analysis (high CPU, failed logins, etc.)

## 🧠 Technical Details

### Enhanced Observation Space (10D)

The environment provides an **enhanced 10-dimensional observation space** for better attack detection:

| Feature | Description | Range |
|---------|-------------|-------|
| `login_rate` | Login attempts per window | [0, 200] |
| `file_access_rate` | File accesses per window | [0, 500] |
| `cpu_usage` | CPU usage percentage | [0, 100] |
| `login_delta` | **Rate of change** in login attempts | [-100, 100] |
| `file_delta` | **Rate of change** in file access | [-200, 200] |
| `cpu_delta` | **Rate of change** in CPU usage | [-50, 50] |
| `login_ma` | **Moving average** of login rate | [0, 200] |
| `file_ma` | **Moving average** of file rate | [0, 500] |
| `sustained_indicator` | **Sustained anomaly** indicator | [0, 1] |
| `normalized_time` | Episode progress | [0, 1] |

> **Note**: Rate-of-change features help detect attack **escalation** patterns.

### Attack Simulation

Two attack types modeled as probabilistic FSMs:

**Brute-Force Attack:**
```
Normal → Probing → Active → Compromised
```

**Ransomware Attack:**
```
Normal → Execution → Encryption → Data Loss
```

### Statistical Modeling

| Approach | Application |
|----------|-------------|
| **Poisson distributions** | Event counts (login attempts, file accesses) |
| **Local rate modeling** | Captures burstiness in network activity |
| **Normal distributions** | CPU usage with N(30,5) normal, N(80,5) attack |

> **Dataset Note**: CICIDS 2017 provides network flow features. `Total Fwd Packets` is used as a proxy for login attempts since explicit authentication logs are unavailable.

### DQN Agent Enhancements

| Feature | Description | Flag |
|---------|-------------|------|
| **Double DQN** | Reduces overestimation bias | Default |
| **N-step Returns** | Better temporal credit assignment | `--n-step` |
| **Dueling Architecture** | Separate value/advantage streams | `--dueling` |
| **Prioritized Replay** | Sample important experiences more | `--prioritized-replay` |

### Reward Structure

```python
rewards = {
    "early_containment": +50,    # Stopped attack in stage 1-2
    "late_containment": +20,     # Stopped attack in stage 3+
    "correct_no_action": +1,     # No action when no attack
    "false_positive": -10,       # Action when no attack
    "missed_attack": -30,        # Attack reached final state
    "step_penalty": -0.1         # Encourages efficiency
}
```

## 📊 Statistical Significance Testing

The project includes rigorous statistical analysis:

```bash
python main.py train --episodes 500 --compare
```

Outputs include:
- **Welch's t-test** with p-values
- **Cohen's d** effect size
- **95% confidence intervals**
- **Mann-Whitney U test** (non-parametric)

Example output:
```
DQN vs random:
  T-statistic: 8.4521
  P-value: 0.000001
  Cohen's d: 1.23
  95% CI: (12.45, 25.67)
  Significant: ✓
```

## 📈 Hyperparameter Sensitivity Analysis

Run sensitivity studies on key hyperparameters:

```python
from src.evaluate import HyperparameterAnalyzer
from src.train import Trainer

analyzer = HyperparameterAnalyzer()
results = analyzer.run_sensitivity_study(
    Trainer,
    param_name='learning_rate',
    param_values=[1e-4, 5e-4, 1e-3, 5e-3],
    num_episodes=200,
    num_seeds=3
)
analyzer.plot_sensitivity('learning_rate')
```

## 🔧 Training Options

```bash
python main.py train \
    --episodes 1000 \
    --attack-type random \
    --n-step \
    --n-steps 3 \
    --dueling \
    --checkpoint-dir models \
    --compare
```

| Option | Description | Default |
|--------|-------------|---------|
| `--episodes` | Training episodes | 500 |
| `--attack-type` | bruteforce, ransomware, both, random | random |
| `--n-step` | Enable N-step returns | False |
| `--n-steps` | N for N-step returns | 3 |
| `--dueling` | Use dueling architecture | False |
| `--no-enhanced` | Use 4D observation instead of 10D | False |
| `--compare` | Compare with baselines + statistics | False |

## 📚 References

- CICIDS 2017 Dataset: Canadian Institute for Cybersecurity
- CERT Insider Threat Dataset: Software Engineering Institute
- DQN: Mnih et al., "Human-level control through deep reinforcement learning"
- Double DQN: van Hasselt et al., "Deep Reinforcement Learning with Double Q-learning"
- Dueling DQN: Wang et al., "Dueling Network Architectures for Deep Reinforcement Learning"

## 🎓 Academic Rigor

This implementation includes features expected in academic work:

- ✅ **Poisson-based simulation** with empirical justification
- ✅ **Statistical significance testing** (t-tests, effect sizes)
- ✅ **Ablation study support** (baseline comparisons)
- ✅ **Hyperparameter sensitivity analysis**
- ✅ **Documented limitations** (proxy features, synthetic attacks)

## 📄 License

This project is for educational purposes as part of a mini project.
