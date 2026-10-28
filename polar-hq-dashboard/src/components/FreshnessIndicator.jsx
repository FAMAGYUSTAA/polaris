import React, { useState, useEffect } from "react";

export default function FreshnessIndicator({ stationId }) {
  const [status, setStatus] = useState(null);

  useEffect(() => {
    setStatus(null);
    const fetchStatus = async () => {
      try {
        const res = await fetch(`/api/station-status?station_id=${stationId}`);
        if (res.ok) {
          setStatus(await res.json());
        }
      } catch (err) {
        console.error("Failed to fetch status", err);
      }
    };
    fetchStatus();
    const intv = setInterval(fetchStatus, 15000);
    return () => clearInterval(intv);
  }, [stationId]);

  if (!status) return <div style={{ color: "var(--text-muted)", fontStyle: "italic" }}>Loading sync status...</div>;

  let timeStr = "Never";
  if (status.last_sync_at) {
    const d = new Date(status.last_sync_at);
    timeStr = d.toLocaleString();
  }

  return (
    <div style={{ display: "flex", alignItems: "center", gap: "1.5rem" }}>
      <div style={{ color: "var(--text-muted)" }}>
        Last Sync: <span style={{ color: "var(--text-primary)", fontWeight: "500" }}>{timeStr}</span>
      </div>
      <div style={{ display: "flex", alignItems: "center", fontWeight: "600", color: status.is_stale ? "var(--danger-color)" : "var(--success-color)" }}>
        <span className={`status-dot ${status.is_stale ? "offline" : ""}`}></span>
        {status.is_stale ? "Connection Stale" : "Satellite Linked"}
      </div>
      <button className="outline" style={{ display: "flex", alignItems: "center", gap: "0.4rem", padding: "0.25rem 0.75rem" }}>
        &#x21bb; Force Sync
      </button>
    </div>
  );
}
