import React, { useState, useEffect } from "react";
import { authFetch } from "../services/authService.js";

export default function CargoApprovalPanel({ stationId }) {
  const [shipments, setShipments] = useState([]);
  const [approving, setApproving] = useState(null);

  const fetchCargo = async () => {
    try {
      const res = await fetch(`/api/cargo?station_id=${stationId}`);
      if (res.ok) setShipments(await res.json());
    } catch (err) {
      console.error("Failed to fetch cargo", err);
    }
  };

  useEffect(() => {
    setShipments([]);
    fetchCargo();
    const intv = setInterval(fetchCargo, 15000);
    return () => clearInterval(intv);
  }, [stationId]);

  const handleApprove = async (id) => {
    setApproving(id);
    try {
      const res = await authFetch(`/api/cargo/${id}/approve`, { method: "POST" });
      if (res.ok) {
        await fetchCargo();
      } else {
        alert("Failed to approve shipment.");
      }
    } catch (err) {
      console.error(err);
      alert("Error approving shipment.");
    } finally {
      setApproving(null);
    }
  };

  const pending = shipments.filter(s => s.status === "PENDING_APPROVAL");
  const others = shipments.filter(s => s.status !== "PENDING_APPROVAL");

  return (
    <div className="panel">
      <div className="panel-header">
        <h2><span className="panel-header-icon"><span className="material-symbols-outlined" style={{fontSize: "inherit"}}>directions_boat</span></span> Recent Cargo Shipments</h2>
        <a href="#cargo" style={{ color: "var(--accent-primary)" }}>View All</a>
      </div>
      <div className="panel-body" style={{ padding: 0 }}>
        {shipments.length === 0 ? (
          <div className="empty-state">
            <span className="empty-state-icon"><span className="material-symbols-outlined" style={{fontSize: "inherit"}}>directions_boat</span></span>
            <span>No shipments found.</span>
          </div>
        ) : (
          <table className="govt-table">
            <thead>
              <tr>
                <th>Shipment ID</th>
                <th>Origin</th>
                <th>Status</th>
                <th>ETA</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {shipments.map(s => {
                const isPending = s.status === "PENDING_APPROVAL";
                return (
                  <tr key={s.id} style={{ backgroundColor: isPending ? "var(--warning-light, #fff8e1)" : "transparent" }}>
                    <td style={{ fontWeight: 500 }}>{s.carrier_name}</td>
                    <td>{s.origin}</td>
                    <td>
                      {isPending ? (
                        <span className="badge badge-warning">Pending HQ</span>
                      ) : s.status === 'ARRIVED' ? (
                        <span className="badge badge-success">Arrived</span>
                      ) : (
                        <span className="badge badge-primary">{s.status.replace('_', ' ')}</span>
                      )}
                    </td>
                    <td>{new Date(s.expected_arrival).toLocaleDateString()}</td>
                    <td>
                      {isPending ? (
                        <button 
                          onClick={() => handleApprove(s.id)}
                          disabled={approving === s.id}
                          style={{ padding: "0.25rem 0.75rem", fontSize: "0.8rem" }}
                        >
                          {approving === s.id ? "..." : "Approve"}
                        </button>
                      ) : (
                        <span style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>No Action</span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
