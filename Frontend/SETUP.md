# Kaisen Frontend Setup Guide

## Quick Start

### 1. Install Dependencies

```bash
cd Frontend
npm install
```

If you encounter any errors, try:

```bash
npm install --legacy-peer-deps
```

### 2. Create Environment File

```bash
cp .env.example .env
```

Edit `.env` and set your backend URL:

```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

### 3. Run Development Server

```bash
npm run dev
```

Open http://localhost:5173 in your browser.

### 4. Run as Electron App (Optional)

```bash
npm run electron:dev
```

## Troubleshooting

### Module Not Found Errors

If you see "Cannot find module" errors:

1. Delete `node_modules` and `package-lock.json`:
   ```bash
   rm -rf node_modules package-lock.json
   ```

2. Clear npm cache:
   ```bash
   npm cache clean --force
   ```

3. Reinstall:
   ```bash
   npm install
   ```

### TypeScript Errors

If you see TypeScript errors, try:

```bash
npm run build
```

This will show you the specific errors. Most common issues:

- Missing type definitions: Install with `npm install --save-dev @types/[package-name]`
- Import errors: Check that all imports use correct paths

### Backend Connection Issues

If the frontend can't connect to the backend:

1. Ensure the backend is running on port 8000
2. Check the `.env` file has correct URLs
3. Verify CORS is enabled on the backend
4. Check browser console for specific errors

### Electron Issues

If Electron won't start:

1. Make sure the dev server is running first
2. Wait for "Local: http://localhost:5173" message
3. Then run `npm run electron:dev` in a new terminal

## Build for Production

```bash
npm run build
```

Output will be in the `dist/` directory.

## Package as Desktop App

```bash
npm run electron:build
```

Installers will be in `dist-electron/` directory.

## Common Commands

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run electron:dev` - Run Electron app in development
- `npm run electron:build` - Build Electron app for distribution
- `npm run lint` - Run ESLint

## Project Structure

```
Frontend/
├── electron/          # Electron configuration
├── src/
│   ├── components/   # React components
│   ├── pages/        # Page components
│   ├── services/     # API and WebSocket services
│   ├── store/        # State management
│   ├── types/        # TypeScript types
│   ├── App.tsx       # Main app
│   └── main.tsx      # Entry point
├── package.json
└── vite.config.ts
```

## Next Steps

1. Start the backend API (see Backend/README.md)
2. Run the frontend development server
3. Open http://localhost:5173
4. Click "Launch Dashboard" to enter the application

## Support

For issues, check:
- Browser console for errors
- Network tab for API call failures
- Backend logs for server errors
