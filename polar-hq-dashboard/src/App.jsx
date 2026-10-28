import React, { useState, useEffect } from "react";
import HQLogin from "./components/HQLogin.jsx";
import FreshnessIndicator from "./components/FreshnessIndicator.jsx";
import CargoApprovalPanel from "./components/CargoApprovalPanel.jsx";
import MusterAlerts from "./components/MusterAlerts.jsx";
import DirectiveComposer from "./components/DirectiveComposer.jsx";
import ActiveMissionPanel from "./components/ActiveMissionPanel.jsx";
import PlannedMissionsPanel from "./components/PlannedMissionsPanel.jsx";
import KpiSummary from "./components/KpiSummary.jsx";
import StationsView from "./components/StationsView.jsx";
import PersonnelView from "./components/PersonnelView.jsx";
import ReportsView from "./components/ReportsView.jsx";
import { restoreSession, logout as authLogout } from "./services/authService.js";

export default function App() {
  const [session, setSession] = useState(null);
  const [activeStation, setActiveStation] = useState("BHARATI");
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [currentView, setCurrentView] = useState("dashboard");
  const [theme, setTheme] = useState(() => localStorage.getItem("hqTheme") || "light");

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("hqTheme", theme);
  }, [theme]);

  useEffect(() => {
    const restored = restoreSession();
    if (restored) {
      setSession(restored);
    }
  }, []);

  const handleLogin = (newSession) => {
    setSession(newSession);
    setActiveStation("BHARATI"); // Reset to default on login
    setCurrentView("dashboard");
  };

  const handleLogout = () => {
    authLogout();
    setSession(null);
  };

  // --- Authentication gate ---
  if (!session) {
    return <HQLogin onLogin={handleLogin} />;
  }

  const navigateTo = (e, view) => {
    e.preventDefault();
    setCurrentView(view);
  };

  const renderView = () => {
    switch (currentView) {
      case "dashboard":
        return (
          <>
            <KpiSummary stationId={activeStation} />
            <div className="hq-main" id="dashboard">
              <CargoApprovalPanel stationId={activeStation} />
              <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
                <ActiveMissionPanel stationId={activeStation} />
                <PlannedMissionsPanel stationId={activeStation} />
              </div>
              <DirectiveComposer stationId={activeStation} />
              <MusterAlerts stationId={activeStation} />
            </div>
          </>
        );
      case "stations":
        return <StationsView />;
      case "cargo":
        return (
          <div className="hq-main" style={{ gridTemplateColumns: "1fr" }}>
            <CargoApprovalPanel stationId={activeStation} />
          </div>
        );
      case "missions":
        return (
          <div className="hq-main" style={{ gridTemplateColumns: "1fr" }}>
            <ActiveMissionPanel stationId={activeStation} />
          </div>
        );
      case "personnel":
        return <PersonnelView stationId={activeStation} />;
      case "muster":
        return (
          <div className="hq-main" style={{ gridTemplateColumns: "1fr" }}>
            <MusterAlerts stationId={activeStation} />
          </div>
        );
      case "directives":
        return (
          <div className="hq-main" style={{ gridTemplateColumns: "1fr" }}>
            <DirectiveComposer stationId={activeStation} />
          </div>
        );
      case "reports":
        return <ReportsView stationId={activeStation} />;
      default:
        return <div>View not found</div>;
    }
  };

  return (
    <div className="app-container">
      {/* Ministry Header */}
                  <header className="ministry-header" style={{ padding: "0.75rem 2rem", display: "flex", justifyContent: "space-between", alignItems: "center", backgroundColor: "var(--bg-white)", borderBottom: "1.5px solid var(--border-color)" }}>
        
        {/* LEFT: Government Branding */}
        <div className="logos left-logos" style={{ display: "flex", alignItems: "center", gap: "0.75rem", flex: 1 }}>
          <img src="/emblem-dark.png" alt="Emblem" style={{ height: "50px" }} onError={(e) => e.target.style.display='none'} />
          <div style={{ lineHeight: 1.2 }}>
            <div style={{ fontWeight: "700", color: "var(--text-primary)", fontSize: "0.95rem" }}>पृथ्वी विज्ञान मंत्रालय</div>
            <div style={{ fontWeight: "700", color: "var(--text-primary)", fontSize: "0.95rem" }}>Ministry of Earth Sciences</div>
            <div style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>Government of India</div>
          </div>
        </div>

        {/* CENTER: Logo + NCPOR Heading */}
        <div className="logos center-logos" style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "1rem", flex: 2 }}>
          <img src="/ncpor-circular-logo.jpg" alt="NCPOR Logo" style={{ height: "65px", borderRadius: "50%", objectFit: "contain" }} onError={(e) => e.target.style.display='none'} />
          <div style={{ textAlign: "center", lineHeight: 1.2 }}>
            <div style={{ fontWeight: "800", fontSize: "1.2rem", letterSpacing: "0.5px", color: "var(--ncpor-navy)" }}>NATIONAL CENTRE FOR POLAR AND OCEAN RESEARCH</div>
            <div style={{ fontWeight: "700", color: "var(--ncpor-navy)", fontSize: "0.95rem", marginTop: "0.15rem" }}>Earth System Sciences Organization</div>
            <div style={{ fontStyle: "italic", color: "var(--text-muted)", fontSize: "0.9rem", marginTop: "0.15rem" }}>Science for a Sustainable Planet</div>
          </div>
        </div>

        {/* RIGHT: NCPOR Hindi/English Branding */}
        <div className="logos right-logos" style={{ display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "flex-end", textAlign: "right", gap: "0.15rem", lineHeight: 1.2, flex: 1 }}>
          <div style={{ fontWeight: "700", color: "var(--text-primary)", fontSize: "0.95rem" }}>राष्ट्रीय ध्रुवीय एवं समुद्री अनुसंधान केंद्र</div>
          <div style={{ fontWeight: "700", color: "var(--text-primary)", fontSize: "0.95rem" }}>National Centre for Polar and Ocean Research</div>
          <div style={{ color: "var(--text-muted)", fontSize: "0.8rem" }}>(An Autonomous Institution under MoES, Govt. of India)</div>
        </div>
        
      </header>

      {/* Secondary Dark Header */}
      <div className="hq-header">
        <div className="portal-title" style={{ cursor: "pointer" }} onClick={() => setSidebarCollapsed(!sidebarCollapsed)}>
          <span style={{ fontSize: "1.2rem" }}>&#9776;</span>
          HQ PORTAL
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "1.5rem" }}>
          <div style={{ color: "white", fontSize: "0.85em", textAlign: "right", lineHeight: "1.2" }}>
            <strong style={{ display: "block", fontSize: "0.95rem" }}>{session.username}</strong>
            <span style={{ opacity: 0.8 }}>Headquarters (Goa) &#x25BE;</span>
          </div>
          <button
            onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}
            style={{
              backgroundColor: "transparent",
              color: "white",
              border: "1px solid rgba(255,255,255,0.4)",
              borderRadius: "4px",
              padding: "0.4rem 0.6rem",
              fontSize: "1rem",
            }}
            title="Toggle Theme"
          >
            {theme === "light" ? "🌙" : "☀️"}
          </button>
          <button
            onClick={handleLogout}
            style={{
              backgroundColor: "transparent",
              color: "white",
              border: "1px solid rgba(255,255,255,0.4)",
              borderRadius: "4px",
              padding: "0.4rem 0.8rem",
              fontSize: "0.85rem",
            }}
          >
            Logout
          </button>
        </div>
      </div>

      <div className="layout-wrapper">
        {/* Sidebar */}
        <aside className={`sidebar ${sidebarCollapsed ? 'collapsed' : ''}`}>
          <nav>
            <a href="#dashboard" className={currentView === "dashboard" ? "active" : ""} onClick={(e) => navigateTo(e, "dashboard")}>
              <span style={{ fontSize: "1.2rem", width: "24px", textAlign: "center" }}><span className="material-symbols-outlined" style={{fontSize: "inherit"}}>home</span></span> 
              <span className="nav-label">Dashboard</span>
            </a>
            <a href="#stations" className={currentView === "stations" ? "active" : ""} onClick={(e) => navigateTo(e, "stations")}>
              <span style={{ fontSize: "1.2rem", width: "24px", textAlign: "center" }}><span className="material-symbols-outlined" style={{fontSize: "inherit"}}>pin_drop</span></span> 
              <span className="nav-label">Stations</span>
            </a>
            <a href="#cargo" className={currentView === "cargo" ? "active" : ""} onClick={(e) => navigateTo(e, "cargo")}>
              <span style={{ fontSize: "1.2rem", width: "24px", textAlign: "center" }}><span className="material-symbols-outlined" style={{fontSize: "inherit"}}>inventory_2</span></span> 
              <span className="nav-label">Cargo & Logistics</span>
            </a>
            <a href="#missions" className={currentView === "missions" ? "active" : ""} onClick={(e) => navigateTo(e, "missions")}>
              <span style={{ fontSize: "1.2rem", width: "24px", textAlign: "center" }}><span className="material-symbols-outlined" style={{fontSize: "inherit"}}>flag</span></span> 
              <span className="nav-label">Missions</span>
            </a>
            <a href="#personnel" className={currentView === "personnel" ? "active" : ""} onClick={(e) => navigateTo(e, "personnel")}>
              <span style={{ fontSize: "1.2rem", width: "24px", textAlign: "center" }}><span className="material-symbols-outlined" style={{fontSize: "inherit"}}>groups</span></span> 
              <span className="nav-label">Personnel</span>
            </a>
            <a href="#muster" className={currentView === "muster" ? "active" : ""} onClick={(e) => navigateTo(e, "muster")}>
              <span style={{ fontSize: "1.2rem", width: "24px", textAlign: "center" }}><span className="material-symbols-outlined" style={{fontSize: "inherit"}}>security</span></span> 
              <span className="nav-label">Muster & Safety</span>
            </a>
            <a href="#directives" className={currentView === "directives" ? "active" : ""} onClick={(e) => navigateTo(e, "directives")}>
              <span style={{ fontSize: "1.2rem", width: "24px", textAlign: "center" }}><span className="material-symbols-outlined" style={{fontSize: "inherit"}}>description</span></span> 
              <span className="nav-label">Directives</span>
            </a>
            <a href="#reports" className={currentView === "reports" ? "active" : ""} onClick={(e) => navigateTo(e, "reports")}>
              <span style={{ fontSize: "1.2rem", width: "24px", textAlign: "center" }}><span className="material-symbols-outlined" style={{fontSize: "inherit"}}>bar_chart</span></span> 
              <span className="nav-label">Reports</span>
            </a>
          </nav>
        </aside>

        {/* Main Content */}
        <main className="main-content">
          <div className="hero-banner">
            <div>
              <h2>Welcome to NCPOR Headquarters</h2>
              <p>Monitor and manage logistics, missions and personnel across Indian Antarctic Stations</p>
            </div>
            <div className="hero-quote">
              "Exploring Today<br/>for a Stronger Tomorrow"
              <hr style={{ borderTop: "1px solid currentColor", opacity: 0.5, borderLeft: "none", borderRight: "none", borderBottom: "none", margin: "0.5rem 0 0 auto", width: "40px" }} />
            </div>
          </div>

          <div className="control-bar">
            <div className="control-bar-left">
              <div className="station-select">
                Viewing Station: 
                <select 
                  value={activeStation} 
                  onChange={(e) => setActiveStation(e.target.value)}
                >
                  <option value="BHARATI">Bharati</option>
                  <option value="MAITRI">Maitri</option>
                  <option value="HIMADRI">Himadri</option>
                </select>
              </div>
              <div style={{ color: "var(--text-muted)" }}>
                Lat: {activeStation === "BHARATI" ? "69.41° S" : activeStation === "MAITRI" ? "70.76° S" : "78.92° N"} | 
                Long: {activeStation === "BHARATI" ? "76.23° E" : activeStation === "MAITRI" ? "11.73° E" : "11.93° E"}
              </div>
            </div>
            <div className="control-bar-right">
              <FreshnessIndicator stationId={activeStation} />
            </div>
          </div>

          <div key={`${currentView}-${activeStation}`} className="view-enter">
            {renderView()}
          </div>

          <footer className="govt-footer">
            <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
              <strong style={{ fontSize: "1.2rem" }}>NIC</strong>
              <div style={{ borderLeft: "1px solid rgba(255,255,255,0.3)", paddingLeft: "1rem" }}>
                <a href="#dashboard" onClick={(e) => navigateTo(e, "dashboard")}>Home</a> | 
                <a href="https://ncpor.res.in" target="_blank" rel="noopener noreferrer">About NCPOR</a> | 
                <a href="https://ncpor.res.in/contactus" target="_blank" rel="noopener noreferrer">Contact</a> | 
                <a href="#" onClick={(e) => { e.preventDefault(); alert('Help documentation not yet available.'); }}>Help</a>
              </div>
            </div>
            <div className="right-text">
              भारत सरकार | Government of India<br/>
              <span style={{ opacity: 0.7, fontSize: "0.75rem" }}>Last Updated: {new Date().toLocaleString()}</span>
            </div>
          </footer>
        </main>
      </div>
    </div>
  );
}
