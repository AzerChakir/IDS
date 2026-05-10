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
          onClick={() => onAdmit?.(alert)}
          title="Admit / Whitelist"
        >
          <ShieldCheck size={16} />
        </button>
        <button
          className="alert-row__btn alert-row__btn--block"
          onClick={() => onBlock?.(alert)}
          title="Block Traffic"
        >
          <Ban size={16} />
        </button>
        <button
          className="alert-row__btn alert-row__btn--pause"
          onClick={() => onPause?.(alert)}
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
