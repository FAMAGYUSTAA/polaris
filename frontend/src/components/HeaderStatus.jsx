import React from "react";
import { hasPermission, PERMISSIONS } from "../permissions.js";

export default function HeaderStatus({ isOnline, pendingCount, lastSyncResult, onForceSync, session, onLogout }) {
  const roleName = session.role; // e.g. STATION_LEADER

  return (
    <header className="app-header">
      <div className="header-brand">
        <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
          {/* We will just use the available logo and some text */}
          <img src="/ncpor-circular-logo.jpg" alt="NCPOR" style={{ width: "40px", height: "40px", borderRadius: "50%" }} />
          <div className="header-titles">
            <h1>Ministry of Earth Sciences</h1>
            <h2>Government of India</h2>
          </div>
          <div style={{ width: "1px", height: "30px", background: "rgba(255,255,255,0.2)", margin: "0 0.5rem" }}></div>
          <div className="header-titles">
            <h1>NCPOR</h1>
            <h2>National Centre for Polar and Ocean Research</h2>
          </div>
        </div>
      </div>
      
      <div className="header-controls">
        <div style={{ display: "flex", alignItems: "center", gap: "1.5rem" }}>
          <div className="status-indicator">
            <span className={`status-dot ${isOnline ? 'online' : 'offline'}`}></span>
            <span className="status-text">{isOnline ? "Satellite Linked" : "Offline"}</span>
          </div>
          
          <div style={{ fontSize: "0.85rem", opacity: 0.9 }}>
            {pendingCount} unsynced events
          </div>

          {hasPermission(session.role, PERMISSIONS.DATA_SYNC) && (
            <button 
              className="btn-primary" 
              onClick={onForceSync}
              disabled={!isOnline || pendingCount === 0}
              style={{ padding: "0.4rem 0.8rem", fontSize: "0.85rem" }}
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="16" height="16">
                <path d="M21 12a9 9 0 1 1-9-9c2.52 0 4.93 1 6.74 2.74L21 8 M21 3v5h-5" />
              </svg>
              Force Sync via Satellite
            </button>
          )}
        </div>

        <div className="user-profile">
          <div className="user-details" style={{ textAlign: "right" }}>
            <span style={{ fontSize: "0.85rem", fontWeight: "600" }}>{session.username}</span>
            <span style={{ fontSize: "0.75rem", opacity: 0.8 }}>STATION - {session.station_id} • Authenticated with HQ</span>
          </div>
          <button className="btn-logout" onClick={onLogout}>
            Logout
          </button>
        </div>
      </div>
    </header>
  );
}
