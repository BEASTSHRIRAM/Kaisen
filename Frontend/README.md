# Kaisen Frontend

Electron-based desktop cybersecurity monitoring application built with React, TypeScript, and Material UI.

## Features

- **Real-Time Dashboard**: Monitor system metrics (CPU, memory, network, failed logins) with live charts
- **Security Alerts**: View and filter security alerts by severity and search criteria
- **Attack Graph Visualization**: Interactive D3.js graph showing attack paths and relationships
- **Suspicious IP Tracking**: Monitor and analyze suspicious IP addresses with risk scoring
- **System Logs**: Searchable log viewer with real-time updates
- **WebSocket Support**: Real-time updates for metrics and alerts
- **Dark Theme**: Professional cybersecurity-themed UI

## Technology Stack

- **Framework**: React 18 with TypeScript
- **Desktop**: Electron 28
- **UI Library**: Material UI 5
- **State Management**: Zustand
- **Charts**: Chart.js with react-chartjs-2
- **Graph Visualization**: D3.js
- **HTTP Client**: Axios
- **Build Tool**: Vite
- **Routing**: React Router v6

## Prerequisites

- Node.js 18+ and npm
- Backend API running (see Backend/README.md)

## Installation

```bash
cd Frontend
npm install
```

## Configuration

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Edit `.env` to configure your backend API URL:

```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

## Development

### Run in Browser (Development Mode)

```bash
npm run dev
```

Open http://localhost:5173 in your browser.

### Run as Electron App

```bash
npm run electron:dev
```

This will start both the Vite dev server and Electron app.

## Building

### Build for Production

```bash
npm run build
```

### Build Electron App

```bash
npm run electron:build
```

This creates distributable packages in `dist-electron/`:
- Windows: `.exe` installer
- Linux: `.AppImage`

## Project Structure

```
Frontend/
├── electron/              # Electron main process
│   ├── main.js           # Main Electron entry point
│   └── preload.js        # Preload script
├── src/
│   ├── components/       # React components
│   │   ├── pages/       # Page components
│   │   │   ├── LandingPage.tsx
│   │   │   ├── Dashboard.tsx
│   │   │   ├── AlertsPage.tsx
│   │   │   ├── AttackGraphPage.tsx
│   │   │   ├── SuspiciousIPsPage.tsx
│   │   │   └── LogsPage.tsx
│   │   ├── Layout.tsx   # Main layout with sidebar
│   │   └── MetricCard.tsx
│   ├── services/        # API and WebSocket services
│   │   ├── api.ts
│   │   └── websocket.ts
│   ├── store/           # Zustand state management
│   │   └── useStore.ts
│   ├── types/           # TypeScript interfaces
│   │   └── index.ts
│   ├── App.tsx          # Main app component
│   ├── main.tsx         # React entry point
│   ├── theme.ts         # Material UI theme
│   └── index.css        # Global styles
├── package.json
├── tsconfig.json
├── vite.config.ts
└── index.html
```

## API Integration

The frontend expects the following backend endpoints:

### REST API

- `GET /metrics/latest` - Get latest system metrics
- `GET /alerts` - Get security alerts (supports `?severity=` and `?limit=` params)
- `GET /graph` - Get attack graph data
- `GET /suspicious-ips` - Get suspicious IP addresses
- `GET /history` - Get system log history (supports `?limit=` param)

### WebSocket

- `/ws/alerts` - Real-time alert notifications
- `/ws/metrics` - Real-time metric updates

## Features Overview

### Landing Page

- Professional landing page with feature highlights
- "Launch Dashboard" button to enter the application

### Dashboard

- Real-time metric cards (CPU, Memory, Network, Failed Logins, Anomaly Score)
- Line charts showing metric trends over time
- Recent alerts panel
- System health overview with progress bars

### Alerts Page

- Filterable table of security alerts
- Filter by severity (critical, high, medium, low)
- Search by node ID, reason, or IP address
- Color-coded severity indicators
- Displays suspicious IPs associated with each alert

### Attack Graph Page

- Interactive force-directed graph visualization
- Nodes colored by risk level (green → yellow → orange → red)
- Different node types: machines, processes, services, external IPs
- Drag nodes to reposition
- Zoom and pan controls
- Legend showing risk levels

### Suspicious IPs Page

- Table of suspicious IP addresses
- Connection count and failed attempt metrics
- Risk score and risk level indicators
- Visual progress bars for metrics
- Search functionality

### Logs Page

- Scrollable table of system logs
- Real-time updates
- Search by node ID or timestamp
- Color-coded status indicators
- Sticky header for easy navigation

## Customization

### Theme

Edit `src/theme.ts` to customize colors and styling.

### API URL

Change the API base URL in `.env` or `src/services/api.ts`.

### Polling Interval

Adjust the polling interval in `src/components/Layout.tsx` (default: 10 seconds).

## Troubleshooting

### Backend Connection Issues

- Ensure the backend API is running
- Check the API URL in `.env`
- Verify CORS is enabled on the backend

### WebSocket Not Connecting

- Check the WebSocket URL in `.env`
- Ensure WebSocket endpoints are available on the backend
- Check browser console for connection errors

### Electron Build Issues

- Clear `node_modules` and reinstall: `rm -rf node_modules && npm install`
- Update Electron: `npm install electron@latest`

## License

[Specify License]

## Contact

[Contact Information]
