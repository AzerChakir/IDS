import React, { useState, useEffect } from "react";
import { Search, Filter } from "lucide-react";
import AlertRow from "../components/AlertRow";
import "./Alerts.css";

export default function Alerts() {
  const [searchTerm, setSearchTerm] = useState("");
  const [severityFilter, setSeverityFilter] = useState("ALL");
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [alertList, setAlertList] = useState([]);

  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        const res = await fetch("/api/dashboard/alerts");
        const data = await res.json();
        setAlertList(data || []);
      } catch (err) {
        console.error("Failed to fetch live alerts", err);
      }
    };

    fetchAlerts();
    const interval = setInterval(fetchAlerts, 3000); // Poll every 3 seconds
    return () => clearInterval(interval);
  }, []);

  const handleAdmit = (alert) => {
    setAlertList((prev) =>
      prev.map((a) => (a.id === alert.id ? { ...a, status: "RESOLVED" } : a))
    );
  };

  const handleBlock = (alert) => {
    setAlertList((prev) =>
      prev.map((a) => (a.id === alert.id ? { ...a, status: "RESOLVED" } : a))
    );
  };

  const handlePause = (alert) => {
    setAlertList((prev) =>
      prev.map((a) => (a.id === alert.id ? { ...a, status: "RESOLVED" } : a))
    );
  };

  const filtered = alertList.filter((a) => {
    if (severityFilter !== "ALL" && a.severity !== severityFilter) return false;
    if (statusFilter !== "ALL" && a.status !== statusFilter) return false;
    if (searchTerm) {
      const s = searchTerm.toLowerCase();
      return (
        a.source_ip.includes(s) ||
        a.type.toLowerCase().includes(s) ||
        a.description.toLowerCase().includes(s)
      );
    }
    return true;
  });

  return (
    <div className="alerts-page">
      <div className="alerts-page__header">
        <div>
          <h1 className="alerts-page__title">Alerts</h1>
          <p className="alerts-page__subtitle">
            {filtered.length} alerts · {filtered.filter((a) => a.status === "UNRESOLVED").length} unresolved
          </p>
        </div>
      </div>

      {/* Filters */}
      <div className="alerts-page__filters">
        <div className="alerts-page__search">
          <Search size={16} />
          <input
            type="text"
            placeholder="Search by IP, type, or description..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        <div className="alerts-page__filter-group">
          <Filter size={14} />
          <select value={severityFilter} onChange={(e) => setSeverityFilter(e.target.value)}>
            <option value="ALL">All Severity</option>
            <option value="CRITICAL">Critical</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
          </select>
          <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
            <option value="ALL">All Status</option>
            <option value="UNRESOLVED">Unresolved</option>
            <option value="RESOLVED">Resolved</option>
          </select>
        </div>
      </div>

      {/* Alert list */}
      <div className="alerts-page__list">
        {filtered.length === 0 ? (
          <p className="alerts-page__empty">No alerts match your filters.</p>
        ) : (
          filtered.map((a) => (
            <AlertRow
              key={a.id}
              alert={a}
              onAdmit={handleAdmit}
              onBlock={handleBlock}
              onPause={handlePause}
            />
          ))
        )}
      </div>
    </div>
  );
}
