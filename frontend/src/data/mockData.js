// =============================================================================
// PCD IDS — Mock Data for Development
// =============================================================================

// Helper: generate a random IP
const randIP = (prefix = "192.168.1") =>
  `${prefix}.${Math.floor(Math.random() * 253) + 1}`;

const randDestIP = () =>
  `10.0.${Math.floor(Math.random() * 10)}.${Math.floor(Math.random() * 253) + 1}`;

// Severity levels
export const SEVERITIES = ["CRITICAL", "HIGH", "MEDIUM", "LOW"];

// Protocols
const PROTOCOLS = ["TCP", "UDP", "ICMP", "HTTP", "HTTPS", "DNS", "SSH"];

// Attack types
const ATTACK_TYPES = [
  "DDoS Attempt",
  "Port Scan",
  "Malware C2",
  "Brute Force SSH",
  "SQL Injection",
  "XSS Detected",
  "DNS Tunneling",
  "Data Exfiltration",
];

// ─── Traffic History Logs ────────────────────────────────────────────────────

function generateTrafficLogs(count = 80) {
  const logs = [];
  const now = Date.now();
  for (let i = 0; i < count; i++) {
    const isBlocked = Math.random() < 0.18;
    logs.push({
      id: `log-${i}`,
      timestamp: new Date(now - i * 60000 * 3).toISOString(),
      source_ip: randIP(),
      dest_ip: randDestIP(),
      protocol: PROTOCOLS[Math.floor(Math.random() * PROTOCOLS.length)],
      bytes: Math.floor(Math.random() * 30000) + 64,
      status: isBlocked ? "BLOCKED" : "ALLOWED",
      port: Math.floor(Math.random() * 65535),
    });
  }
  return logs;
}

// ─── Alerts ─────────────────────────────────────────────────────────────────

function generateAlerts(count = 24) {
  const alerts = [];
  const now = Date.now();
  for (let i = 1; i <= count; i++) {
    alerts.push({
      id: i,
      timestamp: new Date(now - i * 60000 * 8).toISOString(),
      severity: SEVERITIES[Math.floor(Math.random() * SEVERITIES.length)],
      source_ip: randIP(),
      dest_ip: randDestIP(),
      type: ATTACK_TYPES[Math.floor(Math.random() * ATTACK_TYPES.length)],
      description: `Detected suspicious activity pattern matching known threat signature TLP-${Math.floor(Math.random() * 9999)}`,
      status: Math.random() < 0.6 ? "UNRESOLVED" : "RESOLVED",
      protocol: PROTOCOLS[Math.floor(Math.random() * PROTOCOLS.length)],
    });
  }
  return alerts;
}

// ─── Traffic Over Time (chart data) ─────────────────────────────────────────

function generateTrafficTimeline(hours = 24) {
  const data = [];
  const now = Date.now();
  for (let i = hours - 1; i >= 0; i--) {
    const h = new Date(now - i * 3600000);
    data.push({
      time: h.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      inbound: Math.floor(Math.random() * 800) + 200,
      outbound: Math.floor(Math.random() * 600) + 100,
      blocked: Math.floor(Math.random() * 100),
    });
  }
  return data;
}

// ─── Protocol Distribution (pie chart) ──────────────────────────────────────

export const protocolDistribution = [
  { name: "TCP", value: 4200, color: "#00d4ff" },
  { name: "UDP", value: 1800, color: "#7b61ff" },
  { name: "HTTP", value: 3100, color: "#00e68a" },
  { name: "HTTPS", value: 5600, color: "#3b82f6" },
  { name: "DNS", value: 1200, color: "#f59e0b" },
  { name: "ICMP", value: 400, color: "#ef4444" },
  { name: "SSH", value: 700, color: "#ec4899" },
];

// ─── Top Source IPs ─────────────────────────────────────────────────────────

export const topSourceIPs = [
  { ip: "192.168.1.105", requests: 1842, status: "suspicious" },
  { ip: "192.168.1.42", requests: 1456, status: "normal" },
  { ip: "192.168.1.217", requests: 1233, status: "blocked" },
  { ip: "192.168.1.89", requests: 987, status: "normal" },
  { ip: "192.168.1.163", requests: 854, status: "suspicious" },
  { ip: "10.0.2.55", requests: 743, status: "normal" },
  { ip: "192.168.1.201", requests: 651, status: "blocked" },
  { ip: "10.0.5.12", requests: 512, status: "normal" },
];

// ─── Dashboard Stats ────────────────────────────────────────────────────────

export const dashboardStats = {
  totalPackets: 128457,
  inbound: 72341,
  outbound: 56116,
  bandwidth: "2.4 GB",
  activeThreats: 7,
  blockedConnections: 342,
  systemHealth: "Operational",
  uptime: "14d 7h 32m",
};

// ─── Severity Counts ────────────────────────────────────────────────────────

export const severityCounts = {
  critical: 3,
  high: 4,
  medium: 12,
  low: 8,
};

// ─── Export generated data ──────────────────────────────────────────────────

export const trafficLogs = generateTrafficLogs();
export const alerts = generateAlerts();
export const trafficTimeline = generateTrafficTimeline();
