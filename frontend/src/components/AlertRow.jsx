import React, { useState } from "react";
import { ShieldCheck, Ban, PauseCircle, Brain, Loader2 } from "lucide-react";
import "./AlertRow.css";

const severityClass = {
  CRITICAL: "alert-row__badge--critical",
  HIGH: "alert-row__badge--high",
  MEDIUM: "alert-row__badge--medium",
  LOW: "alert-row__badge--low",
};

export default function AlertRow({ alert, onAdmit, onBlock, onPause }) {
  const [analyzing, setAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState(null);

  const handleAnalyze = async () => {
    if (analysis) {
      setAnalysis(null);
      return;
    }
    setAnalyzing(true);
    try {
      const res = await fetch(`/api/alert/${alert.id}/analyze`);
      const data = await res.json();
      if (!res.ok) {
        setAnalysis(data.detail || "Alert not found in database");
      } else {
        // analysis is an object with llm_analysis field
        const analysisData = data.analysis;
        if (analysisData && analysisData.llm_analysis) {
          setAnalysis(analysisData.llm_analysis);
        } else if (analysisData && analysisData.retrieved_context) {
          setAnalysis(analysisData.retrieved_context);
        } else {
          setAnalysis("No analysis available");
        }
      }
    } catch (err) {
      setAnalysis("Failed to analyze: " + err.message);
    }
    setAnalyzing(false);
  };

  const handleAdmitAction = async () => {
    try {
      const res = await fetch("/api/whitelist", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ip: alert.source_ip })
      });
      if (res.ok) {
        onAdmit?.(alert);
      }
    } catch (err) {
      console.error("Failed to whitelist IP", err);
    }
  };

  const handlePauseAction = async () => {
    if (!window.confirm(`Are you sure you want to ISOLATE destination server ${alert.dest_ip || "Target Server"}? This will block all incoming traffic to this server.`)) return;
    try {
      const res = await fetch("/api/isolate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ip: alert.dest_ip || "10.0.0.50" })
      });
      if (res.ok) {
        onPause?.(alert);
      }
    } catch (err) {
      console.error("Failed to isolate destination", err);
    }
  };

  const handleBlockAction = async () => {
    if (!window.confirm(`Are you sure you want to PERMANENTLY blacklist IP ${alert.source_ip}?`)) return;
    try {
      const res = await fetch("/api/blacklist", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ip: alert.source_ip })
      });
      if (res.ok) {
        onBlock?.(alert);
      }
    } catch (err) {
      console.error("Failed to blacklist IP", err);
    }
  };
  return (
    <div className={`alert-row ${alert.status === "RESOLVED" ? "alert-row--resolved" : ""}`}>
      <div className="alert-row__left">
        <span className={`alert-row__badge ${severityClass[alert.severity] || ""}`}>
          {alert.severity}
        </span>
        <div className="alert-row__info">
          <span className="alert-row__type">{alert.type}</span>
          <span className="alert-row__meta">
            {alert.source_ip} → {alert.dest_ip} · {alert.protocol}
          </span>
        </div>
      </div>
      <div className="alert-row__center">
        <span className="alert-row__desc">{alert.description}</span>
      </div>
      <div className="alert-row__time">
        {new Date(alert.timestamp).toLocaleString([], {
          month: "short",
          day: "numeric",
          hour: "2-digit",
          minute: "2-digit",
        })}
      </div>
      <div className="alert-row__actions">
        <button
          className="alert-row__btn alert-row__btn--analyze"
          onClick={handleAnalyze}
          disabled={analyzing}
          title="AI Analysis & Remediation"
        >
          {analyzing ? <Loader2 size={16} className="spinning" /> : <Brain size={16} />}
        </button>
        <button
          className="alert-row__btn alert-row__btn--admit"
          onClick={handleAdmitAction}
          title="Admit / Whitelist"
        >
          <ShieldCheck size={16} />
        </button>
        <button
          className="alert-row__btn alert-row__btn--block"
          onClick={handleBlockAction}
          title="Block Traffic"
        >
          <Ban size={16} />
        </button>
        <button
          className="alert-row__btn alert-row__btn--pause"
          onClick={handlePauseAction}
          title="Stop Site Temporarily"
        >
          <PauseCircle size={16} />
        </button>
      </div>
      {analysis && (
        <div className="alert-row__analysis">
          <strong>AI Recommendation:</strong> {analysis}
        </div>
      )}
    </div>
  );
}
