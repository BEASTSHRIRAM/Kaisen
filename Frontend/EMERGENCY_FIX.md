# Emergency Fix for White Screen

## The Problem
The error `The requested module '/src/store/useStore.ts' does not provide an export named 'useStore'` is causing a white screen.

## Quick Fix Steps

### Step 1: Stop the dev server
Press `Ctrl+C` in the terminal running `npm run dev`

### Step 2: Clear Vite cache
```bash
cd Frontend
rm -rf node_modules/.vite
rm -rf dist
```

### Step 3: Restart the dev server
```bash
npm run dev
```

### Step 4: Hard refresh browser
- Windows/Linux: `Ctrl + Shift + R`
- Mac: `Cmd + Shift + R`

### Step 5: Clear browser cache
1. Open DevTools (F12)
2. Right-click the refresh button
3. Select "Empty Cache and Hard Reload"

## If Still Not Working

Try this alternative fix:

```bash
# Stop dev server
# Then run:
cd Frontend
rm -rf node_modules/.vite
rm -rf node_modules/.cache
npm run dev
```

## Alternative: Use Default Export

If the named export still doesn't work, change the import in `Layout.tsx`:

**Change from:**
```typescript
import { useStore } from '../store/useStore';
```

**To:**
```typescript
import useStore from '../store/useStore';
```

Then do the same in ALL files that import useStore:
- `src/components/pages/Dashboard.tsx`
- `src/components/pages/AlertsPage.tsx`
- `src/components/pages/AttackGraphPage.tsx`
- `src/components/pages/SuspiciousIPsPage.tsx`
- `src/components/pages/LogsPage.tsx`

## Nuclear Option

If nothing works, delete and reinstall:

```bash
cd Frontend
rm -rf node_modules
rm package-lock.json
npm install --legacy-peer-deps
npm run dev
```
