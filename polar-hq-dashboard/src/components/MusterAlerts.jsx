import React, { useState, useEffect } from "react";

export default function MusterAlerts({ stationId }) {
  const [alerts, setAlerts] = useState([]);

  useEffect(() => {
    setAlerts([]);
    const fetchMuster = async () => {
      try {
        const res = await fetch(`/api/muster-events?station_id=${stationId}`);
        if (res.ok) setAlerts(await res.json());
      } catch (err) {
        console.error("Failed to fetch muster alerts", err);
      }
    };
    fetchMuster();
    const intv = setInterval(fetchMuster, 15000);
    return () => clearInterval(intv);
  }, [stationId]);

  return (
    <div className="panel" style={{ flex: 1, border: alerts.length > 0 ? "2px solid var(--danger-color)" : undefined }}>
      <div className="panel-header">
        <h2 style={{ color: alerts.length > 0 ? "var(--danger-color)" : "inherit" }}>
          <span className="panel-header-icon"><span className="material-symbols-outlined" style={{fontSize: "inherit"}}>security</span></span> Emergency Muster Escalation
        </h2>
      </div>
      
      {alerts.length > 0 ? (
        <div className="panel-body" style={{ padding: 0 }}>
          <div className="muster-danger">
            <h3 style={{ margin: 0, fontSize: "1.4rem" }}><span className="material-symbols-outlined" style={{fontSize: "inherit"}}>warning</span> EMERGENCY MUSTER TRIGGERED &#8212; {stationId} Station</h3>
            <div style={{ marginTop: "0.5rem", opacity: 0.9 }}>
              Most recent: {new Date(alerts[0].triggered_at).toLocaleString()}
            </div>
          </div>
          
          <div style={{ padding: "0 1.25rem 1.25rem 1.25rem" }}>
            <h3 style={{ fontSize: "1rem", color: "var(--text-primary)", borderBottom: "1px solid var(--border-color)", paddingBottom: "0.5rem", marginBottom: "1rem" }}>Historical Muster Log</h3>
            <div style={{ maxHeight: "300px", overflowY: "auto" }}>
              <table className="govt-table">
                <thead>
                  <tr>
                    <th>Date & Time</th>
                    <th>Reason</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {alerts.map(a => (
                    <tr key={a.event_id}>
                      <td style={{ fontWeight: 500, color: "var(--danger-dark)" }}>{new Date(a.triggered_at).toLocaleString()}</td>
                      <td>{a.payload.reason || "No reason provided"}</td>
                      <td><span className="badge badge-danger">Emergency</span></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      ) : (
        <div className="panel-body">
          <div className="muster-all-clear">
            <h3 style={{ margin: "0 0 0.5rem 0" }}>&#10004; All Clear</h3>
            <p style={{ margin: 0 }}>No emergency musters recorded.</p>
          </div>
        </div>
      )}
    </div>
  );
}
