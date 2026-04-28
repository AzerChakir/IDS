import React from "react";
import "./StatCard.css";

export default function StatCard({ title, value, icon, trend, trendUp, alert }) {
  return (
    <div className={`stat-card ${alert ? "stat-card--alert" : ""}`}>
      <div className={`stat-card__icon ${alert ? "stat-card__icon--alert" : ""}`}>
        {icon}
      </div>
      <div className="stat-card__content">
        <span className="stat-card__title">{title}</span>
        <span className={`stat-card__value ${alert ? "stat-card__value--alert" : ""}`}>
          {value}
        </span>
        {trend !== undefined && (
          <span className={`stat-card__trend ${trendUp ? "stat-card__trend--up" : "stat-card__trend--down"}`}>
            {trendUp ? "▲" : "▼"} {trend}
          </span>
        )}
      </div>
    </div>
  );
}
