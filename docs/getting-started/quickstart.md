# Quick Start Guide

Get Kaisen up and running in under 5 minutes with this quick start guide.

## Prerequisites

Before starting, ensure you have:
- Python 3.8+ installed
- Node.js 18+ installed
- Git installed (optional, for cloning)

## 3-Step Quick Start

### Step 1: Start the Backend

Open a terminal and navigate to the backend:

```bash
cd Backend/minip
.\start_all.bat
```

You should see output like:
```
========================================
  Kaisen Backend - Starting All Services
========================================

LOG COLLECTOR STARTING
✓ Collector initialized
✓ Collection interval: 7 seconds        
✓ Model loaded
✓ Starting continuous collection...

API SERVER STARTING
✓ API Server initialized
✓ Server running on http://localhost:8000
```

**Keep this terminal open!** The backend needs to stay running.

### Step 2: Start the Frontend

Open a **new** terminal (don't close the backend one):

```bash
cd Frontend
npm run electron:dev
```

The Electron desktop app will open automatically. You can also access it in your browser at [http://localhost:5173](http://localhost:5173).

### Step 3: Verify Everything is Working

1. **Dashboard shows data**: You should see live metrics updating every 7 seconds
2. **CPU/Memory gauges**: Should show actual values (not 0%)
3. **Network connections**: Shows active connections

Test the API in your browser:
- [http://localhost:8000/api/health](http://localhost:8000/api/health) should return `{"status": "healthy"}`
- [http://localhost:8000/api/metrics/latest](http://localhost:8000/api/metrics/latest) should show current metrics

## What You'll See

### Dashboard

The main dashboard displays:

| Component | Description |
|-----------|-------------|
| **CPU Usage** | Live processor utilization with gauge |
| **Memory Usage** | RAM utilization with trend graph |
| **Process Count** | Number of running processes |
| **Network Connections** | Active connections count |
| **Unique IPs** | Distinct IP addresses detected |
| **Failed Logins** | Authentication failures |

### Real-Time Updates

- Metrics update automatically every 7 seconds
- WebSocket provides instant updates to the dashboard
- Alerts appear immediately when anomalies are detected

## Quick Navigation

Use the left sidebar to navigate between sections:

- **Dashboard**: Overview of all metrics
- **Alerts**: Security alerts and notifications
- **Attack Graph**: Visual attack path analysis
- **Suspicious IPs**: IP reputation and risk scoring
- **Logs**: Historical system logs

## Common Tasks

### Viewing Alerts

1. Click **Alerts** in the sidebar
2. Use filters to show Critical/High/Medium/Low alerts
3. Click an alert to view details and AI explanation
4. Acknowledge or resolve the alert

### Analyzing Attack Graph

1. Click **Attack Graph** in the sidebar
2. Use mouse wheel to zoom in/out
3. Click nodes to view details
4. Drag to pan the view

### Monitoring Suspicious IPs

1. Click **Suspicious IPs** in the sidebar
2. Review IPs by risk score
3. Click an IP to view geolocation and activity
4. Take action (whitelist/blacklist)

## Next Steps

Now that you're up and running:

1. **[Configuration Guide](configuration.md)**: Customize Kaisen for your environment
2. **[User Guide](../user-guide/how-to-use.md)**: Learn all features in depth
3. **[Architecture Overview](../architecture/overview.md)**: Understand how Kaisen works

## Troubleshooting Quick Fixes

### Dashboard shows "Loading..."

- Check that backend is running: [http://localhost:8000/api/health](http://localhost:8000/api/health)
- Refresh the frontend page
- Check browser console for errors

### Metrics showing 0%

- Normal for first 7 seconds - wait for first collection cycle
- If persists, restart the backend
- Check logs in `Backend/minip/logs/application.log`

### Cannot connect to backend

- Ensure backend terminal is still running
- Check if port 8000 is blocked by firewall
- Verify no other service is using port 8000

---

**Need more help?** Check the full [troubleshooting guide](../troubleshooting.md).