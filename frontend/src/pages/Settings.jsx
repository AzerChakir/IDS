import React from "react";
import "./Settings.css";

export default function Settings() {
  return (
    <div className="settings-page">
      <div className="settings-page__header">
        <h1 className="settings-page__title">Settings</h1>
        <p className="settings-page__subtitle">System configuration and preferences</p>
      </div>

      <div className="settings-page__grid">
        <div className="settings-card">
          <h3 className="settings-card__title">General</h3>
          <div className="settings-card__item">
            <div>
              <span className="settings-card__label">System Name</span>
              <span className="settings-card__value">PCD IDS v0.2.0</span>
            </div>
          </div>
          <div className="settings-card__item">
            <div>
              <span className="settings-card__label">Auto-refresh Interval</span>
              <span className="settings-card__value">5 seconds</span>
            </div>
          </div>
          <div className="settings-card__item">
            <div>
              <span className="settings-card__label">Theme</span>
              <span className="settings-card__value">Dark (Cybersecurity)</span>
            </div>
          </div>
        </div>

        <div className="settings-card">
          <h3 className="settings-card__title">Security</h3>
          <div className="settings-card__item">
            <div>
              <span className="settings-card__label">Session Timeout</span>
              <span className="settings-card__value">30 minutes</span>
            </div>
          </div>
          <div className="settings-card__item">
            <div>
              <span className="settings-card__label">Two-Factor Auth</span>
              <span className="settings-card__value">Disabled</span>
            </div>
          </div>
          <div className="settings-card__item">
            <div>
              <span className="settings-card__label">API Key</span>
              <span className="settings-card__value" style={{ fontFamily: "monospace", fontSize: "0.75rem" }}>
                ••••••••••••••••
              </span>
            </div>
          </div>
        </div>

        <div className="settings-card">
          <h3 className="settings-card__title">Notifications</h3>
          <div className="settings-card__item">
            <div>
              <span className="settings-card__label">Email Alerts</span>
              <span className="settings-card__value">Enabled</span>
            </div>
          </div>
          <div className="settings-card__item">
            <div>
              <span className="settings-card__label">Critical Alert Sound</span>
              <span className="settings-card__value">Enabled</span>
            </div>
          </div>
        </div>

        <div className="settings-card">
          <h3 className="settings-card__title">About</h3>
          <div className="settings-card__item">
            <div>
              <span className="settings-card__label">Backend</span>
              <span className="settings-card__value">FastAPI v0.135</span>
            </div>
          </div>
          <div className="settings-card__item">
            <div>
              <span className="settings-card__label">ML Model</span>
              <span className="settings-card__value">Random Forest (scikit-learn)</span>
            </div>
          </div>
          <div className="settings-card__item">
            <div>
              <span className="settings-card__label">License</span>
              <span className="settings-card__value">Academic Use</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
