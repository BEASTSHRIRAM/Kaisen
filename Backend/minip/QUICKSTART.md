# Kaisen Backend - Quick Start Guide

## 🚀 Start Everything (Recommended)

Run this single command to start both the log collector and API server:

```bash
start_all.bat
```

This will:
- ✅ Collect system metrics every 7 seconds
- ✅ Run anomaly detection on collected data
- ✅ Serve data via REST API on http://localhost:8000
- ✅ Provide real-time WebSocket updates to frontend

## 📊 What You'll See

Once started, the backend will continuously collect:
- **CPU Usage**: Current processor utilization (%)
- **Memory Usage**: RAM utilization (%)
- **Process Count**: Number of running processes
- **Network Connections**: Active network connections
- **Unique IPs**: Distinct IP addresses in connections
- **Failed Logins**: Failed authentication attempts

## 🌐 API Endpoints

The API server provides these endpoints:

- `GET /api/metrics/latest` - Most recent system metrics
- `GET /api/alerts` - Security alerts
- `GET /api/graph` - Attack graph data
- `GET /api/suspicious-ips` - Suspicious IP addresses
- `GET /api/history` - Historical metrics
- `GET /api/stats` - Overall statistics
- `GET /api/health` - Health check

## 🔌 WebSocket Events

Real-time updates via WebSocket:
- `metrics` - New metrics collected (every 7 seconds)
- `alert` - New security alert generated

## 🛑 Stop Services

Press `CTRL+C` in the terminal to stop all services.

## 📁 Data Storage

Collected data is stored in:
- `logs/history.json` - All collected metrics
- `logs/alerts.json` - Generated alerts
- `logs/attack_graph.json` - Attack graph data
- `logs/application.log` - Application logs

## 🔧 Alternative: Run Services Separately

If you need to run services separately:

### Start Log Collector Only
```bash
start_collector.bat
```

### Start API Server Only
```bash
start_api.bat
```

## ✅ Verify It's Working

1. Open browser to http://localhost:8000/api/health
2. You should see: `{"status": "healthy", "service": "kaisen-api"}`
3. Check http://localhost:8000/api/metrics/latest for real-time data
4. Watch the terminal for collection logs every 7 seconds

## 🎯 Connect Frontend

Once the backend is running:
1. Navigate to the Frontend directory
2. Run `npm run electron:dev`
3. The frontend will automatically connect to http://localhost:8000
4. You'll see real-time metrics updating every 7 seconds

## 🐛 Troubleshooting

**No data showing?**
- Make sure `start_all.bat` is running
- Check that port 8000 is not in use
- Look at `logs/application.log` for errors

**CPU/Memory showing 0%?**
- This is now fixed! The Windows parsing has been updated
- Restart the services to see real values

**Old data not updating?**
- The collector must be running continuously
- Check terminal for "Collection cycle completed" messages
- Verify `logs/history.json` is being updated
