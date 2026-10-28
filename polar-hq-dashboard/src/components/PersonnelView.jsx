import React, { useState, useEffect } from "react";

export default function PersonnelView({ stationId }) {
  const [personnel, setPersonnel] = useState([]);

  useEffect(() => {
    const fetchPersonnel = async () => {
      try {
        const res = await fetch(`/api/personnel?station_id=${stationId}`);
        if (res.ok) {
          const data = await res.json();
          setPersonnel(data.personnel || []);
        }
      } catch (err) {
        console.error("Failed to fetch personnel", err);
      }
    };
    fetchPersonnel();
  }, [stationId]);

  return (
    <div className="hq-main" style={{ gridTemplateColumns: "1fr" }}>
      <div className="panel">
        <div className="panel-header">
          <h2>Personnel on Station</h2>
        </div>
        <div className="panel-body" style={{ padding: 0 }}>
          <table className="govt-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Role</th>
                <th>VHF Channel</th>
              </tr>
            </thead>
            <tbody>
              {personnel.map(p => (
                <tr key={p.id}>
                  <td style={{ fontWeight: 500 }}>{p.full_name}</td>
                  <td>{p.role}</td>
                  <td>{p.vhf_channel || "N/A"}</td>
                </tr>
              ))}
              {personnel.length === 0 && <tr><td colSpan="3" className="empty-state">No personnel found.</td></tr>}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
