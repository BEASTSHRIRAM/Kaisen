# Kaisen Log Collection Backend - Usage Guide

## Overview

The Kaisen Log Collection Backend is a security monitoring system that collects system logs, detects anomalies using machine learning, and builds attack graphs to visualize potential security threats.

## Installation

Ensure you have Python 3.8+ and all dependencies installed:

```bash
cd Backend/minip
pip install -r requirements.txt
```

## Configuration

Create or edit `config.json` in the `Backend/minip` directory:

```json
{
  "collection_interval_seconds": 7,
  "anomaly_threshold": 0.7,
  "log_dir": "logs",
  "model_path": "models/best_model.h5",
  "log_level": "INFO"
}
```

## Commands

### Start Continuous Collection

Start the log collector in continuous mode, collecting logs at the configured interval:

```bash
python -m src.log_collection_main start
```

Press `Ctrl+C` to stop gracefully.

### Single Collection Cycle

Perform a single collection cycle and exit:

```bash
python -m src.log_collection_main collect-once
```

### Collect and Export Graph

Collect logs once and export the attack graph:

```bash
python -m src.log_collection_main collect-once --export-graph
python -m src.log_collection_main collect-once --export-graph -o custom_graph.json
```

### Export Attack Graph

Export the current attack graph without collecting new data:

```bash
python -m src.log_collection_main export-graph
python -m src.log_collection_main export-graph -o logs/attack_graph.json
```

## Output Files

All output files are stored in the `logs/` directory:

- **history.json**: All collected log entries with system metrics
- **alerts.json**: Generated security alerts when anomalies are detected
- **attack_graph.json**: Attack graph visualization data (nodes and edges)
- **application.log**: Application logs for debugging

## Example Workflow

1. **Initial Setup**: Configure `config.json` with your settings
2. **Test Collection**: Run `python -m src.log_collection_main collect-once` to verify setup
3. **Start Monitoring**: Run `python -m src.log_collection_main start` for continuous monitoring
4. **Review Alerts**: Check `logs/alerts.json` for security alerts
5. **Analyze Graph**: Export and visualize the attack graph

## Troubleshooting

### Model Loading Warnings

If you see warnings about model loading, ensure the model file exists at the configured path:
- Default: `Backend/minip/models/best_model.h5`
- Check `config.json` for custom model path

### Permission Errors

Some system commands require elevated privileges:
- **Windows**: Run as Administrator for full access to event logs
- **Linux**: Use `sudo` for access to system logs

### Remote Endpoint Failures

If remote endpoints fail to connect:
- Verify the endpoint URL is accessible
- Check authentication tokens are valid
- Ensure network connectivity

## Signal Handling

The application handles shutdown signals gracefully:
- **SIGINT** (Ctrl+C): Stop collection and exit cleanly
- **SIGTERM**: Graceful shutdown for service management

## Advanced Usage

### Custom Configuration File

Use a custom configuration file:

```bash
python -m src.log_collection_main -c /path/to/config.json start
```

### Integration with Services

For production deployment, integrate with systemd (Linux) or Windows Services:

**Linux systemd example:**
```ini
[Unit]
Description=Kaisen Log Collection Backend
After=network.target

[Service]
Type=simple
User=kaisen
WorkingDirectory=/opt/kaisen/Backend/minip
ExecStart=/usr/bin/python3 -m src.log_collection_main start
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

## Requirements Validated

This implementation validates the following requirements:
- **9.1**: Configuration management from JSON file
- **11.1**: Integration with existing Backend/minip/ codebase
- Full pipeline integration: collection → processing → detection → alerting → storage
