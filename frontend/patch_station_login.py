import os

jsx_content = """import React, { useState } from "react";
import { login } from "../services/authService.js";
import { ROLE_LABELS, ROLES } from "../permissions.js";
import "../login.css"; // The new CSS file for the complete redesign

// SVG Icons
const MapPinIcon = () => (
  <svg className="input-icon" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>
);

const UsersIcon = () => (
  <svg className="input-icon" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>
);

const UserIcon = () => (
  <svg className="input-icon" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
);

const LockIcon = () => (
  <svg className="input-icon" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>
);

const EyeIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>
);

const EyeOffIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line></svg>
);

const ArrowRightIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>
);

const ChevronDownIcon = () => (
  <svg className="select-arrow" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>
);

const ToolIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"></path></svg>
);

/**
 * StationLogin.jsx – Login gate for the Polar Expedition Logistics Station PWA.
 */
export default function StationLogin({ onLogin }) {
  const [stationId, setStationId] = useState("BHARATI");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [selectedRole, setSelectedRole] = useState("STATION_LEADER");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [isOfflineMode, setIsOfflineMode] = useState(false);

  const handleSubmit = async (e, forceOffline = false) => {
    if (e) e.preventDefault();
    if (!username.trim() || !password.trim()) return;

    setLoading(true);
    setError("");
    
    // In actual implementation, authService's login tries online and falls back to offline, 
    // but the original UI had a distinct "Offline Login" note. Here we just call login() 
    // and rely on its internal fallback, or if forced, maybe we pass a flag (not implemented in authService originally).
    // For now, we'll just call the standard login which handles both seamlessly.
    const result = await login(stationId, username.trim(), password, selectedRole);

    if (result.success) {
      onLogin(result.session);
    } else {
      setError(result.error || "Authentication failed");
    }
    setLoading(false);
  };

  return (
    <div className="login-page-container">
      <div className="login-background"></div>
      <div className="login-overlay"></div>

      {/* Header */}
      <header className="login-header">
        <div className="moes-brand">
          <div className="moes-emblem-placeholder">
            {/* Using a text fallback if the emblem asset isn't present, styling it structurally */}
            <svg viewBox="0 0 100 100" fill="currentColor" width="100%" height="100%">
               <path d="M50 5 C30 5, 20 20, 20 20 C20 20, 25 50, 50 90 C75 50, 80 20, 80 20 C80 20, 70 5, 50 5 Z" fill="none" stroke="currentColor" strokeWidth="4"/>
               <circle cx="50" cy="35" r="10" fill="none" stroke="currentColor" strokeWidth="4" />
               <path d="M40 50 L60 50 M45 60 L55 60" stroke="currentColor" strokeWidth="4" strokeLinecap="round"/>
            </svg>
          </div>
          <div className="moes-text">
            <span className="hindi">पृथ्वी विज्ञान मंत्रालय</span>
            <span>Ministry of Earth Sciences</span>
            <span style={{ fontSize: "0.75rem", opacity: 0.8 }}>Government of India</span>
          </div>
        </div>

        <div className="ncpor-brand">
          <img src="/ncpor-circular-logo.jpg" alt="NCPOR Logo" className="ncpor-logo-img" onError={(e) => e.target.style.display='none'} />
          <div className="ncpor-text">
            <span className="acronym">NCPOR</span>
            <span className="full">National Centre for Polar & Ocean Research</span>
            <span className="tagline">Science for a Stronger Tomorrow</span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="login-main-content">
        <div className="promo-section">
          <div className="tricolor-line"></div>
          <div className="promo-subtitle">India in Antarctica</div>
          <h1 className="promo-headline">
            Exploring Today<br/>for a Stronger<br/>Tomorrow
          </h1>
          <div className="promo-footer">
            RESEARCH | RESILIENCE | SUSTAINABILITY
          </div>
        </div>

        <div className="login-card-container">
          <div className="login-card">
            <div className="login-card-header">
              <div className="small-brand">N C P O R</div>
              <h2>Polar Expedition Logistics</h2>
              <p className="subtitle">Station Sign In</p>
            </div>

            {error && (
              <div className="login-error" role="alert">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="login-form">
              <div className="input-group">
                <label htmlFor="station">Station</label>
                <div className="input-wrapper">
                  <MapPinIcon />
                  <select
                    id="station"
                    className="login-input login-select"
                    value={stationId}
                    onChange={(e) => setStationId(e.target.value)}
                  >
                    <option value="BHARATI">Bharati</option>
                    <option value="MAITRI">Maitri</option>
                    <option value="HIMADRI">Himadri</option>
                  </select>
                  <ChevronDownIcon />
                </div>
              </div>

              <div className="input-group">
                <label htmlFor="role">Role</label>
                <div className="input-wrapper">
                  <UsersIcon />
                  <select
                    id="role"
                    className="login-input login-select"
                    value={selectedRole}
                    onChange={(e) => setSelectedRole(e.target.value)}
                  >
                    {Object.entries(ROLE_LABELS).map(([key, label]) => (
                      <option key={key} value={key}>{label}</option>
                    ))}
                  </select>
                  <ChevronDownIcon />
                </div>
              </div>

              <div className="input-group">
                <label htmlFor="username">Username</label>
                <div className="input-wrapper">
                  <UserIcon />
                  <input
                    id="username"
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

              <div className="input-group">
                <label htmlFor="password">Password</label>
                <div className="input-wrapper">
                  <LockIcon />
                  <input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    className="login-input"
                    placeholder="Enter your password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    autoComplete="current-password"
                    required
                  />
                  <button
                    type="button"
                    className="password-toggle"
                    onClick={() => setShowPassword(!showPassword)}
                    aria-label={showPassword ? "Hide password" : "Show password"}
                  >
                    {showPassword ? <EyeOffIcon /> : <EyeIcon />}
                  </button>
                </div>
              </div>

              <button
                type="submit"
                className="signin-btn"
                disabled={loading}
              >
                {loading ? "Authenticating..." : (
                  <>Sign In <ArrowRightIcon /></>
                )}
              </button>
            </form>

            <div className="offline-divider">
              <span>OR</span>
            </div>

            <button 
              type="button" 
              className="offline-btn"
              onClick={() => handleSubmit(null, true)}
              disabled={loading}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <ToolIcon /> Offline Login
              </div>
              <span className="offline-subtitle">For use during limited connectivity</span>
            </button>

            <div className="security-text">
              Secure access for authorised personnel only.<br/>
              All activities are monitored and logged.
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="login-footer">
        <div className="footer-links">
          <a href="#">About NCPOR</a>
          <span className="separator">|</span>
          <a href="#">Privacy Policy</a>
          <span className="separator">|</span>
          <a href="#">Terms of Use</a>
          <span className="separator">|</span>
          <a href="#">Help</a>
        </div>
        <div className="footer-credits">
          National Centre for Polar & Ocean Research<br/>
          Ministry of Earth Sciences, Government of India
        </div>
      </footer>
    </div>
  );
}
"""

with open('src/components/StationLogin.jsx', 'w', encoding='utf-8') as f:
    f.write(jsx_content)

print("Updated StationLogin.jsx")
