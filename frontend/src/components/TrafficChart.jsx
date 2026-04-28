import React from "react";
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from "recharts";
import "./TrafficChart.css";

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload) return null;
  return (
    <div className="traffic-chart__tooltip">
      <p className="traffic-chart__tooltip-label">{label}</p>
      {payload.map((p, i) => (
        <p key={i} style={{ color: p.color }} className="traffic-chart__tooltip-value">
          {p.name}: {p.value}
        </p>
      ))}
    </div>
  );
};

export default function TrafficChart({ data, title = "Network Traffic" }) {
  return (
    <div className="traffic-chart">
      <h3 className="traffic-chart__title">{title}</h3>
      <div className="traffic-chart__container">
        <ResponsiveContainer width="100%" height={280}>
          <AreaChart data={data} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
            <defs>
              <linearGradient id="gradIn" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#00d4ff" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#00d4ff" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="gradOut" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#7b61ff" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#7b61ff" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="gradBlocked" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#ff4757" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#ff4757" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
            <XAxis dataKey="time" tick={{ fill: "rgba(255,255,255,0.3)", fontSize: 11 }} axisLine={false} tickLine={false} />
            <YAxis tick={{ fill: "rgba(255,255,255,0.3)", fontSize: 11 }} axisLine={false} tickLine={false} />
            <Tooltip content={<CustomTooltip />} />
            <Legend wrapperStyle={{ color: "rgba(255,255,255,0.5)", fontSize: 12 }} />
            <Area type="monotone" dataKey="inbound" stroke="#00d4ff" fill="url(#gradIn)" strokeWidth={2} name="Inbound" />
            <Area type="monotone" dataKey="outbound" stroke="#7b61ff" fill="url(#gradOut)" strokeWidth={2} name="Outbound" />
            <Area type="monotone" dataKey="blocked" stroke="#ff4757" fill="url(#gradBlocked)" strokeWidth={2} name="Blocked" />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
