# PCD IDS — React Dashboard Implementation Plan

## Overview
Build a premium network admin dashboard for the PCD Intrusion Detection System using **React 19 + Vite + Tailwind CSS v4**.

## Dashboard Pages / Sections

### 1. Sidebar Navigation
- Logo + brand
- Nav links: Dashboard, Alerts, History, Settings
- Collapse/expand toggle

### 2. Dashboard (Home)
- **Traffic Statistics** — Live counters with animated cards (Total packets, Inbound/Outbound, Bandwidth)
- **Suspicious Entries** — Summary cards showing count by severity (Critical / High / Medium / Low)
- **Mini Charts** — Sparkline-style traffic over time
- **Recent Alerts Feed** — Last 5-10 alerts with severity badges

### 3. Alerts Page
- Table of all alerts with severity, timestamp, source IP, description
- **Action buttons per alert**:
  - ✅ Admit (whitelist)
  - 🚫 Block Traffic
  - ⏸️ Stop Site Temporarily
- Filter/search by severity, date range, IP

### 4. History Page
- Full historical log of traffic events and past alerts
- Filterable table with pagination
- Export option (visual only for now)

### 5. Statistics Page
- Detailed traffic charts (line chart, bar chart for protocols)
- Top source IPs, top destinations
- Protocol distribution (pie/donut chart)

## Tech Stack
| Layer | Technology |
|-------|-----------|
| Build | Vite (latest) |
| UI | React 19 |
| Styling | Tailwind CSS v4 |
| Charts | Recharts |
| Icons | Lucide React |
| Routing | React Router v7 |

## File Structure
```
frontend/
├── index.html
├── package.json
├── vite.config.js
├── tailwind.config.js
├── postcss.config.js
├── src/
│   ├── main.jsx
│   ├── App.jsx
│   ├── index.css          (Tailwind base + custom)
│   ├── components/
│   │   ├── Sidebar.jsx
│   │   ├── Sidebar.css
│   │   ├── StatCard.jsx
│   │   ├── StatCard.css
│   │   ├── AlertRow.jsx
│   │   ├── AlertRow.css
│   │   ├── TrafficChart.jsx
│   │   ├── TrafficChart.css
│   │   └── ...
│   ├── pages/
│   │   ├── Dashboard.jsx
│   │   ├── Dashboard.css
│   │   ├── Alerts.jsx
│   │   ├── Alerts.css
│   │   ├── History.jsx
│   │   ├── History.css
│   │   └── Statistics.jsx
│   │   └── Statistics.css
│   └── data/
│       └── mockData.js    (realistic mock data)
```

## Design System
- **Dark mode** cybersecurity theme
- **Colors**: Deep navy bg (#0a0e1a), cyan accent (#00d4ff), purple accent (#7b61ff), green (#00e68a), red for critical (#ff4757)
- **Font**: Inter (Google Fonts)
- **Glass morphism** cards with backdrop-blur
- **Micro-animations** on hover, transitions on page change
- **Responsive** layout

## Steps
1. Initialize Vite + React project in `frontend/`
2. Install dependencies (tailwindcss, recharts, lucide-react, react-router-dom)
3. Configure Tailwind with custom theme
4. Create base styles in `index.css`
5. Build Sidebar component
6. Build StatCard, AlertRow, TrafficChart components
7. Build Dashboard page
8. Build Alerts page with action buttons
9. Build History page
10. Build Statistics page with charts
11. Wire up routing in App.jsx
12. Add mock data
13. Test and polish
