import React, { useState, useEffect } from "react";
import db from "../db/dexie.js";
import { hasPermission, PERMISSIONS } from "../permissions.js";
import { syncExpeditionsFromServer } from "../services/syncService.js";

/**
 * ExpeditionPlanning.jsx
 *
 * Allows planning and cancelling future expeditions entirely offline.
 */
export default function ExpeditionPlanning({ stationId, session }) {
  const [expeditions, setExpeditions] = useState([]);
  const [personnel, setPersonnel] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // Form State
  const [isPlanOpen, setIsPlanOpen] = useState(false);
  const [planData, setPlanData] = useState({
    team_lead: "",
    purpose: "",
    destination_coords: "",
    vhf_channel: "",
    planned_departure: "",
    planned_return: ""
  });
  const [selectedPersonnelIds, setSelectedPersonnelIds] = useState(new Set());
  const [formError, setFormError] = useState("");
  
  // Cancel confirmation state
  const [cancellingId, setCancellingId] = useState(null);

  const loadLocalData = async () => {
    try {
      const allExps = await db.plannedExpeditions.where("status").equals("PLANNED").toArray();
      const stationExps = allExps.filter(e => e.station_id === stationId);
      // Sort soonest upcoming first
      stationExps.sort((a, b) => new Date(a.planned_departure) - new Date(b.planned_departure));
      setExpeditions(stationExps);
      
      const allPersonnel = await db.personnel.filter(i => i.station_id === stationId).toArray();
      setPersonnel(allPersonnel);
    } catch (err) {
      console.error("[ExpeditionPlanning] Failed to read from Dexie", err);
    }
  };

  useEffect(() => {
    const init = async () => {
      await loadLocalData();
      setLoading(false);
      try {
        await syncExpeditionsFromServer(stationId);
        await loadLocalData();
      } catch (err) {
        console.warn("[ExpeditionPlanning] Could not pull ground truth from server. Using local cache.", err);
      }
    };
    init();
  }, []);

  const toggleSelection = (id) => {
    const newSet = new Set(selectedPersonnelIds);
    if (newSet.has(id)) newSet.delete(id);
    else newSet.add(id);
    setSelectedPersonnelIds(newSet);
  };

  const handlePlanSubmit = async (e) => {
    e.preventDefault();
    if (!planData.team_lead.trim() || !planData.purpose.trim()) {
      setFormError("Team lead and purpose are required.");
      return;
    }
    const depTime = new Date(planData.planned_departure);
    const retTime = new Date(planData.planned_return);
    if (retTime <= depTime) {
      setFormError("Planned return must be after planned departure.");
      return;
    }

    const membersList = Array.from(selectedPersonnelIds).map(id => {
      const p = personnel.find(x => x.id === id);
      return p ? p.full_name : id;
    });

    const newExpedition = {
      id: crypto.randomUUID(),
      station_id: stationId,
      team_lead: planData.team_lead.trim(),
      members: membersList,
      purpose: planData.purpose.trim(),
      destination_coords: planData.destination_coords.trim(),
      vhf_channel: planData.vhf_channel.trim(),
      planned_departure: planData.planned_departure,
      planned_return: planData.planned_return,
      status: "PLANNED"
    };

    try {
      await db.plannedExpeditions.add(newExpedition);
      await db.outboxEvents.add({
        id: crypto.randomUUID(),
        event_type: "EXPEDITION_PLANNED",
        payload: newExpedition,
        timestamp: new Date().toISOString(),
        sync_status: "PENDING",
        station_id: stationId
      });
      await loadLocalData();
      setIsPlanOpen(false);
      setPlanData({ team_lead: "", purpose: "", destination_coords: "", vhf_channel: "", planned_departure: "", planned_return: "" });
      setSelectedPersonnelIds(new Set());
      setFormError("");
    } catch (err) {
      console.error("[ExpeditionPlanning] Failed to save expedition locally", err);
      setFormError("Failed to save expedition locally.");
    }
  };

  const handleConfirmCancel = async (exp) => {
    try {
      // Opt 1: Update status to CANCELLED locally (will be hidden by loadLocalData query)
      await db.plannedExpeditions.update(exp.id, { status: "CANCELLED" });
      
      await db.outboxEvents.add({
        id: crypto.randomUUID(),
        event_type: "EXPEDITION_CANCELLED",
        payload: { expedition_id: exp.id },
        timestamp: new Date().toISOString(),
        sync_status: "PENDING",
        station_id: stationId
      });
      
      await loadLocalData();
      setCancellingId(null);
    } catch (err) {
      console.error("[ExpeditionPlanning] Failed to cancel expedition locally", err);
      alert("Failed to cancel expedition locally.");
    }
  };

  if (loading) return <div className="tracker-panel">Loading expeditions...</div>;

  return (
    <div className="tracker-panel">
      <div className="tracker-header">
        <h2><div className="icon-box "><svg viewBox="0 0 24 24" fill="currentColor" width="24" height="24"><path d="M14 6m-3 0a3 3 0 1 0 6 0 3 3 0 1 0 -6 0M1 21h22L15 10 10 16 7 12 1 21z"/></svg></div> Upcoming Expeditions (Planned)</h2>
        {hasPermission(session.role, PERMISSIONS.PLANNED_EXPEDITIONS) && (<button className="btn-secondary" onClick={() => setIsPlanOpen(!isPlanOpen)}>
          {isPlanOpen ? "Cancel Planning" : "Plan New Expedition"}
        </button>)}
      </div>

      {isPlanOpen && (
        <div className="checkout-form-container">
          <h3>Plan Future Expedition</h3>
          {formError && <div style={{ color: "#ff5252", marginBottom: "1rem" }}>{formError}</div>}
          <form onSubmit={handlePlanSubmit} className="checkout-form">
            <div className="form-group">
              <label>Team Lead</label>
              <input type="text" value={planData.team_lead} onChange={e => setPlanData({...planData, team_lead: e.target.value})} placeholder="e.g. Dr. Sarah Chen" required />
            </div>
            <div className="form-group">
              <label>Purpose</label>
              <input type="text" value={planData.purpose} onChange={e => setPlanData({...planData, purpose: e.target.value})} placeholder="e.g. Ice core sampling" required />
            </div>
            <div className="form-group">
              <label>Destination Coords</label>
              <input type="text" value={planData.destination_coords} onChange={e => setPlanData({...planData, destination_coords: e.target.value})} placeholder="-69.40, 76.18" />
            </div>
            <div className="form-group">
              <label>VHF Channel</label>
              <input type="text" value={planData.vhf_channel} onChange={e => setPlanData({...planData, vhf_channel: e.target.value})} placeholder="CH-16" />
            </div>
            <div className="form-group">
              <label>Planned Departure</label>
              <input type="datetime-local" value={planData.planned_departure} onChange={e => setPlanData({...planData, planned_departure: e.target.value})} required />
            </div>
            <div className="form-group">
              <label>Planned Return</label>
              <input type="datetime-local" value={planData.planned_return} onChange={e => setPlanData({...planData, planned_return: e.target.value})} required />
            </div>
            
            <div className="form-group" style={{ gridColumn: "1 / -1", marginTop: "1rem" }}>
              <label>Select Team Members ({selectedPersonnelIds.size})</label>
              <div style={{ maxHeight: "150px", overflowY: "auto", border: "1px solid #333", padding: "0.5rem", borderRadius: "4px" }}>
                {personnel.map(p => (
                  <div key={p.id} style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.25rem" }}>
                    <input 
                      type="checkbox" 
                      id={`chk-${p.id}`}
                      checked={selectedPersonnelIds.has(p.id)}
                      onChange={() => toggleSelection(p.id)}
                    />
                    <label htmlFor={`chk-${p.id}`} style={{ margin: 0, fontWeight: "normal" }}>{p.full_name} ({p.role})</label>
                  </div>
                ))}
              </div>
            </div>
            
            <button type="submit" className="btn-primary" style={{ gridColumn: "1 / -1", marginTop: "1rem" }}>
              Submit Planned Expedition
            </button>
          </form>
        </div>
      )}

      {expeditions.length === 0 ? (
        <div className="empty-state">
          <p>No upcoming expeditions planned.</p>
        </div>
      ) : (
        <div className="active-missions">
          <div className="mission-grid">
            {expeditions.map(m => (
              <div key={m.id} className="mission-card">
                <div className="mission-details">
                  <strong>Lead:</strong> {m.team_lead} <br />
                  <strong>Purpose:</strong> {m.purpose} <br />
                  <strong>Dest:</strong> {m.destination_coords || 'Unknown'} <br />
                  <strong>VHF:</strong> {m.vhf_channel || 'N/A'} <br />
                  <strong>Departure:</strong> {new Date(m.planned_departure).toLocaleString()} <br />
                  <strong>Return:</strong> {new Date(m.planned_return).toLocaleString()}
                </div>
                
                <div style={{ marginTop: "1rem" }}>
                  {hasPermission(session.role, PERMISSIONS.FIELD_MISSION_MANAGEMENT) && (
                    cancellingId === m.id ? (
                      <div style={{ display: "flex", gap: "0.5rem" }}>
                        <button 
                          onClick={() => setCancellingId(null)}
                          className="btn-secondary"
                        >
                          Abort Cancel
                        </button>
                        <button 
                          onClick={() => handleConfirmCancel(m)}
                          className="btn-danger"
                        >
                          Confirm Cancel
                        </button>
                      </div>
                    ) : (
                      <button 
                        onClick={() => setCancellingId(m.id)}
                        className="btn-secondary"
                      >
                        Cancel Expedition
                      </button>
                    )
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
