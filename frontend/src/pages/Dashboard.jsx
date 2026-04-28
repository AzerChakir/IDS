import React from "react";
import { Activity, ShieldAlert, Server, Wifi, TrendingUp, Clock } from "lucide-react";
import StatCard from "../components/StatCard";
import TrafficChart from "../components/TrafficChart";
import AlertRow from "../components/AlertRow";
import { dashboardStats, severityCounts, trafficTimeline, alerts } from "../data/mockData";
import "./Dashboard.css";

export default function Dashboard() {
  const recentAlerts = alerts.filter((a) => a.status === "UNRESOLVED").slice(0, 5);

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
          trend="+12.5%"
          trendUp
        />
        <StatCard
          title="Inbound"
          value={dashboardStats.inbound.toLocaleString()}
          icon={<Wifi size={22} />}
          trend="+8.2%"
          trendUp
        />
        <StatCard
          title="Active Threats"
          value={dashboardStats.activeThreats}
          icon={<ShieldAlert size={22} />}
          alert={dashboardStats.activeThreats > 0}
          trend="-2 from yesterday"
          trendUp={false}
        />
        <StatCard
          title="Blocked"
          value={dashboardStats.blockedConnections}
          icon={<Server size={22} />}
          trend="+34"
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
