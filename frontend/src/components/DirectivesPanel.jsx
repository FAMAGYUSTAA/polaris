import React, { useState, useEffect } from "react";
import db from "../db/dexie.js";
import { hasPermission, PERMISSIONS } from "../permissions.js";
import { syncDirectivesFromServer } from "../services/syncService.js";

/**
 * DirectivesPanel.jsx
 *
 * Displays HQ directives to station personnel. Allows acknowledging
 * directives offline with full outbox sync support.
 */
export default function DirectivesPanel({ stationId, session }) {
  const [directives, setDirectives] = useState([]);
  const [loading, setLoading] = useState(true);

  const loadLocalData = async () => {
    try {
      const allDirectives = await db.directives.filter(i => i.station_id === stationId).toArray();
      // Sort newest first
      allDirectives.sort((a, b) => new Date(b.issued_at) - new Date(a.issued_at));
      setDirectives(allDirectives);
    } catch (err) {
      console.error("[DirectivesPanel] Failed to read from Dexie", err);
    }
  };

  useEffect(() => {
    const init = async () => {
      await loadLocalData();
      setLoading(false);
      try {
        await syncDirectivesFromServer(stationId);
        await loadLocalData();
      } catch (err) {
        console.warn("[DirectivesPanel] Could not pull ground truth from server. Using local cache.", err);
      }
    };
    init();
  }, []);

  const handleAcknowledge = async (directive) => {
    try {
      // Opt 1: Update status to acknowledged locally
      await db.directives.update(directive.id, { acknowledged: true, acknowledged_at: new Date().toISOString() });
      
      await db.outboxEvents.add({
        id: crypto.randomUUID(),
        event_type: "DIRECTIVE_ACKNOWLEDGED",
        payload: { directive_id: directive.id },
        timestamp: new Date().toISOString(),
        sync_status: "PENDING",
        station_id: stationId
      });
      
      await loadLocalData();
    } catch (err) {
      console.error("[DirectivesPanel] Failed to acknowledge directive locally", err);
      alert("Failed to acknowledge directive.");
    }
  };

  if (loading) return <div className="tracker-panel">Loading HQ Directives...</div>;

  return (
    <div className="tracker-panel">
      <div className="tracker-header">
        <h2><div className="icon-box danger"><svg viewBox="0 0 24 24" fill="currentColor" width="24" height="24"><path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2h12c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z"/></svg></div> HQ Directives</h2>
      </div>

      {directives.length === 0 ? (
        <div className="empty-state">
          <p>No directives from HQ.</p>
        </div>
      ) : (
        <div className="active-missions">
          <div className="mission-grid" style={{ gridTemplateColumns: "1fr" }}>
            {directives.map(d => (
              <div 
                key={d.id} 
                className={d.acknowledged ? "mission-card ack" : "mission-card unack"}
              >
                <div className="mission-details">
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.5rem" }}>
                    <strong className="directive-from">From: {d.issued_by}</strong>
                    <span className="directive-time">{new Date(d.issued_at).toLocaleString()}</span>
                  </div>
                  <p className="directive-msg">
                    {d.message}
                  </p>
                </div>
                
                <div>
                  {(!d.acknowledged && hasPermission(session.role, PERMISSIONS.HQ_DIRECTIVES)) ? (
                    <button 
                      onClick={() => handleAcknowledge(d)}
                      className="btn-primary"
                    >
                      Acknowledge Directive
                    </button>
                  ) : (
                    <div className="directive-ack-time">
                      Acknowledged {d.acknowledged_at ? new Date(d.acknowledged_at).toLocaleString() : ""}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
