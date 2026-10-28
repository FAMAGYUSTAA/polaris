import os

base_dir = r"c:\Users\acer\OneDrive\Desktop\POLAR 2\polar-hq-dashboard"

# App.jsx
app_jsx = """import React, { useState, useEffect } from "react";
import FreshnessIndicator from "./components/FreshnessIndicator.jsx";
import CargoApprovalPanel from "./components/CargoApprovalPanel.jsx";
import MusterAlerts from "./components/MusterAlerts.jsx";
import DirectiveComposer from "./components/DirectiveComposer.jsx";

export default function App() {
  return (
    <div className="hq-root">
      <header className="hq-header">
        <h1>NCPOR Headquarters — Goa</h1>
        {/* Known gap: No authentication/login logic implemented for this HQ MVP dashboard */}
        <div style={{ color: "var(--text-muted)", fontSize: "0.9em" }}>
          Command Center Active
        </div>
      </header>
      <main className="hq-main">
        <div className="left-col" style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          <FreshnessIndicator />
          <MusterAlerts />
          <DirectiveComposer />
        </div>
        <div className="right-col" style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          <CargoApprovalPanel />
        </div>
      </main>
    </div>
  );
}
"""
with open(os.path.join(base_dir, "src", "App.jsx"), "w", encoding="utf-8") as f:
    f.write(app_jsx)

# FreshnessIndicator.jsx
fresh_jsx = """import React, { useState, useEffect } from "react";

export default function FreshnessIndicator() {
  const [status, setStatus] = useState(null);

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const res = await fetch("/api/station-status?station_id=BHARATI");
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
  }, []);

  if (!status) return <div className="panel">Loading connection status...</div>;

  let timeStr = "Never";
  if (status.last_sync_at) {
    const d = new Date(status.last_sync_at);
    timeStr = d.toLocaleString();
  }

  const bgColor = status.is_stale ? "var(--danger-color)" : "var(--success-color)";

  return (
    <div className="panel" style={{ borderLeft: `6px solid ${bgColor}` }}>
      <h2>Bharati Station Connection</h2>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: "1rem" }}>
        <div>
          <strong style={{ fontSize: "1.1rem" }}>Last Synced:</strong> {timeStr}
        </div>
        {status.is_stale ? (
          <div style={{ padding: "0.5rem 1rem", backgroundColor: "var(--danger-color)", color: "white", borderRadius: "4px", fontWeight: "bold" }}>
            ⚠ STALE — no contact in over 24 hours
          </div>
        ) : (
          <div style={{ padding: "0.5rem 1rem", backgroundColor: "var(--success-color)", color: "white", borderRadius: "4px", fontWeight: "bold" }}>
            ONLINE
          </div>
        )}
      </div>
    </div>
  );
}
"""
with open(os.path.join(base_dir, "src", "components", "FreshnessIndicator.jsx"), "w", encoding="utf-8") as f:
    f.write(fresh_jsx)

# CargoApprovalPanel.jsx
cargo_jsx = """import React, { useState, useEffect } from "react";

export default function CargoApprovalPanel() {
  const [shipments, setShipments] = useState([]);
  const [approving, setApproving] = useState(null);

  const fetchCargo = async () => {
    try {
      const res = await fetch("/api/cargo?station_id=BHARATI");
      if (res.ok) setShipments(await res.json());
    } catch (err) {
      console.error("Failed to fetch cargo", err);
    }
  };

  useEffect(() => {
    fetchCargo();
    const intv = setInterval(fetchCargo, 15000);
    return () => clearInterval(intv);
  }, []);

  const handleApprove = async (id) => {
    setApproving(id);
    try {
      const res = await fetch(`/api/cargo/${id}/approve`, { method: "POST" });
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
      <h2>Cargo Approval Workflow</h2>
      
      <div style={{ marginBottom: "2rem" }}>
        <h3 style={{ color: "var(--warning-color)", borderBottom: "1px solid #333", paddingBottom: "0.5rem" }}>
          Requires HQ Action ({pending.length})
        </h3>
        {pending.length === 0 ? (
          <p style={{ color: "var(--text-muted)" }}>No shipments pending approval.</p>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
            {pending.map(s => (
              <div key={s.id} style={{ backgroundColor: "#2d2013", padding: "1rem", borderRadius: "4px", border: "1px solid var(--warning-color)" }}>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.5rem" }}>
                  <strong>{s.carrier_name}</strong>
                  <span style={{ color: "var(--warning-color)" }}>PENDING</span>
                </div>
                <div style={{ fontSize: "0.9em", marginBottom: "1rem", color: "#ddd" }}>
                  Origin: {s.origin}<br/>
                  Departure: {new Date(s.departure_date).toLocaleDateString()}<br/>
                  Expected: {new Date(s.expected_arrival).toLocaleDateString()}
                </div>
                <button 
                  onClick={() => handleApprove(s.id)}
                  disabled={approving === s.id}
                  style={{ width: "100%" }}
                >
                  {approving === s.id ? "Approving..." : "Approve Shipment"}
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      <div>
        <h3 style={{ color: "var(--text-muted)", borderBottom: "1px solid #333", paddingBottom: "0.5rem" }}>
          Other Shipments ({others.length})
        </h3>
        {others.length === 0 ? (
          <p style={{ color: "var(--text-muted)" }}>No other shipments.</p>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
            {others.map(s => (
              <div key={s.id} style={{ backgroundColor: "rgba(255,255,255,0.05)", padding: "0.75rem", borderRadius: "4px", display: "flex", justifyContent: "space-between" }}>
                <span>{s.carrier_name} ({s.origin})</span>
                <span style={{ color: s.status === 'ARRIVED' ? 'var(--success-color)' : '#4da6ff' }}>
                  {s.status}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
"""
with open(os.path.join(base_dir, "src", "components", "CargoApprovalPanel.jsx"), "w", encoding="utf-8") as f:
    f.write(cargo_jsx)

# MusterAlerts.jsx
muster_jsx = """import React, { useState, useEffect } from "react";

export default function MusterAlerts() {
  const [alerts, setAlerts] = useState([]);

  useEffect(() => {
    const fetchMuster = async () => {
      try {
        const res = await fetch("/api/muster-events?station_id=BHARATI");
        if (res.ok) setAlerts(await res.json());
      } catch (err) {
        console.error("Failed to fetch muster alerts", err);
      }
    };
    fetchMuster();
    const intv = setInterval(fetchMuster, 15000);
    return () => clearInterval(intv);
  }, []);

  return (
    <div className="panel" style={{ borderColor: alerts.length > 0 ? "var(--danger-color)" : "var(--border-color)" }}>
      <h2>Emergency Muster Escalation</h2>
      
      {alerts.length > 0 ? (
        <>
          <div style={{ backgroundColor: "var(--danger-color)", color: "white", padding: "1rem", borderRadius: "4px", fontWeight: "bold", fontSize: "1.2rem", textAlign: "center", marginBottom: "1.5rem" }}>
            ⚠ EMERGENCY MUSTER TRIGGERED — Bharati Station
            <div style={{ fontSize: "0.8rem", fontWeight: "normal", marginTop: "0.5rem" }}>
              Most recent: {new Date(alerts[0].triggered_at).toLocaleString()}
            </div>
          </div>
          
          <h3 style={{ fontSize: "1rem", borderBottom: "1px solid #333", paddingBottom: "0.5rem" }}>Historical Muster Log</h3>
          <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem", maxHeight: "300px", overflowY: "auto" }}>
            {alerts.map(a => (
              <div key={a.event_id} style={{ backgroundColor: "rgba(230, 57, 70, 0.1)", padding: "0.75rem", borderRadius: "4px", borderLeft: "4px solid var(--danger-color)" }}>
                <div style={{ color: "var(--danger-color)", fontWeight: "bold", marginBottom: "0.25rem" }}>
                  {new Date(a.triggered_at).toLocaleString()}
                </div>
                <div style={{ color: "#eee" }}>
                  {a.payload.reason || "No reason provided"}
                </div>
              </div>
            ))}
          </div>
        </>
      ) : (
        <div style={{ padding: "2rem", textAlign: "center", color: "var(--success-color)", backgroundColor: "rgba(76, 175, 80, 0.1)", borderRadius: "4px" }}>
          <h3>All Clear</h3>
          <p>No emergency musters recorded.</p>
        </div>
      )}
    </div>
  );
}
"""
with open(os.path.join(base_dir, "src", "components", "MusterAlerts.jsx"), "w", encoding="utf-8") as f:
    f.write(muster_jsx)

# DirectiveComposer.jsx
dir_jsx = """import React, { useState, useEffect } from "react";

export default function DirectiveComposer() {
  const [directives, setDirectives] = useState([]);
  const [formData, setFormData] = useState({ message: "", issued_by: "HQ Goa" });
  const [sending, setSending] = useState(false);

  const fetchDirectives = async () => {
    try {
      const res = await fetch("/api/directives?station_id=BHARATI");
      if (res.ok) setDirectives(await res.json());
    } catch (err) {
      console.error("Failed to fetch directives", err);
    }
  };

  useEffect(() => {
    fetchDirectives();
    const intv = setInterval(fetchDirectives, 15000);
    return () => clearInterval(intv);
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.message.trim() || !formData.issued_by.trim()) return;
    
    setSending(true);
    try {
      const res = await fetch("/api/directives", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          station_id: "BHARATI",
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
    <div className="panel">
      <h2>HQ Directives</h2>
      
      <form onSubmit={handleSubmit} style={{ marginBottom: "2rem", backgroundColor: "rgba(255,255,255,0.02)", padding: "1rem", borderRadius: "4px", border: "1px solid #333" }}>
        <h3 style={{ marginTop: 0, fontSize: "1.1rem" }}>Compose New Directive</h3>
        <div className="form-group">
          <label>Issued By</label>
          <input 
            type="text" 
            value={formData.issued_by} 
            onChange={e => setFormData({...formData, issued_by: e.target.value})} 
            required 
          />
        </div>
        <div className="form-group">
          <label>Message</label>
          <textarea 
            rows="3"
            value={formData.message} 
            onChange={e => setFormData({...formData, message: e.target.value})} 
            placeholder="Enter directive message for the station..."
            required 
          />
        </div>
        <button type="submit" disabled={sending} style={{ width: "100%" }}>
          {sending ? "Sending..." : "Send Directive to Station"}
        </button>
      </form>

      <div>
        <h3 style={{ fontSize: "1rem", borderBottom: "1px solid #333", paddingBottom: "0.5rem" }}>Previously Sent Directives</h3>
        <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem", maxHeight: "400px", overflowY: "auto" }}>
          {directives.length === 0 ? (
            <p style={{ color: "var(--text-muted)" }}>No directives sent.</p>
          ) : (
            directives.map(d => (
              <div key={d.id} style={{ 
                backgroundColor: d.acknowledged ? "rgba(76, 175, 80, 0.1)" : "rgba(255, 152, 0, 0.1)", 
                padding: "1rem", 
                borderRadius: "4px", 
                borderLeft: `4px solid ${d.acknowledged ? "var(--success-color)" : "var(--warning-color)"}` 
              }}>
                <div style={{ marginBottom: "0.5rem", color: "#ddd" }}>
                  "{d.message}"
                </div>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.85rem" }}>
                  <span style={{ color: "var(--text-muted)" }}>{new Date(d.issued_at).toLocaleString()}</span>
                  
                  {d.acknowledged ? (
                    <span style={{ color: "var(--success-color)", fontWeight: "bold" }}>
                      ✓ Acknowledged ({new Date(d.acknowledged_at).toLocaleTimeString()})
                    </span>
                  ) : (
                    <span style={{ color: "var(--warning-color)", fontWeight: "bold" }}>
                      ⏳ Awaiting Acknowledgment
                    </span>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
"""
with open(os.path.join(base_dir, "src", "components", "DirectiveComposer.jsx"), "w", encoding="utf-8") as f:
    f.write(dir_jsx)

print("HQ components built.")
