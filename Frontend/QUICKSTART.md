# Kaisen Frontend - Quick Start

## Fastest Way to Get Started

### Windows

1. Double-click `install.bat`
2. Wait for installation to complete
3. Edit `.env` file (set your backend URL)
4. Run: `npm run dev`
5. Open: http://localhost:5173

### Linux/Mac

```bash
chmod +x install.sh
./install.sh
# Edit .env file
npm run dev
```

## Manual Installation

```bash
# 1. Install dependencies
npm install --legacy-peer-deps

# 2. Create environment file
cp .env.example .env

# 3. Edit .env (set VITE_API_URL and VITE_WS_URL)

# 4. Start development server
npm run dev
```

## If You Get Errors

### "Cannot find module 'zustand'"

```bash
npm install zustand
```

### "Module not found" errors

```bash
rm -rf node_modules package-lock.json
npm cache clean --force
npm install --legacy-peer-deps
```

### TypeScript errors

These should be warnings only and won't prevent the app from running. If they block you:

```bash
# Temporarily disable type checking
npm run dev -- --force
```

## Testing Without Backend

The app will show connection errors if the backend isn't running. To test the UI:

1. Comment out the API calls in `src/components/Layout.tsx` (lines 45-75)
2. Import and use mock data:

```typescript
import { mockMetrics, mockAlerts, mockGraph, mockSuspiciousIPs, mockLogs } from '../services/mockData';

// In useEffect, replace API calls with:
useStore.setState({
  currentMetrics: mockMetrics,
  alerts: mockAlerts,
  attackGraph: mockGraph,
  suspiciousIPs: mockSuspiciousIPs,
  logs: mockLogs,
});
```

## Verify Installation

After running `npm run dev`, you should see:

```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

Open the URL and you should see the Kaisen landing page.

## Common Issues

| Issue | Solution |
|-------|----------|
| Port 5173 already in use | Kill the process or change port in `vite.config.ts` |
| Cannot connect to backend | Check backend is running on port 8000 |
| Blank page | Check browser console for errors |
| Module errors | Run `npm install --legacy-peer-deps` |

## Next Steps

1. ✅ Install dependencies
2. ✅ Configure .env
3. ✅ Run dev server
4. ⏳ Start backend (see Backend/README.md)
5. ⏳ Test full integration

## Need Help?

- Check `SETUP.md` for detailed instructions
- Check `FIXES.md` for list of fixes applied
- Check browser console for errors
- Check terminal for build errors

## Production Build

```bash
npm run build
```

## Electron App

```bash
npm run electron:dev
```

---

**Quick Links:**
- [Detailed Setup](SETUP.md)
- [Fixes Applied](FIXES.md)
- [Full README](README.md)
