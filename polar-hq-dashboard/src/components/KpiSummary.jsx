import React, { useState, useEffect } from "react";

export default function KpiSummary({ stationId }) {
  const [kpiData, setKpiData] = useState({
    inventory: [],
    cargo: [],
    activeMissions: [],
    personnel: [],
    musterAlerts: [],
  });
  const [isLoading, setIsLoading] = useState(true);
  const [activeModal, setActiveModal] = useState(null);

  useEffect(() => {
    let isMounted = true;
    setIsLoading(true);

    const fetchKpis = async () => {
      try {
        const invRes = await fetch(`/api/inventory?station_id=${stationId}`);
        const invData = invRes.ok ? await invRes.json() : [];
        
        const cargoRes = await fetch(`/api/cargo?station_id=${stationId}`);
        const cargoData = cargoRes.ok ? await cargoRes.json() : [];
        const pendingCargo = cargoData.filter(c => c.status === "PENDING_APPROVAL");

        const perRes = await fetch(`/api/personnel?station_id=${stationId}`);
        const perData = perRes.ok ? await perRes.json() : { personnel: [], active_missions: [] };

        const musterRes = await fetch(`/api/muster-events?station_id=${stationId}`);
        const musterData = musterRes.ok ? await musterRes.json() : [];
        const activeAlerts = musterData.filter(m => m.status === "EMERGENCY" && !m.resolved);

        if (isMounted) {
          setKpiData({
            inventory: invData,
            cargo: pendingCargo,
            activeMissions: perData.active_missions || [],
            personnel: perData.personnel || [],
            musterAlerts: activeAlerts
          });
          setIsLoading(false);
        }
      } catch (err) {
        console.error("Failed to fetch KPIs", err);
        if (isMounted) setIsLoading(false);
      }
    };

    fetchKpis();

    return () => {
      isMounted = false;
    };
  }, [stationId]);

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') setActiveModal(null);
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const openModal = (e, modalName) => {
    e.preventDefault();
    setActiveModal(modalName);
  };

  const closeModal = () => setActiveModal(null);

  const activeMissionName = kpiData.activeMissions.length > 0 
    ? kpiData.activeMissions[0].purpose || "Field Mission" 
    : "None";

  const renderValue = (val) => isLoading ? <span style={{ opacity: 0.5 }}>...</span> : val;

  return (
    <>
      <div className="kpi-row">
        <div className="kpi-card">
          <div className="kpi-icon-box inventory"><span className="material-symbols-outlined" style={{fontSize: "inherit"}}>inventory_2</span></div>
          <div className="kpi-content">
            <div className="kpi-title">Inventory Items</div>
            <div className="kpi-value">{renderValue(kpiData.inventory.length)}</div>
            <div className="kpi-subtext">Total Items</div>
            <a href="#" onClick={(e) => openModal(e, 'inventory')} className="kpi-link">View Inventory &rarr;</a>
          </div>
        </div>
        
        <div className="kpi-card">
          <div className="kpi-icon-box cargo"><span className="material-symbols-outlined" style={{fontSize: "inherit"}}>directions_boat</span></div>
          <div className="kpi-content">
            <div className="kpi-title">Cargo Shipments</div>
            <div className="kpi-value">{renderValue(kpiData.cargo.length)}</div>
            <div className="kpi-subtext">Pending HQ Action</div>
            <a href="#" onClick={(e) => openModal(e, 'cargo')} className="kpi-link">View Shipments &rarr;</a>
          </div>
        </div>
        
        <div className="kpi-card">
          <div className="kpi-icon-box mission"><span className="material-symbols-outlined" style={{fontSize: "inherit"}}>flag</span></div>
          <div className="kpi-content">
            <div className="kpi-title">Active Mission</div>
            <div className="kpi-value" style={{ fontSize: (!isLoading && activeMissionName === "None") ? "1.5rem" : "1.2rem" }}>
              {renderValue(activeMissionName)}
            </div>
            <div className="kpi-subtext">{isLoading ? "Loading..." : activeMissionName === "None" ? "No ongoing mission" : "Currently Deployed"}</div>
            <a href="#" onClick={(e) => openModal(e, 'missions')} className="kpi-link">View Missions &rarr;</a>
          </div>
        </div>
        
        <div className="kpi-card">
          <div className="kpi-icon-box personnel"><span className="material-symbols-outlined" style={{fontSize: "inherit"}}>groups</span></div>
          <div className="kpi-content">
            <div className="kpi-title">Personnel On Station</div>
            <div className="kpi-value">{renderValue(kpiData.personnel.length)}</div>
            <div className="kpi-subtext">Total Personnel</div>
            <a href="#" onClick={(e) => openModal(e, 'personnel')} className="kpi-link">View Personnel &rarr;</a>
          </div>
        </div>
        
        <div className="kpi-card" style={{ borderTop: !isLoading && kpiData.musterAlerts.length > 0 ? "3px solid var(--danger-color)" : "1px solid var(--border-color)" }}>
          <div className="kpi-icon-box muster"><span className="material-symbols-outlined" style={{fontSize: "inherit"}}>warning</span></div>
          <div className="kpi-content">
            <div className="kpi-title" style={{ color: !isLoading && kpiData.musterAlerts.length > 0 ? "var(--danger-color)" : "inherit" }}>
              Muster Alerts
            </div>
            <div className="kpi-value" style={{ color: !isLoading && kpiData.musterAlerts.length > 0 ? "var(--danger-color)" : "inherit" }}>
              {renderValue(kpiData.musterAlerts.length)}
            </div>
            <div className="kpi-subtext">Active Alerts</div>
            <a href="#" onClick={(e) => openModal(e, 'muster')} className="kpi-link">View Muster &rarr;</a>
          </div>
        </div>
      </div>

      {activeModal && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close" onClick={closeModal}>&times;</button>
            <h2 style={{ marginTop: 0, marginBottom: "1rem" }}>
              {activeModal.charAt(0).toUpperCase() + activeModal.slice(1)} Details
            </h2>
            
            {activeModal === 'inventory' && (
              <table className="govt-table">
                <thead><tr><th>Item</th><th>Quantity</th></tr></thead>
                <tbody>
                  {kpiData.inventory.map(i => (
                    <tr key={i.id}><td>{i.name}</td><td>{i.quantity}</td></tr>
                  ))}
                  {kpiData.inventory.length === 0 && <tr><td colSpan="2">No inventory data.</td></tr>}
                </tbody>
              </table>
            )}

            {activeModal === 'cargo' && (
              <table className="govt-table">
                <thead><tr><th>Carrier</th><th>Origin</th><th>ETA</th></tr></thead>
                <tbody>
                  {kpiData.cargo.map(c => (
                    <tr key={c.id}><td>{c.carrier_name}</td><td>{c.origin}</td><td>{new Date(c.expected_arrival).toLocaleDateString()}</td></tr>
                  ))}
                  {kpiData.cargo.length === 0 && <tr><td colSpan="3">No pending shipments.</td></tr>}
                </tbody>
              </table>
            )}

            {activeModal === 'missions' && (
              <table className="govt-table">
                <thead><tr><th>Mission</th><th>Location</th></tr></thead>
                <tbody>
                  {kpiData.activeMissions.map(m => (
                    <tr key={m.id}><td>{m.purpose}</td><td>{m.destination_coords || "Unknown"}</td></tr>
                  ))}
                  {kpiData.activeMissions.length === 0 && <tr><td colSpan="2">No active missions.</td></tr>}
                </tbody>
              </table>
            )}

            {activeModal === 'personnel' && (
              <table className="govt-table">
                <thead><tr><th>Name</th><th>Role</th></tr></thead>
                <tbody>
                  {kpiData.personnel.map(p => (
                    <tr key={p.id}><td>{p.full_name}</td><td>{p.role}</td></tr>
                  ))}
                  {kpiData.personnel.length === 0 && <tr><td colSpan="2">No personnel listed.</td></tr>}
                </tbody>
              </table>
            )}

            {activeModal === 'muster' && (
              <table className="govt-table">
                <thead><tr><th>Time</th><th>Reason</th></tr></thead>
                <tbody>
                  {kpiData.musterAlerts.map(m => (
                    <tr key={m.event_id}><td>{new Date(m.triggered_at).toLocaleString()}</td><td>{m.payload?.reason || "Emergency"}</td></tr>
                  ))}
                  {kpiData.musterAlerts.length === 0 && <tr><td colSpan="2">No active alerts.</td></tr>}
                </tbody>
              </table>
            )}
            
            <div style={{ marginTop: "1.5rem", textAlign: "right" }}>
              <button className="secondary" onClick={closeModal}>Close</button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
