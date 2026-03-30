# SIEM Dashboard

A professional **Security Operations Center (SOC)** dashboard built with React, Tailwind CSS, and Recharts — powered by mock Wazuh SIEM data.

![Dark cybersecurity theme with sidebar navigation, stat cards, charts, and alert tables]

---

## 🚀 Quick Start

```bash
# 1. Install dependencies
npm install

# 2. Start dev server
npm start
```

Open [http://localhost:3000](http://localhost:3000) to view the dashboard.

---

## 📁 Project Structure

```
siem-dashboard/
├── public/
│   └── index.html              # HTML shell (imports Google Fonts)
├── src/
│   ├── data/
│   │   └── mockAlerts.js       # All mock alert + investigation data
│   ├── components/
│   │   ├── Sidebar.jsx         # Left nav + system status
│   │   ├── Topbar.jsx          # Search bar + user profile
│   │   ├── SeverityBadge.jsx   # Color-coded severity pill
│   │   ├── StatusBadge.jsx     # Open/Closed status pill
│   │   └── AlertDetailPanel.jsx # Slide-in alert detail panel
│   ├── pages/
│   │   ├── DashboardPage.jsx   # Stat cards + charts + recent table
│   │   ├── AlertsPage.jsx      # Filterable alert table
│   │   ├── LogsPage.jsx        # Raw log stream viewer
│   │   └── InvestigationPage.jsx # Incident report + timeline
│   ├── App.jsx                 # Root layout + page routing
│   ├── index.js                # React entry point
│   └── index.css               # Tailwind base + CSS variables
├── tailwind.config.js
├── postcss.config.js
└── package.json
```

---

## 🖥️ Pages

| Page | Description |
|------|-------------|
| **Dashboard** | Summary stat cards, bar chart timeline, pie chart, recent alerts table |
| **Alerts** | Full alert table with severity filter, IP/rule search, slide-in detail panel |
| **Logs** | Raw log stream with expandable rows showing full Wazuh log output |
| **Investigation** | Incident report with timeline, metadata, and editable analyst notes |

---

## 🎨 Design

- **Dark theme** — `#070b12` background, `#00d4ff` accent
- **Fonts** — Syne (display) + JetBrains Mono (body/code)
- **Color coding** — Red (High) · Orange (Medium) · Yellow (Low)
- **Charts** — Recharts (BarChart + PieChart)

---

## 🔌 Connecting to a Real Backend

To wire up a real Wazuh instance, replace the mock data in `src/data/mockAlerts.js` with API calls:

```js
// Example: fetch from Wazuh API
const response = await fetch("https://your-wazuh-manager:55000/alerts", {
  headers: { Authorization: `Bearer ${token}` },
});
const { data } = await response.json();
```

Then pass the fetched alerts through the same component props — no structural changes needed.

---

## 📦 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| react | ^18.2 | UI framework |
| react-dom | ^18.2 | DOM rendering |
| recharts | ^2.8 | Charts |
| tailwindcss | (via react-scripts) | Styling |

---

Built for SOC portfolio showcase · Wazuh SIEM · 2025
