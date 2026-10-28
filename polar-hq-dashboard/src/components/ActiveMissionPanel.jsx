import React, { useState, useEffect } from "react";

export default function ActiveMissionPanel({ stationId }) {
  const [activeMissions, setActiveMissions] = useState([]);
  const [personnelMap, setPersonnelMap] = useState({});

  const fetchData = async () => {
    try {
      const res = await fetch(`/api/personnel?station_id=${stationId}`);
      if (res.ok) {
        const data = await res.json();
        setActiveMissions(data.active_missions || []);
        
        const pMap = {};
        if (data.personnel) {
          data.personnel.forEach(p => {
            pMap[p.id] = p.full_name;
          });
        }
        setPersonnelMap(pMap);
      }
    } catch (err) {
      console.error("Failed to fetch active missions", err);
    }
  };

  useEffect(() => {
    setActiveMissions([]); setPersonnelMap({});
    fetchData();
    const intv = setInterval(fetchData, 15000);
    return () => clearInterval(intv);
  }, [stationId]);

  return (
    <div className="panel" style={{ flex: 1 }}>
      <div className="panel-header">
        <h2><span className="panel-header-icon"><span className="material-symbols-outlined" style={{fontSize: "inherit"}}>flag</span></span> Active / Upcoming Missions</h2>
        <a href="#missions" style={{ color: "var(--accent-primary)" }}>View All</a>
      </div>
      <div className="panel-body" style={{ padding: 0 }}>
        {activeMissions.length === 0 ? (
          <div className="empty-state">
            <span className="empty-state-icon"><span className="material-symbols-outlined" style={{fontSize: "inherit"}}>flag</span></span>
            <span>No missions scheduled.</span>
          </div>
        ) : (
          <table className="govt-table">
            <thead>
              <tr>
                <th>Mission Name</th>
                <th>Type</th>
                <th>Status</th>
                <th>Timeline</th>
              </tr>
            </thead>
            <tbody>
              {activeMissions.map(m => (
                <tr key={m.id} style={{ backgroundColor: "var(--success-light, #d1e7dd)" }}>
                  <td style={{ fontWeight: 500 }}>{m.purpose || "Field Mission"}</td>
                  <td>Outfield</td>
                  <td>
                    <span className="badge badge-success">Active</span>
                  </td>
                  <td style={{ fontSize: "0.85rem", color: "var(--text-muted)" }}>
                    <div style={{ color: "var(--text-primary)" }}>Dept: {m.departure_time ? new Date(m.departure_time).toLocaleDateString() : "Unknown"}</div>
                    <div>Ret: {m.expected_return ? new Date(m.expected_return).toLocaleDateString() : "Unknown"}</div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
