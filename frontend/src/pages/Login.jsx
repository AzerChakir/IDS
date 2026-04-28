import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Shield, Eye, EyeOff, AlertCircle } from "lucide-react";
import "./Login.css";

export default function Login() {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const response = await fetch("http://localhost:8000/api/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, password }),
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem(
          "pcd_ids_auth",
          JSON.stringify({ 
            user: username, 
            role: data.role || "administrator", 
            token: data.token,
            loggedInAt: new Date().toISOString() 
          })
        );
        navigate("/dashboard");
      } else {
        const errorData = await response.json();
        setError(errorData.detail || "Invalid credentials.");
      }
    } catch (err) {
      setError("Failed to connect to the server. Is the backend running?");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      {/* Animated background grid */}
      <div className="login-page__bg">
        <div className="login-page__grid"></div>
        <div className="login-page__glow login-page__glow--1"></div>
        <div className="login-page__glow login-page__glow--2"></div>
      </div>

      <div className="login-card">
        {/* Logo */}
        <div className="login-card__logo">
          <div className="login-card__logo-icon">
            <Shield size={32} strokeWidth={2.5} />
          </div>
          <h1 className="login-card__title">PCD IDS</h1>
          <p className="login-card__subtitle">Intrusion Detection System</p>
        </div>

        {/* Form */}
        <form className="login-card__form" onSubmit={handleSubmit}>
          <div className="login-card__field">
            <label htmlFor="username">Username</label>
            <input
              id="username"
              type="text"
              placeholder="Enter your username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              autoComplete="username"
              required
            />
          </div>

          <div className="login-card__field">
            <label htmlFor="password">Password</label>
            <div className="login-card__password-wrap">
              <input
                id="password"
                type={showPassword ? "text" : "password"}
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete="current-password"
                required
              />
              <button
                type="button"
                className="login-card__eye"
                onClick={() => setShowPassword(!showPassword)}
                tabIndex={-1}
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
          </div>

          {error && (
            <div className="login-card__error">
              <AlertCircle size={16} />
              <span>{error}</span>
            </div>
          )}

          <button
            type="submit"
            className={`login-card__submit ${loading ? "login-card__submit--loading" : ""}`}
            disabled={loading}
          >
            {loading ? (
              <span className="login-card__spinner"></span>
            ) : (
              "Sign In"
            )}
          </button>
        </form>

        <p className="login-card__footer">
          Network Administrator Access Only
        </p>
      </div>
    </div>
  );
}
