from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import httpx, asyncio, smtplib, os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

app = FastAPI(title="SIEM Dashboard API v2")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Wazuh Config ──────────────────────────────────────────────
WAZUH_HOST = "https://localhost:55000"
WAZUH_USER = os.getenv("WAZUH_USER")
WAZUH_PASS = os.getenv("WAZUH_PASS")
CLIENT_KWARGS = {"verify": False, "timeout": 30.0}

# ── Email Config — UPDATE THESE ───────────────────────────────
EMAIL_SENDER   = "your_gmail@gmail.com"       # ← your Gmail
EMAIL_PASSWORD = "your_16_char_app_password"          # ← Gmail App Password
EMAIL_RECEIVER = "alerts@yourmail.com"   # ← who gets alerts
SMTP_HOST      = "smtp.gmail.com"
SMTP_PORT      = 587

# ── Token Cache ───────────────────────────────────────────────
_token_cache = {"token": None}

# ── Email Alert Tracking (avoid duplicate emails) ─────────────
_alerted_ids = set()

async def get_token():
    if _token_cache["token"]:
        return _token_cache["token"]
    async with httpx.AsyncClient(**CLIENT_KWARGS) as client:
        r = await client.post(
            f"{WAZUH_HOST}/security/user/authenticate",
            auth=(WAZUH_USER, WAZUH_PASS),
        )
        if r.status_code != 200:
            raise HTTPException(status_code=401, detail=f"Auth failed: {r.text}")
        token = r.json()["data"]["token"]
        _token_cache["token"] = token
        asyncio.get_event_loop().call_later(
            840, lambda: _token_cache.update({"token": None})
        )
        return token

# ── Email Alert Function ──────────────────────────────────────
def send_email_alert(alert: dict):
    """Send email for high severity alerts."""
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"🚨 SIEM HIGH SEVERITY ALERT: {alert['rule']}"
        msg["From"]    = EMAIL_SENDER
        msg["To"]      = EMAIL_RECEIVER

        html = f"""
        <html>
        <body style="font-family: monospace; background: #070b12; color: #e2e8f0; padding: 24px;">
            <div style="max-width: 600px; margin: 0 auto;">
                <div style="background: #ff3b5c; color: white; padding: 12px 20px; border-radius: 8px 8px 0 0;">
                    <h2 style="margin:0;">🚨 HIGH SEVERITY ALERT DETECTED</h2>
                </div>
                <div style="background: #0d1320; border: 1px solid #1e2d45; padding: 24px; border-radius: 0 0 8px 8px;">
                    <table style="width:100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 8px 0; color: #4a6080; width: 140px;">Rule</td>
                            <td style="padding: 8px 0; color: #ff3b5c; font-weight: bold;">{alert['rule']}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; color: #4a6080;">Severity</td>
                            <td style="padding: 8px 0; color: #ff3b5c; font-weight: bold;">HIGH</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; color: #4a6080;">Source IP</td>
                            <td style="padding: 8px 0; color: #00d4ff;">{alert['src_ip']}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; color: #4a6080;">Agent</td>
                            <td style="padding: 8px 0; color: #e2e8f0;">{alert['agent']}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; color: #4a6080;">Time</td>
                            <td style="padding: 8px 0; color: #e2e8f0;">{alert['timestamp']}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; color: #4a6080;">Description</td>
                            <td style="padding: 8px 0; color: #e2e8f0;">{alert['desc']}</td>
                        </tr>
                    </table>
                    <div style="margin-top: 20px; padding: 12px; background: #111827; border-radius: 6px; border-left: 3px solid #ff3b5c;">
                        <pre style="color: #7dd3fc; font-size: 11px; margin: 0; white-space: pre-wrap;">{str(alert.get('log', ''))[:500]}</pre>
                    </div>
                    <p style="margin-top: 20px; color: #4a6080; font-size: 12px;">
                        This is an automated alert from your SIEM Dashboard.<br>
                        Investigate immediately at your SOC dashboard.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """

        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())

        print(f"[EMAIL] Alert sent for: {alert['rule']}")

    except Exception as e:
        print(f"[EMAIL ERROR] {e}")


def check_and_alert(alerts: list, background_tasks: BackgroundTasks):
    """Check for high severity alerts and send emails."""
    for alert in alerts:
        alert_id = alert.get("id", "")
        if alert.get("severity") == "high" and alert_id not in _alerted_ids:
            _alerted_ids.add(alert_id)
            background_tasks.add_task(send_email_alert, alert)


# ── Helpers ───────────────────────────────────────────────────
def map_severity(level: int) -> str:
    if level >= 12: return "high"
    if level >= 7:  return "medium"
    return "low"

def format_syscheck(a: dict) -> dict:
    agent_info = a.get("agent", {})
    agent_name = agent_info.get("name", "unknown") if isinstance(agent_info, dict) else "unknown"
    agent_ip   = agent_info.get("ip",   "unknown") if isinstance(agent_info, dict) else "unknown"

    event_type = a.get("type", a.get("result", ""))
    if event_type in ["deleted", "failed"]:
        severity = "high"
    elif event_type in ["modified", "unknown"]:
        severity = "medium"
    else:
        severity = "low"

    file_path = a.get("file", a.get("name", "Unknown"))
    rule = f"File integrity change: {file_path}" if a.get("file") else f"SCA Check: {file_path}"

    return {
        "id":        str(a.get("date", "") or a.get("id", "")),
        "timestamp": a.get("date", a.get("start_scan", "")),
        "rule":      rule,
        "severity":  severity,
        "src_ip":    agent_ip,
        "dst_ip":    "-",
        "agent":     agent_name,
        "status":    "open" if event_type != "passed" else "closed",
        "desc":      a.get("description", rule),
        "log":       str(a)[:500],
        "rule_id":   str(a.get("id", "")),
        "groups":    [],
        "level":     12 if severity == "high" else 7 if severity == "medium" else 3,
    }
def format_opensearch_alert(hit: dict) -> dict:
    """Format raw OpenSearch alert to frontend format."""
    src = hit.get("_source", {})
    rule  = src.get("rule",  {})
    agent = src.get("agent", {})
    data  = src.get("data",  {})

    level = rule.get("level", 0)
    if level >= 12:   severity = "high"
    elif level >= 7:  severity = "medium"
    else:             severity = "low"

    return {
        "id":        hit.get("_id", ""),
        "timestamp": src.get("timestamp", ""),
        "rule":      rule.get("description", "Unknown rule"),
        "severity":  severity,
        "src_ip":    data.get("srcip") or agent.get("ip", "unknown"),
        "dst_ip":    data.get("dstip", "-"),
        "agent":     agent.get("name", "unknown"),
        "status":    "open",
        "desc":      rule.get("description", ""),
        "log":       src.get("full_log", "")[:500],
        "rule_id":   str(rule.get("id", "")),
        "groups":    rule.get("groups", []),
        "level":     level,
    }

def format_agent(a: dict) -> dict:
    return {
        "id":       a.get("id", ""),
        "name":     a.get("name", "unknown"),
        "ip":       a.get("ip", "unknown"),
        "status":   a.get("status", "unknown"),
        "os":       a.get("os", {}).get("name", "unknown"),
        "version":  a.get("version", "unknown"),
        "lastSeen": a.get("lastKeepAlive", ""),
    }

# ── Routes ────────────────────────────────────────────────────

@app.get("/health")
async def health():
    try:
        await get_token()
        return {
            "backend":       "ok",
            "wazuh":         "ok",
            "authenticated": True,
            "email":         EMAIL_SENDER != "your_gmail@gmail.com",
            "timestamp":     datetime.now().isoformat(),
        }
    except Exception as e:
        return {"backend": "ok", "wazuh": "error", "detail": str(e)}


@app.get("/api/alerts")
async def get_alerts(
    background_tasks: BackgroundTasks,
    limit: int = Query(500, le=1000),
    severity: str = Query(None),
    search: str = Query(None),
):
    # Query OpenSearch indexer directly (has ALL alerts)
    async with httpx.AsyncClient(**CLIENT_KWARGS) as client:
        r = await client.post(
            "https://localhost:9200/wazuh-alerts-*/_search",
            auth=("admin", "SecretPassword"),
            json={
                "size": limit,
                "sort": [{"timestamp": {"order": "desc"}}],
                "query": {"match_all": {}},
            },
        )

    if r.status_code != 200:
        raise HTTPException(status_code=r.status_code, detail=r.text)

    hits = r.json().get("hits", {}).get("hits", [])
    alerts = [format_opensearch_alert(h) for h in hits]

    # Send email for high severity
    check_and_alert(alerts, background_tasks)

    # Apply filters
    if severity and severity != "all":
        alerts = [a for a in alerts if a["severity"] == severity]
    if search:
        s = search.lower()
        alerts = [
            a for a in alerts
            if s in a["src_ip"].lower()
            or s in a["rule"].lower()
            or s in a["agent"].lower()
        ]

    return {"success": True, "total": len(alerts), "data": alerts}


@app.get("/api/stats")
async def get_stats():
    async with httpx.AsyncClient(**CLIENT_KWARGS) as client:
        r = await client.post(
            "https://localhost:9200/wazuh-alerts-*/_search",
            auth=("admin", "SecretPassword"),
            json={
                "size": 0,
                "aggs": {
                    "high":   {"filter": {"range": {"rule.level": {"gte": 12}}}},
                    "medium": {"filter": {"range": {"rule.level": {"gte": 7, "lt": 12}}}},
                    "low":    {"filter": {"range": {"rule.level": {"lt": 7}}}},
                },
            },
        )

    data = r.json()
    total = data.get("hits", {}).get("total", {}).get("value", 0)
    aggs  = data.get("aggregations", {})

    return {
        "success": True,
        "total":   total,
        "high":    aggs.get("high",   {}).get("doc_count", 0),
        "medium":  aggs.get("medium", {}).get("doc_count", 0),
        "low":     aggs.get("low",    {}).get("doc_count", 0),
    }

@app.get("/api/agents")
async def get_agents():
    token = await get_token()
    async with httpx.AsyncClient(**CLIENT_KWARGS) as client:
        r = await client.get(
            f"{WAZUH_HOST}/agents",
            headers={"Authorization": f"Bearer {token}"},
            params={"limit": 500},
        )
    if r.status_code != 200:
        raise HTTPException(status_code=r.status_code, detail=r.text)
    items = r.json().get("data", {}).get("affected_items", [])
    return {
        "success": True,
        "total":   len(items),
        "data":    [format_agent(a) for a in items],
    }


@app.post("/api/test-email")
async def test_email(background_tasks: BackgroundTasks):
    """Send a test email to verify email config is working."""
    test_alert = {
        "id":        "test-001",
        "rule":      "TEST — Email Alert System Working",
        "severity":  "high",
        "src_ip":    "192.168.1.176",
        "agent":     "test-agent",
        "timestamp": datetime.now().isoformat(),
        "desc":      "This is a test alert to confirm your email notifications are working correctly.",
        "log":       "Test log entry from SIEM Dashboard",
    }
    background_tasks.add_task(send_email_alert, test_alert)
    return {"success": True, "message": f"Test email sent to {EMAIL_RECEIVER}"}
