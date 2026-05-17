# ⚡ START HERE - Get Kaisen Running in 2 Minutes

## 🎯 Goal
See real-time system metrics (CPU, Memory, Processes, Network) in the frontend dashboard.

## 📋 Prerequisites
- Python 3.8+ with virtual environment activated
- Node.js 16+ installed
- Windows OS (for current setup)

## 🚀 Step-by-Step Instructions

### Terminal 1: Start Backend

```bash
cd Backend/minip
start_all.bat
```

**Wait for this output:**
```
✓ Collector initialized
✓ Server running on http://localhost:8000
```

**Leave this terminal OPEN and RUNNING!**

---

### Terminal 2: Start Frontend

```bash
cd Frontend
npm run dev
```

**Then open browser to:** http://localhost:5173

---

## ✅ Success Checklist

After 7-10 seconds, you should see:

- [ ] Backend terminal shows: `Collection cycle completed. CPU: XX%, Memory: XX%`
- [ ] Frontend dashboard displays real CPU percentage (not 0%)
- [ ] Frontend dashboard displays real Memory percentage (not 0%)
- [ ] Process count shows actual number (e.g., 343)
- [ ] Network connections shows actual count (e.g., 113)
- [ ] Metrics update automatically every 7 seconds

## 🎉 What You'll See

### Backend Terminal (Every 7 seconds):
```
Collection cycle completed. 
CPU: 65.0%, 
Memory: 85.0%, 
Processes: 343, 
Network: 113, 
Failed logins: 0
```

### Frontend Dashboard:
```
┌─────────────────────────────────────┐
│  CPU Usage: 65%     Memory: 85%     │
│  Processes: 343     Network: 113    │
│  Unique IPs: 8      Alerts: 0       │
└─────────────────────────────────────┘
```

## 🐛 Not Working?

### Backend shows "Collection cycle completed" but CPU/Memory are 0%
✅ **FIXED!** Restart the backend - the Windows parsing has been updated.

### Frontend shows old data (from 11:14 AM)
❌ Backend collector is not running. Make sure you ran `start_all.bat` (not `start_api.bat`)

### Frontend shows "Cannot connect to backend"
❌ Backend is not running. Start it with `start_all.bat`

### Metrics not updating
❌ Check both terminals are still running. Press CTRL+C and restart both.

## 🎯 Quick Test

Open these URLs in your browser while backend is running:

1. http://localhost:8000/api/health
   - Should show: `{"status": "healthy", "service": "kaisen-api"}`

2. http://localhost:8000/api/metrics/latest
   - Should show current metrics with real CPU/Memory values

3. http://localhost:5173
   - Should show the dashboard with live data

## 🛑 Stop Everything

1. Press `CTRL+C` in backend terminal
2. Press `CTRL+C` in frontend terminal
3. Done!

## 📚 More Information

- Full guide: See `RUNNING.md`
- Backend details: See `Backend/minip/QUICKSTART.md`
- Frontend details: See `Frontend/README.md`

---

**That's it! You should now see real-time metrics updating every 7 seconds! 🎉**
