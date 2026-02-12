# Kaisen - Automated Security Incident Response System

A comprehensive security monitoring and incident response system combining reinforcement learning-based anomaly detection with real-time log collection and attack graph modeling.

## 🎯 Overview

Kaisen is an intelligent security system that learns to detect and respond to cyber attacks without explicit detection rules. It combines:

- **Reinforcement Learning Agent**: Learns optimal defensive actions through experience
- **Real-Time Log Collection**: Monitors system metrics across Windows and Linux
- **IP Address Tracking**: Identifies and tracks suspicious external connections
- **Attack Graph Modeling**: Visualizes potential attack paths through infrastructure
- **Automated Alerting**: Generates alerts with suspected attack reasons

## 🏗️ Architecture

```
Kaisen/
├── Backend/
│   ├── minip/                 # Main application
│   │   ├── src/               # Source code
│   │   ├── models/            # Trained RL models
│   │   ├── logs/              # Collected logs & alerts
│   │   ├── tests/             # Unit & property tests
│   │   └── data/              # Training datasets
│   └── README.md              # Detailed backend documentation
└── Frontend/                  # (Coming soon)
```

## 🚀 Quick Start

### Prerequisites

```bash
# Python 3.8+
python --version

# Install dependencies
cd Backend/minip
pip install -r requirements.txt
```

### 1. Train the RL Model (Optional - pre-trained model included)

```bash
cd Backend/minip
python main.py train --episodes 500 --n-step --dueling
```

### 2. Start Log Collection & Monitoring

```bash
# Configure settings (optional)
# Edit Backend/minip/config.json

# Start continuous monitoring
python src/log_collection_main.py start

# Or run a single collection cycle
python src/log_collection_main.py collect-once
```

### 3. View Results

```bash
# View collected logs
cat logs/history.json

# View generated alerts
cat logs/alerts.json

# Export attack graph
python src/log_collection_main.py export-graph
```

## ✨ Key Features

### 🤖 Reinforcement Learning
- **DQN Agent** with Double DQN, N-step returns, and Dueling architecture
- **Learns from experience** without predefined attack signatures
- **Adaptive responses** based on observed behavioral patterns
- **Trained on real datasets**: CICIDS 2017 and CERT Insider Threat

### 📊 Real-Time Monitoring
- **Cross-platform**: Windows and Linux support
- **System metrics**: CPU, memory, processes, network connections
- **Failed login tracking**: Monitors authentication attempts
- **Configurable intervals**: 5-10 second collection windows

### 🌐 IP Address Intelligence
- **Extracts source/destination IPs** from network connections
- **Tracks connection patterns** per IP address
- **Identifies suspicious IPs** with abnormal behavior
- **Failed attempt correlation** per IP address

### 🕸️ Attack Graph Visualization
- **NetworkX-based graphs** showing attack paths
- **Risk score propagation** with decay factor
- **Multiple node types**: machines, processes, services, external IPs
- **JSON export** for visualization tools

### 🔔 Intelligent Alerting
- **Anomaly score-based** threshold detection
- **Suspected reason analysis**: high CPU, failed logins, excessive connections
- **Severity levels**: low, medium, high, critical
- **Suspicious IP lists** included in alerts

### 🌍 Remote Log Collection
- **HTTP/HTTPS API support** for remote machines
- **Authentication**: API key and bearer token
- **Automatic retry** with exponential backoff
- **Unified pipeline** merging local and remote logs

## 📖 Documentation

- **[Backend README](Backend/README.md)**: Detailed technical documentation
- **[RL Training Guide](Backend/README.md#-quick-start)**: Model training instructions
- **[Log Collection Guide](Backend/README.md#log-collection-system)**: Setup and configuration

## 🔬 Technical Highlights

### Enhanced Observation Space (10D)
- Base metrics: login rate, file access, CPU usage
- **Rate-of-change features**: Detect attack escalation
- **Moving averages**: Smooth out noise
- **Sustained anomaly indicators**: Identify persistent threats

### Statistical Rigor
- **Poisson distributions** for event modeling
- **Welch's t-test** for significance testing
- **Cohen's d** effect size analysis
- **95% confidence intervals**

### Attack Types Modeled
1. **Brute-Force Attacks**: Login attempt patterns
2. **Ransomware**: File encryption behavior

## 🛠️ Configuration

Edit `Backend/minip/config.json`:

```json
{
  "collection_interval_seconds": 7,
  "anomaly_threshold": 0.7,
  "log_dir": "logs",
  "remote_endpoints": [
    {
      "node_id": "server_001",
      "url": "https://api.example.com/logs",
      "auth_type": "bearer",
      "auth_token": "your_token_here"
    }
  ],
  "log_level": "INFO"
}
```

## 📊 Example Output

### Alert Example
```json
{
  "alert_id": "550e8400-e29b-41d4-a716-446655440000",
  "node_id": "local",
  "timestamp": "2024-01-15T10:30:00Z",
  "anomaly_score": 0.85,
  "severity": "high",
  "suspected_reason": "high CPU usage, multiple failed logins",
  "suspicious_ips": ["203.0.113.45", "198.51.100.23"]
}
```

### Attack Graph Export
```json
{
  "nodes": [
    {"id": "machine_001", "type": "machine", "anomaly_score": 0.85},
    {"id": "203.0.113.45", "type": "external_ip", "anomaly_score": 0.72}
  ],
  "edges": [
    {"source": "machine_001", "target": "203.0.113.45", "type": "ip_connection"}
  ]
}
```

## 🧪 Testing

```bash
cd Backend/minip

# Run all tests
pytest tests/

# Run unit tests only
pytest tests/unit/

# Run property-based tests
pytest tests/property/
```

## 📚 Datasets

- **CICIDS 2017**: Network intrusion detection dataset
- **CERT Insider Threat**: Insider threat behavior dataset

## 🤝 Contributing

This is an academic project. For questions or suggestions, please open an issue.

## 📄 License

Educational use only - Mini Project

## 🎓 Academic Context

This project demonstrates:
- Reinforcement learning for cybersecurity
- Real-time anomaly detection
- Attack graph modeling
- Cross-platform system monitoring
- Statistical validation of ML models

## 🔮 Future Work

- [ ] Frontend dashboard for visualization
- [ ] Additional attack type models
- [ ] Multi-agent coordination
- [ ] Integration with SIEM systems
- [ ] Real-time graph visualization

---

**Built with**: Python, TensorFlow, OpenAI Gym, NetworkX, Hypothesis

**Status**: Active Development 🚧
