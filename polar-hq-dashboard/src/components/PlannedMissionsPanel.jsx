import React, { useState, useEffect } from "react";

export default function PlannedMissionsPanel({ stationId }) {
  const [plannedMissions, setPlannedMissions] = useState([]);
  const [personnelMap, setPersonnelMap] = useState({});

  const fetchData = async () => {
    try {
      // Fetch expeditions
      const expRes = await fetch(`/api/expeditions?station_id=${stationId}`);
      if (expRes.ok) {
        const missions = await expRes.json();
        // Sort chronologically by planned_departure
        missions.sort((a, b) => new Date(a.planned_departure) - new Date(b.planned_departure));
        setPlannedMissions(missions);
      }

      // Fetch personnel for resolving names (in case of IDs)
      const perRes = await fetch(`/api/personnel?station_id=${stationId}`);
      if (perRes.ok) {
        const perData = await perRes.json();
        const pMap = {};
        if (perData.personnel) {
          perData.personnel.forEach(p => {
            pMap[p.id] = p.full_name;
          });
        }
        setPersonnelMap(pMap);
      }
    } catch (err) {
      console.error("Failed to fetch planned missions", err);
    }
  };

  useEffect(() => {
    setPlannedMissions([]); setPersonnelMap({});
    fetchData();
    const intv = setInterval(fetchData, 15000);
    return () => clearInterval(intv);
  }, [stationId]);

  return (
    <div className="panel" style={{ flex: 1 }}>
      <div className="panel-header">
        <h2><span className="panel-header-icon"><span className="material-symbols-outlined" style={{fontSize: "inherit"}}>calendar_today</span></span> Upcoming Planned Missions</h2>
      </div>
      <div className="panel-body" style={{ padding: 0 }}>
        {plannedMissions.length === 0 ? (
          <div className="empty-state">
            <span className="empty-state-icon"><span className="material-symbols-outlined" style={{fontSize: "inherit"}}>calendar_today</span></span>
            <span>No planned missions.</span>
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
              {plannedMissions.map(m => (
                <tr key={m.id}>
                  <td style={{ fontWeight: 500 }}>{m.purpose || "Planned Mission"}</td>
                  <td>Expedition</td>
                  <td>
                    <span className="badge badge-primary">Planned</span>
                  </td>
                  <td style={{ fontSize: "0.85rem", color: "var(--text-muted)" }}>
                    <div style={{ color: "var(--text-primary)" }}>Dept: {m.planned_departure ? new Date(m.planned_departure).toLocaleDateString() : "Unknown"}</div>
                    <div>Ret: {m.planned_return ? new Date(m.planned_return).toLocaleDateString() : "Unknown"}</div>
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
