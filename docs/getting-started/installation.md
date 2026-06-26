# Installation Guide

This guide will walk you through installing Kaisen on your system.

## Prerequisites

Before installing Kaisen, ensure you have the following:

### System Requirements

- **Operating System**: Windows 10/11, Linux (Ubuntu 18.04+), or macOS 10.14+
- **CPU**: 4 cores minimum, 8 cores recommended
- **RAM**: 8 GB minimum, 16 GB recommended
- **Storage**: 10 GB free space minimum
- **Network**: Internet connection for initial setup

### Software Requirements

- **Python**: 3.8 or higher ([Download](https://www.python.org/downloads/))
- **Node.js**: 18.x or higher ([Download](https://nodejs.org/))
- **npm**: 9.x or higher (included with Node.js)
- **Git**: For cloning the repository

## Backend Installation

### Step 1: Navigate to Backend Directory

```bash
cd Backend/minip
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/macOS
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install all required Python packages including:
- TensorFlow (for ML models)
- Flask (for API server)
- NumPy, Pandas (for data processing)
- And more...

### Step 4: Verify Installation

```bash
python -c "import tensorflow; print('TensorFlow version:', tensorflow.__version__)"
```

## Frontend Installation

### Step 1: Navigate to Frontend Directory

```bash
cd Frontend
```

### Step 2: Install Dependencies

```bash
npm install
```

This will install all required Node.js packages including:
- React 18
- Electron 28
- Material UI 5
- Vite
- And more...

### Step 3: Verify Installation

```bash
npm list react
```

## Configuration

### Backend Configuration

Create a configuration file at `Backend/minip/config.json`:

```json
{
  "collection_interval": 7,
  "api_port": 8000,
  "anomaly_threshold": 0.7,
  "log_level": "INFO",
  "retention_days": 30
}
```

### Frontend Configuration

Create a `.env` file in `Frontend/`:

```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

## Starting Kaisen

### Start Backend

```bash
cd Backend/minip
.\start_all.bat
```

### Start Frontend

Open a new terminal:

```bash
cd Frontend
npm run electron:dev
```

Or for browser-only mode:

```bash
npm run dev
```

Then visit [http://localhost:5173](http://localhost:5173)

## Verification

After starting both services:

1. **Check Backend**: Visit [http://localhost:8000/api/health](http://localhost:8000/api/health)
   - Should return: `{"status": "healthy"}`

2. **Check Metrics**: Visit [http://localhost:8000/api/metrics/latest](http://localhost:8000/api/metrics/latest)
   - Should show current system metrics

3. **Check Frontend**: Dashboard should show live metrics updating every 7 seconds

## Troubleshooting

### Backend Issues

**"No module named 'src'"**
- Make sure you're in `Backend/minip/` directory
- Activate virtual environment: `.venv\Scripts\activate`

**"Port 8000 already in use"**
- Stop any other Flask/Python processes
- Or change port in `config.json`

**"Cannot find best_model.h5"**
- Run: `python src/train.py` to train the model
- Or use rule-based fallback (automatic)

### Frontend Issues

**"Cannot connect to backend"**
- Verify backend is running on port 8000
- Check `.env` file has correct `VITE_API_URL`
- Check browser console for CORS errors

**"npm install fails"**
- Clear npm cache: `npm cache clean --force`
- Delete `node_modules` and `package-lock.json`
- Run `npm install` again

**"Electron window is blank"**
- Check DevTools console for errors
- Try browser mode: `npm run dev`
- Check that backend is running

## Next Steps

Now that Kaisen is installed, learn how to:

- [Configure Kaisen](configuration.md) - Customize settings for your environment
- [Quick Start](quickstart.md) - Get up and running in 5 minutes
- [How to Use](../user-guide/how-to-use.md) - Learn to use all features effectively

## Uninstallation

To remove Kaisen:

```bash
# Stop all services
# Delete project directory
rm -rf /path/to/kaisen

# Optional: Remove virtual environments and node_modules
# These are within the project directory and will be removed
```

---

**Need Help?** Check the [troubleshooting guide](../troubleshooting.md) or refer to the main [README](../../README.md).