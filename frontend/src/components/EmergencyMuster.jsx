import React, { useState } from "react";
import db from "../db/dexie.js";
import { hasPermission, PERMISSIONS } from "../permissions.js";

export default function EmergencyMuster({ stationId, session }) {
  const [isConfirming, setIsConfirming] = useState(false);
  const [musterLog, setMusterLog] = useState(null);

  const handleTriggerClick = () => {
    setIsConfirming(true);
  };

  const handleCancel = () => {
    setIsConfirming(false);
  };

  const handleConfirm = async () => {
    const timestamp = new Date().toISOString();
    try {
      await db.outboxEvents.add({
        id: crypto.randomUUID(),
        event_type: "MUSTER_TRIGGERED",
        payload: {
          triggered_at: timestamp,
          initiated_by: "field_ui",
          reason: "Emergency UI Trigger"
        },
        timestamp: timestamp,
        sync_status: "PENDING",
        station_id: stationId
      });
      
      setMusterLog(`Emergency muster logged at ${new Date().toLocaleTimeString()} - all departments notified.`);
      setIsConfirming(false);
    } catch (err) {
      console.error("[EmergencyMuster] Failed to queue muster event:", err);
      alert("Failed to log muster event locally. See console.");
    }
  };

  return (
    <div className="tracker-panel emergency-panel">
      <div className="tracker-header">
        <h2><div className="icon-box danger"><svg viewBox="0 0 24 24" fill="currentColor" width="24" height="24"><path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/></svg></div> Emergency Protocols</h2>
      </div>
      <div className="emergency-container">
        {hasPermission(session.role, PERMISSIONS.EMERGENCY_MUSTER) ? (
          !isConfirming ? (
            <>
              <h3>Emergency Protocols</h3>
              <button className="btn-danger" onClick={handleTriggerClick}><svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20" style={{marginRight:"8px"}}><path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/></svg> INITIATE EMERGENCY MUSTER</button>
            </>
          ) : (
            <div className="muster-confirm-box" style={{textAlign: "center"}}>
              <p style={{marginBottom: "1rem"}}><strong>Are you sure?</strong> This will log a station-wide emergency event.</p>
              <div style={{display: "flex", gap: "1rem", justifyContent: "center"}}>
                <button className="btn-secondary" onClick={handleCancel}>Cancel</button>
                <button className="btn-danger" onClick={handleConfirm}>CONFIRM MUSTER</button>
              </div>
            </div>
          )
        ) : (
          <div style={{textAlign: "center"}}>
            <p><strong>Medical Officer View:</strong> Awaiting station muster status. Medical emergency reporting and casualty tracking will appear here during active muster.</p>
          </div>
        )}
      </div>
      
      {musterLog && (
        <div style={{marginTop: "1rem", color: "#16A34A", fontWeight: "600", textAlign: "center"}}>
          {musterLog}
        </div>
      )}
    </div>
  );
}
