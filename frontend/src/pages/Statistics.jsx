import React from "react";
import {
  BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from "recharts";
import TrafficChart from "../components/TrafficChart";
import { trafficTimeline, protocolDistribution, topSourceIPs } from "../data/mockData";
import "./Statistics.css";

// Bar chart data: top source IPs
const barData = topSourceIPs.map((ip) => ({
  ip: ip.ip.replace("192.168.1.", "*."),
  requests: ip.requests,
  fill:
    ip.status === "blocked" ? "#ff4757" :
    ip.status === "suspicious" ? "#ff9f43" : "#00d4ff",
}));

const CustomBarTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload;
  return (
    <div className="stats-tooltip">
      <p style={{ fontWeight: 600 }}>{topSourceIPs.find((i) => d.ip === i.ip.replace("192.168.1.", "*."))?.ip || d.ip}</p>
      <p>{d.requests.toLocaleString()} requests</p>
    </div>
  );
};

export default function Statistics() {
  return (
    <div className="statistics-page">
      <div className="statistics-page__header">
        <h1 className="statistics-page__title">Statistics</h1>
        <p className="statistics-page__subtitle">Detailed traffic analytics and insights</p>
      </div>

      {/* Traffic Timeline */}
      <TrafficChart data={trafficTimeline} title="24-Hour Traffic Overview" />

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
