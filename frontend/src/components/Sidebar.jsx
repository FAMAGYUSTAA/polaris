import React from "react";
import { hasPermission, hasAnyPermission, PERMISSIONS } from "../permissions.js";

export default function Sidebar({ session, collapsed, onToggle }) {
  const role = session.role;

  // Determine visibility based on specific permission or overarching STATION_OVERVIEW
  const canSeeCargo = hasAnyPermission(role, [PERMISSIONS.CARGO_TRACKING, PERMISSIONS.STATION_OVERVIEW]);
  const canSeeDirectives = hasAnyPermission(role, [PERMISSIONS.HQ_DIRECTIVES, PERMISSIONS.STATION_OVERVIEW]);
  const canSeeInventory = hasAnyPermission(role, [PERMISSIONS.INVENTORY_MANAGEMENT, PERMISSIONS.STATION_OVERVIEW]);
  const canSeePersonnel = hasAnyPermission(role, [PERMISSIONS.PERSONNEL_MANAGEMENT, PERMISSIONS.OWN_MISSION_CHECKOUT_CHECKIN, PERMISSIONS.EMERGENCY_STATUS_REPORTING, PERMISSIONS.STATION_OVERVIEW]);
  const canSeeExpeditions = hasAnyPermission(role, [PERMISSIONS.PLANNED_EXPEDITIONS, PERMISSIONS.FIELD_MISSION_MANAGEMENT, PERMISSIONS.STATION_OVERVIEW]);
  const canSeeEmergency = hasAnyPermission(role, [PERMISSIONS.EMERGENCY_MUSTER, PERMISSIONS.EMERGENCY_MUSTER_MEDICAL, PERMISSIONS.STATION_OVERVIEW]);
  const canSeeSync = hasAnyPermission(role, [PERMISSIONS.SNEAKERNET, PERMISSIONS.STATION_OVERVIEW, PERMISSIONS.DATA_SYNC]);

  const scrollTo = (id) => {
    const el = document.getElementById(id);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        {!collapsed && <span className="sidebar-title">Dashboard</span>}
        <button className="btn-sidebar-toggle" onClick={onToggle} title="Toggle Sidebar">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M3 12h18M3 6h18M3 18h18" />
          </svg>
        </button>
      </div>
      <nav className="sidebar-nav">
        {canSeeDirectives && (
          <a href="#directives" onClick={(e) => { e.preventDefault(); scrollTo('directives'); }} className="nav-item">
            <svg className="nav-icon" viewBox="0 0 24 24" fill="currentColor"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/></svg>
            {!collapsed && <span>HQ Directives</span>}
          </a>
        )}
        
        {canSeeCargo && (
          <a href="#cargo" onClick={(e) => { e.preventDefault(); scrollTo('cargo'); }} className="nav-item">
            <svg className="nav-icon" viewBox="0 0 24 24" fill="currentColor"><path d="M20,8h-3V4c0-1.1-0.9-2-2-2H9C7.9,2,7,2.9,7,4v4H4c-1.1,0-2,0.9-2,2v10h20V10C22,8.9,21.1,8,20,8z M9,4h6v4H9V4z"/></svg>
            {!collapsed && <span>Cargo Tracking</span>}
          </a>
        )}

        {canSeeInventory && (
          <a href="#inventory" onClick={(e) => { e.preventDefault(); scrollTo('inventory'); }} className="nav-item">
            <svg className="nav-icon" viewBox="0 0 24 24" fill="currentColor"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/></svg>
            {!collapsed && <span>Inventory</span>}
          </a>
        )}

        {canSeePersonnel && (
          <a href="#personnel" onClick={(e) => { e.preventDefault(); scrollTo('personnel'); }} className="nav-item">
            <svg className="nav-icon" viewBox="0 0 24 24" fill="currentColor"><path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/></svg>
            {!collapsed && <span>Personnel</span>}
          </a>
        )}

        {canSeeExpeditions && (
          <a href="#expeditions" onClick={(e) => { e.preventDefault(); scrollTo('expeditions'); }} className="nav-item">
            <svg className="nav-icon" viewBox="0 0 24 24" fill="currentColor"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 9.36l-7.1 7.1a1 1 0 0 1-1.4 0l-2.83-2.83a1 1 0 0 1 0-1.4l7.1-7.1a6 6 0 0 1 9.36-7.94z"/></svg>
            {!collapsed && <span>Expeditions</span>}
          </a>
        )}

        {canSeeEmergency && (
          <a href="#emergency" onClick={(e) => { e.preventDefault(); scrollTo('emergency'); }} className="nav-item">
            <svg className="nav-icon" viewBox="0 0 24 24" fill="currentColor"><path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/></svg>
            {!collapsed && <span>Emergency</span>}
          </a>
        )}

        {canSeeSync && (
          <a href="#sync" onClick={(e) => { e.preventDefault(); scrollTo('sync'); }} className="nav-item">
            <svg className="nav-icon" viewBox="0 0 24 24" fill="currentColor"><path d="M21 12a9 9 0 1 1-9-9c2.52 0 4.93 1 6.74 2.74L21 8 M21 3v5h-5"/></svg>
            {!collapsed && <span>Sync / Export</span>}
          </a>
        )}
      </nav>
      
      {!collapsed && (
        <div className="sidebar-footer">
          <p className="sidebar-motto">
            SCIENCE<br/>
            PEOPLE<br/>
            PLANET<br/>
            <span>A STRONGER TOMORROW</span>
          </p>
        </div>
      )}
    </aside>
  );
}
