# Configuration Guide

Learn how to configure Kaisen for your specific environment and use case.

## Configuration Files

Kaisen uses several configuration files to control its behavior:

### Backend Configuration (`config.json`)

Located in `Backend/minip/config.json`:

```json
{
  "collection_interval": 7,
  "api_port": 8000,
  "api_host": "0.0.0.0",
  "anomaly_threshold": 0.7,
  "log_level": "INFO",
  "retention_days": 30,
  "max_log_file_size_mb": 100,
  "enable_websocket": true,
  "cors_origins": ["http://localhost:5173", "http://127.0.0.1:5173"],
  "model": {
    "path": "models/best_model.h5",
    "fallback_enabled": true,
    "input_features": 13
  },
  "collection": {
    "cpu": true,
    "memory": true,
    "processes": true,
    "network": true,
    "failed_logins": true,
    "ip_tracking": true
  },
  "alerts": {
    "enabled": true,
    "cooldown_seconds": 300,
    "severity_thresholds": {
      "critical": 0.9,
      "high": 0.75,
      "medium": 0.6,
      "low": 0.4
    }
  }
}
```

#### Configuration Options Explained

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `collection_interval` | integer | 7 | Seconds between metric collections |
| `api_port` | integer | 8000 | Port for API server |
| `api_host` | string | "0.0.0.0" | Host binding for API server |
| `anomaly_threshold` | float | 0.7 | Threshold for anomaly detection (0-1) |
| `log_level` | string | "INFO" | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `retention_days` | integer | 30 | Days to retain historical data |

### Frontend Configuration (`.env`)

Located in `Frontend/.env`:

```env
# API Configuration
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000

# Feature Flags
VITE_ENABLE_WEBSOCKET=true
VITE_ENABLE_MOCK_DATA=false

# UI Configuration
VITE_REFRESH_INTERVAL=2000
VITE_CHART_HISTORY_POINTS=50
VITE_MAX_ALERTS_DISPLAY=100

# Theme
VITE_DEFAULT_THEME=dark

# Development
VITE_DEBUG=false
```

#### Frontend Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `VITE_API_URL` | string | "http://localhost:8000" | Backend API URL |
| `VITE_WS_URL` | string | "ws://localhost:8000" | WebSocket URL |
| `VITE_REFRESH_INTERVAL` | integer | 2000 | Dashboard refresh interval (ms) |
| `VITE_CHART_HISTORY_POINTS` | integer | 50 | Number of points in trend charts |

## Environment-Specific Configuration

### Development Environment

`config.development.json`:

```json
{
  "collection_interval": 5,
  "log_level": "DEBUG",
  "retention_days": 7,
  "enable_mock_data": true,
  "cors_origins": ["*"],
  "alerts": {
    "enabled": true,
    "cooldown_seconds": 60
  }
}
```

### Production Environment

`config.production.json`:

```json
{
  "collection_interval": 10,
  "api_host": "127.0.0.1",
  "log_level": "WARNING",
  "retention_days": 90,
  "enable_websocket": true,
  "cors_origins": ["https://yourdomain.com"],
  "max_log_file_size_mb": 500,
  "alerts": {
    "enabled": true,
    "cooldown_seconds": 600,
    "severity_thresholds": {
      "critical": 0.95,
      "high": 0.8,
      "medium": 0.65,
      "low": 0.5
    }
  },
  "security": {
    "enable_https": true,
    "cert_file": "/path/to/cert.pem",
    "key_file": "/path/to/key.pem",
    "rate_limiting": {
      "enabled": true,
      "requests_per_minute": 100
    }
  }
}
```

## Advanced Configuration

### Custom Collection Commands

You can customize the commands used for data collection:

```json
{
  "collection": {
    "cpu": true,
    "cpu_command": "wmic cpu get loadpercentage /value",
    "memory": true,
    "memory_command": "wmic OS get TotalVisibleMemorySize,FreePhysicalMemory /value",
    "custom_metrics": {
      "disk_io": {
        "enabled": true,
        "command": "wmic logicaldisk get size,freespace,caption",
        "parser": "disk_parser"
      }
    }
  }
}
```

### Alert Routing

Configure where alerts are sent:

```json
{
  "alerts": {
    "routing": {
      "webhook": {
        "enabled": true,
        "url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
        "headers": {
          "Content-Type": "application/json"
        }
      },
      "email": {
        "enabled": true,
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "username": "alerts@yourdomain.com",
        "password": "${EMAIL_PASSWORD}",
        "recipients": ["security@yourdomain.com"]
      },
      "sms": {
        "enabled": true,
        "provider": "twilio",
        "account_sid": "${TWILIO_SID}",
        "auth_token": "${TWILIO_TOKEN}",
        "from_number": "+1234567890",
        "to_numbers": ["+0987654321"]
      }
    }
  }
}
```

### Model Configuration

Configure the ML model behavior:

```json
{
  "model": {
    "path": "models/best_model.h5",
    "fallback_enabled": true,
    "input_features": 13,
    "sequence_length": 10,
    "prediction_batch_size": 32,
    "retraining": {
      "enabled": true,
      "interval_days": 30,
      "min_samples": 10000,
      "validation_split": 0.2
    },
    "explainability": {
      "enabled": true,
      "method": "shap",
      "samples": 100
    }
  }
}
```

## Configuration Best Practices

### 1. Environment Separation

Always use separate configurations for different environments:

```
Backend/minip/
├── config.json              # Default/base configuration
├── config.development.json  # Development overrides
├── config.staging.json      # Staging overrides
├── config.production.json   # Production overrides
```

### 2. Sensitive Data

Never commit sensitive data to version control:

```json
{
  "database": {
    "password": "${DB_PASSWORD}"  // Use environment variable
  }
}
```

Use `.env` files (not committed) or secret management tools.

### 3. Validation

Always validate configuration on startup:

```python
# config_validator.py
import jsonschema

CONFIG_SCHEMA = {
    "type": "object",
    "properties": {
        "collection_interval": {
            "type": "integer",
            "minimum": 1,
            "maximum": 3600
        }
    },
    "required": ["collection_interval"]
}

def validate_config(config):
    jsonschema.validate(config, CONFIG_SCHEMA)
```

### 4. Documentation

Document all configuration options:

- Use comments in JSON files (if supported)
- Maintain a configuration reference guide
- Include examples for common scenarios
- Document default values and valid ranges

### 5. Testing

Test configuration changes:

```python
# test_config.py
import pytest
from config import load_config

def test_config_loading():
    config = load_config('config.json')
    assert 'collection_interval' in config
    assert config['collection_interval'] > 0

def test_environment_override():
    config = load_config('config.json', env='production')
    assert config['log_level'] == 'WARNING'
```

## Troubleshooting Configuration Issues

### Common Problems

1. **Configuration Not Loading**
   - Check file path and permissions
   - Validate JSON syntax
   - Check for typos in keys

2. **Changes Not Taking Effect**
   - Restart the service after changes
   - Check if environment variable is overriding
   - Verify correct config file is being loaded

3. **Environment-Specific Issues**
   - Check environment variable `KAISEN_ENV`
   - Verify environment-specific config exists
   - Check for missing required fields

### Debug Mode

Enable debug logging to troubleshoot:

```json
{
  "log_level": "DEBUG",
  "debug": {
    "config_loading": true,
    "validation": true,
    "overrides": true
  }
}
```

---

For more information, see:
- [Installation Guide](installation.md) - Detailed installation instructions
- [Quick Start](quickstart.md) - Get running in minutes
- [User Guide](../user-guide/how-to-use.md) - Learn to use all features