import React, { useState, useEffect } from "react";
import { authFetch } from "../services/authService.js";

export default function DirectiveComposer({ stationId }) {
  const [directives, setDirectives] = useState([]);
  const [formData, setFormData] = useState({ message: "", issued_by: "HQ Goa" });
  const [sending, setSending] = useState(false);

  const fetchDirectives = async () => {
    try {
      const res = await fetch(`/api/directives?station_id=${stationId}`);
      if (res.ok) setDirectives(await res.json());
    } catch (err) {
      console.error("Failed to fetch directives", err);
    }
  };

  useEffect(() => {
    setDirectives([]);
    fetchDirectives();
    const intv = setInterval(fetchDirectives, 15000);
    return () => clearInterval(intv);
  }, [stationId]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.message.trim() || !formData.issued_by.trim()) return;
    
    setSending(true);
    try {
      const res = await authFetch("/api/directives", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          station_id: stationId,
          message: formData.message,
          issued_by: formData.issued_by
        })
      });
      if (res.ok) {
        setFormData({ ...formData, message: "" });
        await fetchDirectives();
      } else {
        alert("Failed to send directive.");
      }
    } catch (err) {
      console.error(err);
      alert("Error sending directive.");
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="panel" style={{ flex: 1 }}>
      <div className="panel-header">
        <h2><span className="panel-header-icon"><span className="material-symbols-outlined" style={{fontSize: "inherit"}}>description</span></span> Recent Directives</h2>
        <a href="#directives" style={{ color: "var(--accent-primary)" }}>View All</a>
      </div>
      <div className="panel-body" style={{ padding: 0 }}>
        {directives.length === 0 ? (
          <div className="empty-state">
            <span className="empty-state-icon"><span className="material-symbols-outlined" style={{fontSize: "inherit"}}>description</span></span>
            <span>No directives found.</span>
          </div>
        ) : (
          <div style={{ maxHeight: "300px", overflowY: "auto" }}>
            <table className="govt-table">
              <thead>
                <tr>
                  <th>Issued By</th>
                  <th style={{ width: "40%" }}>Message</th>
                  <th>Date & Time</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {directives.map(d => (
                  <tr key={d.id}>
                    <td style={{ fontWeight: 500 }}>{d.issued_by}</td>
                    <td style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>"{d.message}"</td>
                    <td style={{ fontSize: "0.85rem", color: "var(--text-muted)" }}>{new Date(d.issued_at).toLocaleString()}</td>
                    <td>
                      {d.acknowledged ? (
                        <span className="badge badge-success">&#10003; Acknowledged</span>
                      ) : (
                        <span className="badge badge-warning">&#8987; Pending</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Composer Form underneath */}
      <div style={{ padding: "1.25rem", backgroundColor: "#f8f9fa", borderTop: "1px solid var(--border-color)" }}>
        <h3 style={{ fontSize: "1rem", color: "var(--text-primary)", marginBottom: "1rem" }}>Compose New Directive</h3>
        <form onSubmit={handleSubmit}>
          <div style={{ display: "flex", gap: "1rem" }}>
            <div className="form-group" style={{ flex: "0 0 200px" }}>
              <input 
                type="text" 
                value={formData.issued_by} 
                onChange={e => setFormData({...formData, issued_by: e.target.value})} 
                required 
                placeholder="Issued By"
              />
            </div>
            <div className="form-group" style={{ flex: 1 }}>
              <input 
                type="text"
                value={formData.message} 
                onChange={e => setFormData({...formData, message: e.target.value})} 
                placeholder="Enter directive message for the station..."
                required 
              />
            </div>
            <div className="form-group">
              <button type="submit" disabled={sending} style={{ height: "100%" }}>
                {sending ? "Sending..." : "Send Directive"}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}
