# 🛡️ XSiem — Wazuh SIEM Dashboard

<div align="center">

![XSiem Banner](https://img.shields.io/badge/XSiem-SOC%20Dashboard-00d4ff?style=for-the-badge&logo=shield&logoColor=white)

[![React](https://img.shields.io/badge/React-18.2-61DAFB?style=flat-square&logo=react)](https://reactjs.org)
[![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=flat-square&logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)
[![Wazuh](https://img.shields.io/badge/Wazuh-4.9.2-blue?style=flat-square)](https://wazuh.com)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

**A full-stack, production-grade Security Operations Center (SOC) dashboard built on Wazuh SIEM.**  
Real attacks. Real alerts. Real monitoring. 800+ live security events.

[Features](#-features) • [Architecture](#-architecture) • [Quick Start](#-quick-start) • [Screenshots](#-screenshots) • [Attack Lab](#-attack-simulation-lab) • [API Docs](#-api-endpoints)

</div>

---

## 🎯 What Is This?

XSiem is a **complete home lab SIEM project** that demonstrates real-world SOC analyst skills:

- 🔴 **Attack** a target machine using Kali Linux (nmap, Hydra, Nikto)
- 👁️ **Detect** threats in real-time via Wazuh SIEM agent monitoring
- 📊 **Visualize** 800+ live security events in a custom React dashboard
- 🚨 **Alert** — automated HTML emails sent for every high-severity threat
- 🔍 **Investigate** — full incident timeline, raw logs, analyst notes

> ⚠️ All attacks were performed exclusively on personally owned machines in a controlled home lab. This is a legal and ethical security research project.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📡 **Real-Time Monitoring** | Fetches live alerts from Wazuh OpenSearch with 30s auto-refresh |
| 🎨 **Severity Classification** | Color-coded High/Medium/Low matching Wazuh rule levels 1-15 |
| 📊 **Interactive Charts** | Bar chart timeline + donut severity split (Recharts) |
| 🔍 **Alert Search & Filter** | Filter by severity, search by IP, rule name, or agent |
| 📋 **Alert Detail Panel** | Slide-in panel with raw logs, IPs, timestamps, Mark as Resolved |
| 🖥️ **Agents Monitoring** | Live status, OS, IP, version for all connected Wazuh agents |
| 🕵️ **Investigation Page** | Incident report, event timeline, editable analyst notes |
| 📧 **Email Alerts** | Automated HTML email for every HIGH severity alert via Gmail SMTP |
| 🔔 **Toast Notifications** | In-browser pop-ups when new high-severity alerts detected |
| 🔄 **Auto-Refresh** | 30-second sync + manual refresh with last-updated timestamp |
| 📺 **Live Log Stream** | Expandable raw Wazuh log entries per alert |
| 🌐 **Swagger API Docs** | Interactive API documentation at `/docs` |
| 🎭 **Mock Data Fallback** | Demo always works even if backend is offline |
| 🌙 **Dark SOC Theme** | JetBrains Mono + Syne fonts, cybersecurity aesthetic |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        HOME LAB SETUP                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌──────────────┐    attacks     ┌──────────────────────┐     │
│   │  Kali Linux  │ ─────────────► │   Windows 11 Host    │     │
│   │  VM (Attacker│                │   (Target Machine)   │     │
│   │  192.168.1.176│               │   192.168.1.175      │     │
│   │              │                │   Wazuh Agent 4.9.2  │     │
│   │  nmap        │                └──────────┬───────────┘     │
│   │  Hydra       │                           │ logs            │
│   │  Nikto       │                           ▼                 │
│   └──────────────┘                ┌──────────────────────┐     │
│                                   │   Docker Containers  │     │
│                                   │                      │     │
│   ┌──────────────┐                │  Wazuh Manager       │     │
│   │    React     │                │  Wazuh Indexer       │     │
│   │  Dashboard   │ ◄──────────── │  (OpenSearch:9200)   │     │
│   │  :3000       │   FastAPI      │  Wazuh Dashboard     │     │
│   └──────────────┘   :4000        └──────────────────────┘     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | React 18 + Recharts + Tailwind CSS | Dashboard UI, charts, alert tables |
| **Backend** | Python 3.13 + FastAPI + uvicorn | REST API, Wazuh auth, OpenSearch queries |
| **SIEM Engine** | Wazuh 4.9.2 | Log collection, rule matching, alert generation |
| **Data Store** | OpenSearch (Wazuh Indexer) | Stores 800+ real security events |
| **Containers** | Docker Desktop + docker-compose | Wazuh Manager, Indexer, Dashboard |
| **Attack Tools** | nmap, Hydra, Nikto, Netcat | Port scanning, brute force, web scanning |
| **Networking** | VirtualBox Bridged Adapter | Kali on same subnet as Windows target |
| **Email** | Python smtplib + Gmail SMTP | Automated high-severity notifications |
| **OS** | Windows 11 + Kali Linux | Host and attacker machines |

---

## 🚀 Quick Start

### Prerequisites

- Windows 11 with at least **8GB RAM**
- [Docker Desktop](https://docker.com/products/docker-desktop) with WSL2
- [Python 3.11+](https://python.org/downloads)
- [Node.js 18+](https://nodejs.org)
- [VirtualBox](https://virtualbox.org) + Kali Linux VM

---

### Step 1 — Start Wazuh (Docker)

```bash
git clone https://github.com/wazuh/wazuh-docker.git
cd wazuh-docker
git checkout v4.9.2
cd single-node

# Generate certificates (first time only)
docker-compose -f generate-indexer-certs.yml run --rm generator

# Start Wazuh
docker-compose up -d
```

Verify at `https://localhost` → Login: `admin / SecretPassword`

---

### Step 2 — Start the Backend

```bash
git clone https://github.com/YOUR_USERNAME/xsiem.git
cd xsiem/siem-backend

# Install dependencies
py -m pip install fastapi uvicorn httpx python-dotenv

# Start server
py -m uvicorn main:app --reload --port 4000
```

Visit `http://localhost:4000/docs` — interactive API docs.

---

### Step 3 — Start the Frontend

```bash
cd xsiem/siem-dashboard

npm install
npm start
```

Visit `http://localhost:3000` — your SOC dashboard.

---

### Step 4 — Install Wazuh Agent on Windows

```powershell
# Run as Administrator
Invoke-WebRequest -Uri "https://packages.wazuh.com/4.x/windows/wazuh-agent-4.9.2-1.msi" `
  -OutFile "$env:TEMP\wazuh-agent.msi"

msiexec.exe /i "$env:TEMP\wazuh-agent.msi" /q `
  WAZUH_MANAGER="127.0.0.1" `
  WAZUH_REGISTRATION_SERVER="127.0.0.1"

NET START WazuhSvc
```

---

### ☀️ Daily Startup (3 commands)

```bash
# Terminal 1 — Wazuh
cd wazuh-docker/single-node && docker-compose up -d

# Terminal 2 — Backend
cd xsiem/siem-backend && py -m uvicorn main:app --reload --port 4000

# Terminal 3 — Frontend
cd xsiem/siem-dashboard && npm start
```

---

## 📧 Email Alert Setup

1. Enable **2-Step Verification** on your Gmail account
2. Go to **Google Account → Security → App Passwords**
3. Generate a password for "Mail / Windows"
4. Update `siem-backend/main.py`:

```python
EMAIL_SENDER   = "your_gmail@gmail.com"
EMAIL_PASSWORD = "your_16_char_app_password"
EMAIL_RECEIVER = "alerts@yourmail.com"
```

Test it:
```bash
curl -X POST http://localhost:4000/api/test-email
```

---

## ⚔️ Attack Simulation Lab

> All commands run from **Kali Linux VM** against your Windows machine.

```bash
TARGET="192.168.1.*"  # Your Windows IP

# 1. Port Scan — triggers network detection alerts
nmap -sS -A -p 1-1000 $TARGET

# 2. SSH Brute Force — triggers HIGH severity alerts
hydra -l Administrator \
  -P /usr/share/wordlists/rockyou.txt \
  ssh://$TARGET -t 4 -w 3

# 3. Rapid Failed Logins — triggers authentication spike
for i in {1..50}; do
  ssh -o ConnectTimeout=2 -o StrictHostKeyChecking=no \
    fakeuser@$TARGET 2>/dev/null
done

# 4. RDP Brute Force
hydra -l Administrator \
  -P /usr/share/wordlists/rockyou.txt \
  rdp://$TARGET -t 4

# 5. Web Scan (if web server running)
nikto -h http://$TARGET
```

Watch alerts appear live at `http://localhost:3000` 🔴

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|--------|---------|-------------|
| `GET` | `/health` | Backend + Wazuh connection status |
| `GET` | `/api/alerts` | Fetch alerts (params: limit, severity, search) |
| `GET` | `/api/stats` | Summary counts: total, high, medium, low |
| `GET` | `/api/agents` | All connected Wazuh agents |
| `POST` | `/api/test-email` | Send test email alert |

Full interactive docs: `http://localhost:4000/docs`

**Example — fetch high severity alerts:**
```bash
curl "http://localhost:4000/api/alerts?severity=high&limit=20"
```

---

## 📁 Project Structure

```
xsiem/
├── siem-dashboard/              # React Frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── Sidebar.jsx      # Navigation + system status
│   │   │   ├── Topbar.jsx       # Search + refresh + user
│   │   │   ├── SeverityBadge.jsx
│   │   │   ├── StatusBadge.jsx
│   │   │   └── AlertDetailPanel.jsx
│   │   ├── pages/
│   │   │   ├── DashboardPage.jsx   # Overview + charts
│   │   │   ├── AlertsPage.jsx      # Full alert table
│   │   │   ├── LogsPage.jsx        # Raw log stream
│   │   │   ├── AgentsPage.jsx      # Agent monitoring
│   │   │   └── InvestigationPage.jsx
│   │   ├── services/
│   │   │   └── api.js           # All backend API calls
│   │   └── data/
│   │       └── mockAlerts.js    # Fallback demo data
│   ├── tailwind.config.js
│   └── package.json
│
└── siem-backend/                # Python Backend
    └── main.py                  # FastAPI app + all routes
```

---

## 🖼️ Screenshots

### Dashboard Overview
> 812 real security events, severity charts, recent alerts table

### Alerts Page
> 500 alerts with severity filters, search, and detail panel

### Live Log Stream
> Raw Wazuh logs streaming in real-time

### Alert Detail Panel
> Full log, IPs, agent, rule description, Mark as Resolved

### Kali Attack + Dashboard
> SSH brute force running while dashboard updates live

### Email Alert
> Automated HTML email notification for high-severity threats

---

## 🎓 Skills Demonstrated

| Skill | Tool/Technology |
|-------|----------------|
| SIEM Deployment | Wazuh 4.9.2 + Docker |
| Log Analysis | Wazuh Manager + OpenSearch |
| Threat Detection | 3000+ Wazuh detection rules |
| Attack Simulation | Kali Linux, Hydra, nmap, Nikto |
| Backend Development | Python FastAPI |
| Frontend Development | React 18 + Recharts |
| API Integration | Wazuh REST API + OpenSearch API |
| Containerization | Docker Compose |
| Email Automation | Python smtplib + Gmail SMTP |
| Incident Response | Alert triage, investigation workflow |

---

## ⚠️ Disclaimer

This project is for **educational purposes only**. All attack simulations were performed exclusively on personally owned machines in a controlled home lab environment. Never perform security testing on systems you do not own or have explicit written permission to test.

---

## 👤 Author

**Shakir** — SOC Analyst  
📧 [muhdshakir5656@gmail.com]  
🔗 [LinkedIn](https://www.linkedin.com/in/muhammed-sakir-k/)
🐙 [GitHub](https://github.com/Muhammed-Sakir-k)

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

**⭐ Star this repo if it helped you build your cybersecurity portfolio!**

Built with 🛡️ by Shakir | Wazuh SIEM | 2026

</div>
