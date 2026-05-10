import React, { useState, useEffect } from "react";
import { Activity, ShieldAlert, Server, Wifi, TrendingUp, Clock } from "lucide-react";
import StatCard from "../components/StatCard";
import TrafficChart from "../components/TrafficChart";
import AlertRow from "../components/AlertRow";

import "./Dashboard.css";

export default function Dashboard() {
  const [dashboardStats, setDashboardStats] = useState({
    totalPackets: 0,
    inbound: 0,
    activeThreats: 0,
    blockedConnections: 0,
    systemHealth: "Healthy",
    uptime: "99.9%"
  });
  const [alerts, setAlerts] = useState([]);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const statsRes = await fetch("/api/dashboard/stats");
        const statsData = await statsRes.json();
        setDashboardStats({
          totalPackets: statsData.total_packets || 0,
          totalBytes: statsData.total_bytes || 0,
          activeThreats: statsData.active_threats || 0,
          blockedConnections: statsData.blocked_connections || 0,
          systemHealth: statsData.system_health || "Healthy",
          uptime: "99.9%"
        });

        const alertsRes = await fetch("/api/dashboard/alerts");
        const alertsData = await alertsRes.json();
        setAlerts(alertsData || []);
        
        const histRes = await fetch("/api/dashboard/history");
        const histData = await histRes.json();
        setHistory(histData || []);
      } catch (err) {
        console.error("Failed to fetch live data", err);
      }
    };

    fetchData(); // Initial fetch
    const interval = setInterval(fetchData, 3000); // Poll every 3 seconds for real-time effect
    return () => clearInterval(interval);
  }, []);

  const recentAlerts = alerts.filter((a) => a.status === "UNRESOLVED").slice(0, 5);

  const severityCounts = {
    critical: alerts.filter(a => a.severity === "CRITICAL" && a.status === "UNRESOLVED").length,
    high: alerts.filter(a => a.severity === "HIGH" && a.status === "UNRESOLVED").length,
    medium: alerts.filter(a => a.severity === "MEDIUM" && a.status === "UNRESOLVED").length,
    low: alerts.filter(a => a.severity === "LOW" && a.status === "UNRESOLVED").length,
  };

  const trafficTimeline = [...history]
    .sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp))
    .slice(-20)
    .map(log => {
      const d = new Date(log.timestamp);
      return {
        time: d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        inbound: log.status === "ALLOWED" ? log.bytes : 0,
        outbound: log.status === "ALLOWED" ? Math.floor(log.bytes * 0.4) : 0,
        blocked: log.status !== "ALLOWED" ? log.bytes : 0
      };
    });


  return (
    <div className="dashboard">
      <div className="dashboard__header">
        <div>
          <h1 className="dashboard__title">Dashboard</h1>
          <p className="dashboard__subtitle">Real-time network monitoring overview</p>
        </div>
        <div className="dashboard__status">
          <span className="dashboard__status-dot"></span>
          <span>System {dashboardStats.systemHealth}</span>
          <span className="dashboard__uptime">
            <Clock size={14} /> {dashboardStats.uptime}
          </span>
        </div>
      </div>

      {/* Stats Row */}
      <div className="dashboard__stats">
        <StatCard
          title="Total Packets"
          value={dashboardStats.totalPackets.toLocaleString()}
          icon={<Activity size={22} />}
          trend="Live count"
          trendUp
        />
        <StatCard
          title="Total Traffic"
          value={(dashboardStats.totalBytes / 1024).toFixed(1) + " KB"}
          icon={<Wifi size={22} />}
          trend="Real-time"
          trendUp
        />
        <StatCard
          title="Active Threats"
          value={dashboardStats.activeThreats}
          icon={<ShieldAlert size={22} />}
          alert={dashboardStats.activeThreats > 0}
          trend="Blocked IPs"
          trendUp={false}
        />
        <StatCard
          title="Blocked"
          value={dashboardStats.blockedConnections}
          icon={<Server size={22} />}
          trend="Manual/Auto"
          trendUp
        />
      </div>

      {/* Severity Summary */}
      <div className="dashboard__severity">
        <div className="severity-pill severity-pill--critical">
          <span className="severity-pill__count">{severityCounts.critical}</span>
          <span>Critical</span>
        </div>
        <div className="severity-pill severity-pill--high">
          <span className="severity-pill__count">{severityCounts.high}</span>
          <span>High</span>
        </div>
        <div className="severity-pill severity-pill--medium">
          <span className="severity-pill__count">{severityCounts.medium}</span>
          <span>Medium</span>
        </div>
        <div className="severity-pill severity-pill--low">
          <span className="severity-pill__count">{severityCounts.low}</span>
          <span>Low</span>
        </div>
      </div>

      {/* Chart */}
      <TrafficChart data={trafficTimeline} title="Traffic Over Last 24 Hours" />

      {/* Recent Alerts */}
      <div className="dashboard__section">
        <h2 className="dashboard__section-title">
          <ShieldAlert size={18} /> Recent Alerts
        </h2>
        <div className="dashboard__alerts-list">
          {recentAlerts.length === 0 ? (
            <p className="dashboard__empty">No active alerts — system is clean.</p>
          ) : (
            recentAlerts.map((a) => <AlertRow key={a.id} alert={a} />)
          )}
        </div>
      </div>
    </div>
  );
}
