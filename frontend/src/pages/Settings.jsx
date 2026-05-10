import React, { useState, useEffect } from "react";
import { Shield, Ban, Trash2, CheckCircle } from "lucide-react";
import "./Settings.css";

export default function Settings() {
  const [blacklist, setBlacklist] = useState([]);
  const [whitelist, setWhitelist] = useState([]);

  useEffect(() => {
    fetchLists();
  }, []);

  const fetchLists = async () => {
    try {
      const bRes = await fetch("/api/blacklist");
      const bData = await bRes.json();
      setBlacklist(bData);

      const wRes = await fetch("/api/whitelist");
      const wData = await wRes.json();
      setWhitelist(wData);
    } catch (err) {
      console.error("Failed to fetch firewall lists", err);
    }
  };

  const handleRemove = async (type, ip) => {
    try {
      const res = await fetch(`/api/${type}/${ip}`, { method: "DELETE" });
      if (res.ok) {
        fetchLists();
      }
    } catch (err) {
      console.error(`Failed to remove ${ip} from ${type}`, err);
    }
  };

  return (
    <div className="settings-page">
      <div className="settings-page__header">
        <h1 className="settings-page__title">Firewall & Settings</h1>
        <p className="settings-page__subtitle">Manage blacklists, whitelists, and system configuration</p>
      </div>

      <div className="settings-page__firewall-row">
        <div className="settings-card settings-card--firewall">
          <h3 className="settings-card__title"><Ban size={18} /> IP Blacklist</h3>
          <div className="firewall-list">
            {blacklist.length === 0 ? <p className="firewall-empty">No IPs blocked.</p> :
              blacklist.map(item => (
                <div key={item.ip} className="firewall-item">
                  <span>{item.ip}</span>
                  <button onClick={() => handleRemove("blacklist", item.ip)}><Trash2 size={14} /></button>
                </div>
              ))
            }
          </div>
        </div>

        <div className="settings-card settings-card--firewall">
          <h3 className="settings-card__title"><Shield size={18} /> Trusted Whitelist</h3>
          <div className="firewall-list">
            {whitelist.length === 0 ? <p className="firewall-empty">No IPs whitelisted.</p> :
              whitelist.map(item => (
                <div key={item.ip} className="firewall-item">
                  <span>{item.ip}</span>
                  <button onClick={() => handleRemove("whitelist", item.ip)}><Trash2 size={14} /></button>
                </div>
              ))
            }
          </div>
        </div>
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
