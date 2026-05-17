# 🚀 Running Kaisen - Complete Guide

## Quick Start (3 Steps)

### Step 1: Start Backend Services

Open a terminal in `Backend/minip/` and run:

```bash
start_all.bat
```

You should see:
```
╔==========================================================╗
║               KAISEN BACKEND SERVICES                    ║
╚==========================================================╝

LOG COLLECTOR STARTING
✓ Collector initialized
✓ Collection interval: 7 seconds
✓ Model loaded
✓ Starting continuous collection...

API SERVER STARTING
✓ API Server initialized
✓ Server running on http://localhost:8000
```

**Keep this terminal open!** The backend will collect metrics every 7 seconds.

### Step 2: Start Frontend

Open a NEW terminal in `Frontend/` and run:

```bash
npm run electron:dev
```

Or just open in browser:
```bash
npm run dev
```
Then go to http://localhost:5173

### Step 3: Watch Real-Time Data

The frontend will now display:
- **CPU Usage**: Live processor utilization (updates every 7 seconds)
- **Memory Usage**: Live RAM utilization
- **Process Count**: Number of running processes
- **Network Connections**: Active connections
- **Unique IPs**: Distinct IP addresses
- **Alerts**: Security anomalies detected by AI

## 📊 What You'll See

### Backend Terminal Output
Every 7 seconds you'll see:
```
Collection cycle completed. CPU: 65.0%, Memory: 85.0%, Processes: 343, Network: 113, Failed logins: 0
```

### Frontend Dashboard
Real-time metrics updating automatically:
- CPU gauge showing current usage
- Memory gauge showing current usage
- Process count
- Network connections
- IP tracking
- Alert notifications

## 🔌 How It Works

```
┌─────────────────┐
│  Log Collector  │  ← Collects metrics every 7 seconds
│  (Python)       │  ← Runs anomaly detection
└────────┬────────┘
         │
         ↓ Saves to logs/history.json
         │
┌────────┴────────┐
│   API Server    │  ← Serves data via REST API
│   (Flask)       │  ← WebSocket for real-time updates
└────────┬────────┘
         │
         ↓ HTTP + WebSocket
         │
┌────────┴────────┐
│    Frontend     │  ← Displays data in real-time
│ (React+Electron)│  ← Updates every 2 seconds
└─────────────────┘
```

## 🌐 API Endpoints

Once backend is running, you can test these URLs in your browser:

- http://localhost:8000/api/health - Health check
- http://localhost:8000/api/metrics/latest - Latest metrics
- http://localhost:8000/api/stats - Overall statistics
- http://localhost:8000/api/history - Historical data
- http://localhost:8000/api/alerts - Security alerts

## 🐛 Troubleshooting

### Backend Issues

**"No module named 'src'"**
- Make sure you're in `Backend/minip/` directory
- Activate virtual environment: `.venv\Scripts\activate`

**"Port 8000 already in use"**
- Stop any other Flask/Python processes
- Or change port in `api_server.py`

**CPU/Memory showing 0%**
- This is now FIXED! You should see real values
- If still 0%, restart the backend

**Old data not updating**
- Make sure `start_all.bat` is running (not just `start_api.bat`)
- Check terminal for "Collection cycle completed" messages

### Frontend Issues

**"Cannot connect to backend"**
- Make sure backend is running on port 8000
- Check http://localhost:8000/api/health in browser

**Blank screen in Electron**
- Use browser mode instead: `npm run dev`
- Open http://localhost:5173

**Data not updating**
- Check browser console for errors
- Verify WebSocket connection in Network tab

## 📁 Data Files

All collected data is stored in `Backend/minip/logs/`:

- `history.json` - All metrics (grows over time)
- `alerts.json` - Security alerts
- `attack_graph.json` - Attack graph data
- `application.log` - Backend logs

## 🛑 Stopping Services

1. Press `CTRL+C` in backend terminal
2. Press `CTRL+C` in frontend terminal
3. All services will shut down gracefully

## 🎯 Expected Behavior

### First 7 Seconds
- Backend starts collecting
- Frontend shows "Loading..." or old data
- WebSocket connects

### After 7 Seconds
- First collection completes
- New data appears in frontend
- Metrics update automatically

### Every 7 Seconds After
- New metrics collected
- WebSocket pushes update to frontend
- Dashboard refreshes automatically
- Anomaly detection runs
- Alerts generated if threshold exceeded

## ✅ Verify Everything Works

1. **Backend Running**: Terminal shows "Collection cycle completed" every 7 seconds
2. **API Working**: http://localhost:8000/api/health returns `{"status": "healthy"}`
3. **Data Flowing**: http://localhost:8000/api/metrics/latest shows current metrics
4. **Frontend Connected**: Dashboard shows real CPU/Memory values (not 0%)
5. **Real-Time Updates**: Watch metrics change every 7 seconds

## 🎨 Frontend Features

- **Dashboard**: Overview of all metrics
- **Alerts Page**: Security alerts with severity levels
- **Attack Graph**: Visual representation of attack paths
- **Suspicious IPs**: IP addresses with high risk scores
- **Logs Page**: Historical metrics data

## 🔐 Security Notes

- Backend runs on localhost only (not exposed to internet)
- Only whitelisted commands can be executed
- Anomaly detection uses trained ML model
- All data stored locally

## 📈 Performance

- Collection interval: 7 seconds
- API response time: < 100ms
- WebSocket latency: < 50ms
- Frontend update rate: 2 seconds (polling) + real-time (WebSocket)

## 🚀 Production Deployment

For production use:
1. Change Flask to production WSGI server (gunicorn/waitress)
2. Use proper WebSocket server (not development mode)
3. Add authentication to API endpoints
4. Configure HTTPS
5. Set up log rotation
6. Monitor system resources

---

**Need Help?** Check the logs in `Backend/minip/logs/application.log`
