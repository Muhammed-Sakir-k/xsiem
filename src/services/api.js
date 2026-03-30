const BASE = "http://localhost:4000/api";

async function request(path, params = {}, options = {}) {
  const query = new URLSearchParams(params).toString();
  const url = query ? `${BASE}${path}?${query}` : `${BASE}${path}`;
  const res = await fetch(url, options);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export const api = {
  getAlerts: (params) => request("/alerts", params),
  getStats:  ()       => request("/stats"),
  getAgents: ()       => request("/agents"),
  testEmail: ()       => request("/test-email", {}, { method: "POST" }),
  health:    ()       => fetch("http://localhost:4000/health").then((r) => r.json()),
};