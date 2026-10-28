import React, { useState } from "react";
import { login } from "../services/authService.js";

/**
 * HQLogin.jsx — Login gate for the NCPOR HQ Dashboard.
 * Visual redesign to match command center aesthetic.
 */
export default function HQLogin({ onLogin }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!username.trim() || !password.trim()) return;

    setLoading(true);
    setError("");

    const result = await login(username.trim(), password);

    if (result.success) {
      onLogin(result.session);
    } else {
      setError(result.error || "Authentication failed");
    }
    setLoading(false);
  };

  return (
    <div className="hq-login-page">
      <style>{`
        .hq-login-page {
          min-height: 100vh;
          width: 100vw;
          display: flex;
          align-items: center;
          justify-content: center;
          position: relative;
          overflow: hidden;
          font-family: 'Inter', system-ui, sans-serif;
          color: white;
        }

        .hq-login-bg {
          position: absolute;
          top: -2%; left: -2%; right: -2%; bottom: -2%;
          background: linear-gradient(135deg, rgba(12, 36, 75, 0.85) 0%, rgba(20, 60, 110, 0.4) 100%), url('/bg-station.jpg');
          background-size: cover;
          background-position: center;
          z-index: -1;
          animation: bgZoom 20s infinite alternate cubic-bezier(0.4, 0, 0.2, 1);
        }

        @keyframes bgZoom {
          0% { transform: scale(1); }
          100% { transform: scale(1.05); }
        }

        .branding-fade {
          animation: fadeIn 1s ease-out forwards;
        }

        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }

        /* Top Left Branding */
        .top-left-branding {
          position: absolute;
          top: 2rem;
          left: 2.5rem;
          display: flex;
          align-items: center;
          gap: 1rem;
          z-index: 10;
        }

        /* Top Right Branding */
        .top-right-branding {
          position: absolute;
          top: 2.5rem;
          right: 2.5rem;
          text-align: right;
          z-index: 10;
        }
        
        .top-right-branding .divider {
          height: 1px;
          background: rgba(255, 255, 255, 0.4);
          width: 60px;
          display: inline-block;
          vertical-align: middle;
          margin-right: 10px;
        }

        /* Left Tagline */
        .left-tagline {
          position: absolute;
          left: 4rem;
          top: 50%;
          transform: translateY(-50%);
          z-index: 10;
          border-left: 2px solid rgba(255, 255, 255, 0.4);
          padding-left: 1.5rem;
        }

        .tagline-main {
          font-size: 3.5rem;
          font-weight: 600;
          font-style: italic;
          line-height: 1.1;
          margin-bottom: 1rem;
          text-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }

        .tagline-sub {
          font-size: 0.9rem;
          font-weight: 500;
          letter-spacing: 0.5px;
          opacity: 0.9;
        }

        /* Login Card */
        .login-card-container {
          position: relative;
          z-index: 20;
          animation: cardEntrance 0.8s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
          width: 100%;
          max-width: 440px;
        }

        @keyframes cardEntrance {
          from { opacity: 0; transform: translateY(30px); }
          to { opacity: 1; transform: translateY(0); }
        }

        .login-card {
          background: rgba(255, 255, 255, 0.88);
          backdrop-filter: blur(12px);
          -webkit-backdrop-filter: blur(12px);
          border: 1px solid rgba(255, 255, 255, 0.5);
          border-radius: 16px;
          padding: 3rem 2.5rem;
          box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2), inset 0 1px 0 rgba(255,255,255,0.6);
          color: #333;
        }

        .login-header {
          text-align: center;
          margin-bottom: 2rem;
        }

        .login-header h1 {
          font-size: 1.7rem;
          color: #0b3d91;
          margin: 0 0 0.5rem 0;
          font-weight: 700;
        }

        .login-header p {
          color: #5c6c80;
          font-size: 0.95rem;
          margin: 0;
        }

        /* Form Inputs */
        .login-form-group {
          margin-bottom: 1.25rem;
        }

        .login-form-group label {
          display: block;
          font-size: 0.85rem;
          font-weight: 600;
          color: #334155;
          margin-bottom: 0.4rem;
        }

        .input-wrapper {
          position: relative;
          display: flex;
          align-items: center;
        }

        .input-icon {
          position: absolute;
          left: 12px;
          color: #64748b;
          font-size: 1.1rem;
        }

        .login-input {
          width: 100%;
          padding: 0.8rem 1rem 0.8rem 2.5rem;
          border-radius: 8px;
          border: 1px solid rgba(0, 0, 0, 0.1);
          background: rgba(255, 255, 255, 0.6);
          font-size: 0.95rem;
          color: #1e293b;
          transition: all 0.2s ease;
        }

        .login-input::placeholder {
          color: #94a3b8;
        }

        .login-input:focus {
          outline: none;
          background: #ffffff;
          border-color: #0b3d91;
          box-shadow: 0 0 0 3px rgba(11, 61, 145, 0.15);
        }

        /* Button */
        .login-btn {
          width: 100%;
          background-color: #0b3d91;
          color: white;
          padding: 0.85rem;
          border: none;
          border-radius: 8px;
          font-size: 1rem;
          font-weight: 600;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 0.5rem;
          margin-top: 1.5rem;
          transition: all 0.2s ease;
          box-shadow: 0 4px 12px rgba(11, 61, 145, 0.2);
        }

        .login-btn:hover:not(:disabled) {
          background-color: #082d6b;
          transform: translateY(-1px);
          box-shadow: 0 6px 16px rgba(11, 61, 145, 0.3);
        }

        .login-btn:active:not(:disabled) {
          transform: translateY(1px);
        }

        .login-btn:disabled {
          background-color: #64748b;
          cursor: not-allowed;
          box-shadow: none;
        }

        /* Bottom Text */
        .bottom-left-text {
          position: absolute;
          bottom: 2rem;
          left: 2.5rem;
          font-size: 0.75rem;
          letter-spacing: 2px;
          font-weight: 600;
          display: flex;
          align-items: center;
          z-index: 10;
        }

        .bottom-left-text .divider {
          width: 40px; height: 1px; background: rgba(255,255,255,0.4); margin-right: 15px;
        }

        .bottom-right-text {
          position: absolute;
          bottom: 2rem;
          right: 2.5rem;
          font-size: 0.75rem;
          letter-spacing: 2px;
          font-weight: 600;
          display: flex;
          align-items: center;
          z-index: 10;
        }

        .bottom-right-text .divider {
          width: 40px; height: 1px; background: rgba(255,255,255,0.4); margin-left: 15px;
        }

        @media (max-width: 1024px) {
          .left-tagline { display: none; }
          .top-left-branding { top: 1.5rem; left: 1.5rem; }
          .top-right-branding { display: none; }
          .bottom-left-text { bottom: 1.5rem; left: 1.5rem; }
          .bottom-right-text { display: none; }
        }

        @media (prefers-reduced-motion: reduce) {
          .hq-login-bg { animation: none; }
          .branding-fade, .login-card-container { animation: none; opacity: 1; transform: none; }
          .login-btn { transition: none; }
          .login-input { transition: none; }
        }
      `}</style>

      <div className="hq-login-bg"></div>

      {/* Top Left Branding */}
      <div className="top-left-branding branding-fade">
        <img src="https://upload.wikimedia.org/wikipedia/commons/5/55/Emblem_of_India.svg" alt="Govt of India" style={{ height: "55px", filter: "brightness(0) invert(1)" }} />
        <div>
          <div style={{ fontSize: "0.95rem", fontWeight: "600" }}>पृथ्वी विज्ञान मंत्रालय</div>
          <div style={{ fontSize: "1.05rem", fontWeight: "700" }}>Ministry of Earth Sciences</div>
          <div style={{ fontSize: "0.8rem", opacity: 0.8 }}>Government of India</div>
        </div>
      </div>

      {/* Top Right Branding */}
      <div className="top-right-branding branding-fade" style={{ animationDelay: "0.2s" }}>
        <div style={{ fontSize: "0.95rem", fontWeight: "700", letterSpacing: "0.5px" }}>
          NATIONAL CENTRE FOR POLAR AND OCEAN RESEARCH
        </div>
        <div style={{ fontSize: "0.85rem", fontStyle: "italic", opacity: 0.9, marginTop: "0.3rem" }}>
          <span className="divider"></span>
          Science for a Sustainable Planet
        </div>
      </div>

      {/* Left Tagline */}
      <div className="left-tagline branding-fade" style={{ animationDelay: "0.4s" }}>
        <div className="tagline-main">
          Exploring<br/>
          for a Brighter<br/>
          Tomorrow
        </div>
        <div className="tagline-sub">
          Polar Regions &nbsp;|&nbsp; Oceans &nbsp;|&nbsp; Planetary Wellbeing
        </div>
      </div>

      {/* Center Card */}
      <div className="login-card-container">
        <div className="login-card">
          <div className="login-header">
            <h1>NCPOR Headquarters</h1>
            <p>Goa — Command Center Login</p>
          </div>

          {error && (
            <div style={{
              backgroundColor: "rgba(230, 57, 70, 0.1)",
              border: "1px solid rgba(230, 57, 70, 0.3)",
              borderRadius: "6px",
              padding: "0.75rem 1rem",
              marginBottom: "1.25rem",
              color: "#e63946",
              fontSize: "0.9rem",
              textAlign: "center"
            }}>
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div className="login-form-group">
              <label>Username</label>
              <div className="input-wrapper">
                <span className="input-icon">&#128100;</span>
                <input
                  type="text"
                  className="login-input"
                  placeholder="Enter your username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  autoComplete="username"
                  autoFocus
                  required
                />
              </div>
            </div>

            <div className="login-form-group">
              <label>Password</label>
              <div className="input-wrapper">
                <span className="input-icon">&#128274;</span>
                <input
                  type="password"
                  className="login-input"
                  placeholder="Enter your password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  autoComplete="current-password"
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              className="login-btn"
              disabled={loading}
            >
              {loading ? "Authenticating..." : "Sign In"}
              {!loading && <span>&rarr;</span>}
            </button>
          </form>

          <div style={{ marginTop: "1.5rem", textAlign: "center", color: "#64748b", fontSize: "0.8rem" }}>
            HQ login requires active server connectivity.
          </div>
        </div>
      </div>

      {/* Bottom Text */}
      <div className="bottom-left-text branding-fade" style={{ animationDelay: "0.6s" }}>
        <span className="divider"></span>
        INDIA IN THE POLAR REGIONS
      </div>
      
      <div className="bottom-right-text branding-fade" style={{ animationDelay: "0.6s" }}>
        RESEARCH &nbsp;|&nbsp; RESILIENCE &nbsp;|&nbsp; A SUSTAINABLE PLANET
        <span className="divider"></span>
      </div>
    </div>
  );
}
