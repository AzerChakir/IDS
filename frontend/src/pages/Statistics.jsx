import React, { useState, useEffect } from "react";
import {
  BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from "recharts";
import TrafficChart from "../components/TrafficChart";
import "./Statistics.css";

const CustomBarTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload;
  return (
    <div className="stats-tooltip">
      <p style={{ fontWeight: 600 }}>{d.originalIp || d.ip}</p>
      <p>{d.requests.toLocaleString()} requests</p>
    </div>
  );
};

export default function Statistics() {
  const [history, setHistory] = useState([]);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const res = await fetch("/api/dashboard/history");
        const data = await res.json();
        setHistory(data || []);
      } catch (err) {
        console.error("Failed to fetch live history", err);
      }
    };
    fetchHistory();
    const interval = setInterval(fetchHistory, 3000);
    return () => clearInterval(interval);
  }, []);

  // 1. Traffic Timeline
  const trafficTimeline = [...history]
    .sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp))
    .slice(-24)
    .map(log => {
      const d = new Date(log.timestamp);
      return {
        time: d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        inbound: log.status === "ALLOWED" ? log.bytes : 0,
        outbound: log.status === "ALLOWED" ? Math.floor(log.bytes * 0.4) : 0,
        blocked: log.status !== "ALLOWED" ? log.bytes : 0
      };
    });

  // 2. Protocol Distribution
  const protocolCounts = history.reduce((acc, log) => {
    acc[log.protocol] = (acc[log.protocol] || 0) + 1;
    return acc;
  }, {});
  const colors = { TCP: "#00d4ff", UDP: "#7b61ff", HTTP: "#00e68a", HTTPS: "#3b82f6", ICMP: "#ef4444" };
  const protocolDistribution = Object.keys(protocolCounts).map(proto => ({
    name: proto,
    value: protocolCounts[proto],
    color: colors[proto] || "#f59e0b"
  }));

  // 3. Top Source IPs
  const ipCounts = history.reduce((acc, log) => {
    if (!acc[log.source_ip]) acc[log.source_ip] = { requests: 0, blocks: 0 };
    acc[log.source_ip].requests++;
    if (log.status === "BLOCKED") acc[log.source_ip].blocks++;
    return acc;
  }, {});
  
  const topSourceIPs = Object.keys(ipCounts)
    .map(ip => ({
      ip,
      requests: ipCounts[ip].requests,
      status: ipCounts[ip].blocks > 0 ? "blocked" : "normal"
    }))
    .sort((a, b) => b.requests - a.requests)
    .slice(0, 8);

  const barData = topSourceIPs.map((ip) => ({
    ip: ip.ip.replace("192.168.1.", "*."),
    originalIp: ip.ip,
    requests: ip.requests,
    fill: ip.status === "blocked" ? "#ff4757" : "#00d4ff",
  }));

  return (
    <div className="statistics-page">
      <div className="statistics-page__header">
        <h1 className="statistics-page__title">Statistics</h1>
        <p className="statistics-page__subtitle">Detailed traffic analytics and insights</p>
      </div>

      {/* Traffic Timeline */}
      <TrafficChart data={trafficTimeline} title="Recent Traffic Activity" />

      <div className="statistics-page__grid">
        {/* Protocol Distribution */}
        <div className="stats-card">
          <h3 className="stats-card__title">Protocol Distribution</h3>
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie
                data={protocolDistribution}
                cx="50%" cy="50%"
                innerRadius={70} outerRadius={110}
                paddingAngle={3}
                dataKey="value"
                stroke="none"
              >
                {protocolDistribution.map((entry, i) => (
                  <Cell key={i} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  background: "rgba(10,14,26,0.95)",
                  border: "1px solid rgba(255,255,255,0.1)",
                  borderRadius: 8,
                  color: "#fff",
                  fontSize: "0.8rem",
                }}
              />
              <Legend
                wrapperStyle={{ fontSize: "0.75rem", color: "rgba(255,255,255,0.5)" }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Top Source IPs */}
        <div className="stats-card">
          <h3 className="stats-card__title">Top Source IPs</h3>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={barData} layout="vertical" margin={{ left: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" horizontal={false} />
              <XAxis type="number" tick={{ fill: "rgba(255,255,255,0.3)", fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis dataKey="ip" type="category" tick={{ fill: "rgba(255,255,255,0.5)", fontSize: 11 }} axisLine={false} tickLine={false} width={55} />
              <Tooltip content={<CustomBarTooltip />} />
              <Bar dataKey="requests" radius={[0, 6, 6, 0]} barSize={18}>
                {barData.map((entry, i) => (
                  <Cell key={i} fill={entry.fill} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* IP Table */}
      <div className="stats-card">
        <h3 className="stats-card__title">Top Source IP Details</h3>
        <table className="stats-table">
          <thead>
            <tr>
              <th>IP Address</th>
              <th>Requests</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {topSourceIPs.map((ip, i) => (
              <tr key={i}>
                <td className="stats-table__ip">{ip.ip}</td>
                <td>{ip.requests.toLocaleString()}</td>
                <td>
                  <span className={`stats-table__status stats-table__status--${ip.status}`}>
                    {ip.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
