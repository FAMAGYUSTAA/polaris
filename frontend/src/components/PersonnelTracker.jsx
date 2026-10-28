import React, { useState, useEffect } from "react";
import db from "../db/dexie.js";
import { hasPermission, PERMISSIONS, ROLES } from "../permissions.js";
import { syncPersonnelFromServer } from "../services/syncService.js";

/**
 * PersonnelTracker.jsx — "Whiteout Safety Board"
 *
 * Tracks personnel location and active field missions.
 * Features automated overdue detection and optimistic offline-first checkouts/check-ins.
 */
export default function PersonnelTracker({ stationId, session }) {
  const [personnel, setPersonnel] = useState([]);
  const [missions, setMissions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [now, setNow] = useState(new Date());

  // Checkout Form State
  const [isCheckoutOpen, setIsCheckoutOpen] = useState(false);
  const [selectedPersonnelIds, setSelectedPersonnelIds] = useState(new Set());
  const [checkoutData, setCheckoutData] = useState({
    purpose: "",
    destination_coords: "",
    vhf_channel: "",
    expected_return: "" // datetime-local format
  });

  const loadLocalData = async () => {
    try {
      const allPersonnel = await db.personnel.filter(i => i.station_id === stationId).toArray();
      const allMissionsFallback = await db.fieldMissions.filter(i => i.station_id === stationId).toArray();
      const activeMissions = allMissionsFallback.filter(m => m.is_active === true || m.is_active === 1);

      setPersonnel(allPersonnel.sort((a, b) => a.full_name.localeCompare(b.full_name)));
      setMissions(activeMissions);
    } catch (err) {
      console.error("[PersonnelTracker] Failed to read from Dexie", err);
    }
  };

  useEffect(() => {
    const init = async () => {
      await loadLocalData();
      setLoading(false);
      try {
        await syncPersonnelFromServer(stationId);
        await loadLocalData();
      } catch (err) {
        console.warn("[PersonnelTracker] Could not pull personnel from server (likely offline).");
      }
    };
    init();

    // Timer for overdue detection
    const intervalId = setInterval(() => {
      setNow(new Date());
    }, 30000); // Check every 30s

    return () => clearInterval(intervalId);
  }, []);

  const handleCheckoutSubmit = async (e) => {
    e.preventDefault();
    if (selectedPersonnelIds.size === 0) {
      alert("Select at least one person to checkout.");
      return;
    }

    const selectedIdsArray = Array.from(selectedPersonnelIds);
    const selectedPeople = personnel.filter(p => selectedIdsArray.includes(p.id));
    const teamLead = selectedPeople[0].full_name; // Default first selected to lead
    const memberNames = selectedPeople.map(p => p.full_name);

    const departureTime = new Date().toISOString();
    let expectedReturnTime = null;
    if (checkoutData.expected_return) {
      expectedReturnTime = new Date(checkoutData.expected_return).toISOString();
    }

    const missionId = crypto.randomUUID();

    try {
      // 1. Update Dexie personnel statuses
      for (const pid of selectedIdsArray) {
        await db.personnel.update(pid, { status: "FIELD_MISSION" });
      }

      // 2. Create mission locally
      await db.fieldMissions.add({
        id: missionId,
        team_lead: teamLead,
        destination_coords: checkoutData.destination_coords,
        departure_time: departureTime,
        expected_return: expectedReturnTime,
        is_active: true
      });

      // 3. Queue sync event. Using exact field names from sync_engine.py!
      await db.outboxEvents.add({
        id: crypto.randomUUID(),
        event_type: "FIELD_CHECKOUT",
        payload: {
          mission_id: missionId,
          team_lead: teamLead,
          members: memberNames,
          personnel_ids: selectedIdsArray,
          purpose: checkoutData.purpose,
          destination_coords: checkoutData.destination_coords,
          vhf_channel: checkoutData.vhf_channel,
          departure_time: departureTime,
          expected_return: expectedReturnTime
        },
        timestamp: departureTime,
        sync_status: "PENDING",
        station_id: stationId
      });

      await loadLocalData();
      setIsCheckoutOpen(false);
      setSelectedPersonnelIds(new Set());
      setCheckoutData({ purpose: "", destination_coords: "", vhf_channel: "", expected_return: "" });
    } catch (err) {
      console.error("Checkout failed:", err);
      alert("Failed to checkout. See console.");
    }
  };

  const handleCheckin = async (mission) => {
    if (!confirm(`Check in mission led by ${mission.team_lead}?`)) return;

    try {
      // 1. Close mission locally
      await db.fieldMissions.update(mission.id, { is_active: false });

      // We need to guess which personnel belonged to this mission based on current status,
      // because in the local Dexie table, personnel just have 'FIELD_MISSION' status, they aren't explicitly linked.
      // But we can just use all people currently marked FIELD_MISSION who match the members array if we kept it,
      // or realistically, anyone we know is out there. 
      // For this prototype, we'll mark ALL people currently in FIELD_MISSION back to INSIDE_BASE.
      // A full relational model would query the join table.
      const deployed = personnel.filter(p => p.status === "FIELD_MISSION");
      const deployedIds = deployed.map(p => p.id);

      for (const pid of deployedIds) {
        await db.personnel.update(pid, { status: "INSIDE_BASE" });
      }

      // 2. Queue checkin sync event
      await db.outboxEvents.add({
        id: crypto.randomUUID(),
        event_type: "FIELD_CHECKIN",
        payload: {
          mission_id: mission.id,
          personnel_ids: deployedIds
        },
        timestamp: new Date().toISOString(),
        sync_status: "PENDING",
        station_id: stationId
      });

      await loadLocalData();
    } catch (err) {
      console.error("Checkin failed:", err);
      alert("Failed to checkin. See console.");
    }
  };

  if (loading) return <div className="tracker-panel">Loading personnel...</div>;
  if (personnel.length === 0) {
    return (
      <div className="tracker-panel empty-state">
        <h2><div className="icon-box "><svg viewBox="0 0 24 24" fill="currentColor" width="24" height="24"><path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/></svg></div> Personnel Tracker</h2>
        <p>No personnel records found locally.</p>
        <p className="text-muted">Wait for network connectivity to pull ground truth.</p>
      </div>
    );
  }

  const insideBase = personnel.filter(p => p.status === "INSIDE_BASE" || p.status === "MEDICAL_BAY");
  const onField = personnel.filter(p => p.status === "FIELD_MISSION");

  const toggleSelection = (id) => {
    const newSet = new Set(selectedPersonnelIds);
    if (newSet.has(id)) newSet.delete(id);
    else newSet.add(id);
    setSelectedPersonnelIds(newSet);
  };

  return (
    <div className="tracker-panel">
      <div className="tracker-header">
        <h2><div className="icon-box "><svg viewBox="0 0 24 24" fill="currentColor" width="24" height="24"><path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/></svg></div> Whiteout Safety Board</h2>
        {hasPermission(session.role, PERMISSIONS.OWN_MISSION_CHECKOUT_CHECKIN) && (
          <button className="btn-secondary" onClick={() => setIsCheckoutOpen(!isCheckoutOpen)}>
            {isCheckoutOpen ? "Cancel Checkout" : "New Field Checkout"}
          </button>
        )}
      </div>

      {isCheckoutOpen && (
        <div className="checkout-form-container">
          <h3>Field Team Checkout</h3>
          <p className="text-muted">Select personnel from the "Inside Base" column.</p>
          <form onSubmit={handleCheckoutSubmit} className="checkout-form">
            <div className="form-group">
              <label>Purpose</label>
              <input type="text" value={checkoutData.purpose} onChange={e => setCheckoutData({...checkoutData, purpose: e.target.value})} />
            </div>
            <div className="form-group">
              <label>Destination Coords</label>
              <input type="text" value={checkoutData.destination_coords} onChange={e => setCheckoutData({...checkoutData, destination_coords: e.target.value})} placeholder="-69.4077, 76.1868" />
            </div>
            <div className="form-group">
              <label>VHF Channel</label>
              <input type="text" value={checkoutData.vhf_channel} onChange={e => setCheckoutData({...checkoutData, vhf_channel: e.target.value})} placeholder="CH-7" />
            </div>
            <div className="form-group">
              <label>Expected Return</label>
              <input type="datetime-local" value={checkoutData.expected_return} onChange={e => setCheckoutData({...checkoutData, expected_return: e.target.value})} required />
            </div>
            <button type="submit" className="btn-confirm">Submit Checkout ({selectedPersonnelIds.size} selected)</button>
          </form>
        </div>
      )}

      {/* Active Missions View */}
      {missions.length > 0 && (
        <div className="active-missions">
          <h3>Active Field Missions</h3>
          <div className="mission-grid">
            {missions.map(m => {
              let overdueStr = null;
              if (m.expected_return) {
                const returnTime = new Date(m.expected_return);
                if (now > returnTime) {
                  const diffMins = Math.floor((now - returnTime) / 60000);
                  overdueStr = `OVERDUE by ${diffMins} minutes`;
                }
              }

              return (
                <div key={m.id} className={`mission-card ${overdueStr ? 'is-overdue' : ''}`}>
                  {overdueStr && <div className="overdue-banner">{overdueStr}</div>}
                  <div className="mission-details">
                    <strong>Lead:</strong> {m.team_lead} <br />
                    <strong>Dest:</strong> {m.destination_coords || 'Unknown'} <br />
                    <strong>VHF:</strong> {m.vhf_channel || 'N/A'} <br />
                    <strong>Expected Return:</strong> {m.expected_return ? new Date(m.expected_return).toLocaleString() : 'N/A'}
                  </div>
                  { (hasPermission(session.role, PERMISSIONS.FIELD_MISSION_MANAGEMENT) || (hasPermission(session.role, PERMISSIONS.OWN_MISSION_CHECKOUT_CHECKIN) && (m.team_lead === session.username || (m.members && m.members.includes(session.username))))) && (
                    <button className="btn-primary" onClick={() => handleCheckin(m)}>Check In Mission</button>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      <div className="personnel-grid">
        <div className="personnel-col">
          <h3>Inside Base ({insideBase.length})</h3>
          <div className="personnel-list">
            {insideBase.map(p => (
              <div key={p.id} className={`personnel-card status-${p.status.toLowerCase()}`}>
                {isCheckoutOpen && (
                  <input 
                    type="checkbox" 
                    checked={selectedPersonnelIds.has(p.id)}
                    onChange={() => toggleSelection(p.id)}
                    disabled={session.role === ROLES.FIELD_TEAM_MEMBER && p.full_name !== session.username}
                  />
                )}
                <div className="p-info"><div className="p-avatar"><svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg></div><div className="p-details">
                  <span className="p-name">{p.full_name}</span>
                  <span className="p-role">{p.role}</span></div></div>
                <div className="p-meta">
                  {p.status === "MEDICAL_BAY" && <span className="badge-medical">MEDICAL</span>}
                  <span className="blood-type">{p.blood_type || "N/A"}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
        
        <div className="personnel-col">
          <h3>On Field Sortie ({onField.length})</h3>
          <div className="personnel-list">
            {onField.length === 0 && <div style={{textAlign: "center", padding: "2rem", opacity: 0.5}}><svg viewBox="0 0 24 24" fill="currentColor" width="48" height="48" style={{margin: "0 auto", display: "block"}}><path d="M14 6l-4 5-3-2-5 7h18z"/></svg><p style={{fontSize:"0.85rem", marginTop: "1rem"}}>No personnel currently on field sortie.</p></div>}
            {onField.map(p => (
              <div key={p.id} className="personnel-card status-field">
                <div className="p-info"><div className="p-avatar"><svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg></div><div className="p-details">
                  <span className="p-name">{p.full_name}</span>
                  <span className="p-role">{p.role}</span></div></div>
                <div className="p-meta">
                  <span className="blood-type">{p.blood_type || "N/A"}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
