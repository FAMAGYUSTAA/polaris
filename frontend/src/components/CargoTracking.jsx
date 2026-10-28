import React, { useState, useEffect } from "react";
import db from "../db/dexie.js";
import { hasPermission, PERMISSIONS } from "../permissions.js";
import { syncCargoFromServer } from "../services/syncService.js";

const API_BASE = "";

export default function CargoTracking({ stationId, session }) {
  const [shipments, setShipments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [notification, setNotification] = useState(null);
  const [actionLoadingId, setActionLoadingId] = useState(null);

  const loadLocalData = async () => {
    try {
      const allShipments = await db.cargoShipments.filter(i => i.station_id === stationId).toArray();
      setShipments(allShipments);
    } catch (err) {
      console.error("[CargoTracking] Failed to read from Dexie", err);
    }
  };

  const init = async () => {
    setLoading(true);
    await loadLocalData();
    setLoading(false);
    try {
      await syncCargoFromServer(stationId);
      await loadLocalData();
    } catch (err) {
      console.warn("[CargoTracking] Could not pull from server. Using local cache.", err);
    }
  };

  useEffect(() => {
    init();
    const interval = setInterval(init, 10000);
    return () => clearInterval(interval);
  }, []);

  const handleMarkArrived = async (id) => {
    setActionLoadingId(id);
    setNotification(null);
    try {
      const shipment = await db.cargoShipments.get(id);
      if (!shipment) throw new Error("Shipment not found locally");
      if (!shipment.hq_approved) throw new Error("Cannot mark unapproved shipment as arrived.");

      const arrivedAt = new Date().toISOString();
      
      // Update cargo locally
      await db.cargoShipments.update(id, { 
        status: "ARRIVED", 
        arrived_at: arrivedAt 
      });

      // Update inventory locally (optimistic)
      for (const item of shipment.manifest) {
        const invItem = await db.inventory.where("sku").equals(item.sku).first();
        if (invItem) {
          await db.inventory.update(invItem.id, {
            quantity: invItem.quantity + item.quantity
          });
        }
      }

      // Queue outbox event
      await db.outboxEvents.add({
        id: crypto.randomUUID(),
        event_type: "CARGO_MARKED_ARRIVED",
        payload: { shipment_id: id },
        timestamp: arrivedAt,
        sync_status: "PENDING",
        station_id: stationId
      });

      setNotification({ type: "success", message: "Shipment marked arrived (Offline). Inventory updated locally." });
      await loadLocalData();
    } catch (err) {
      console.error("[CargoTracking] Mark arrived error:", err);
      setNotification({ type: "warning", message: err.message || "Failed to mark arrived." });
    } finally {
      setActionLoadingId(null);
    }
  };

  const inTransit = shipments.filter(s => s.status === "IN_TRANSIT" || s.status === "DELAYED" || s.status === "PENDING_APPROVAL");
  const arrived = shipments.filter(s => s.status === "ARRIVED");

  const getStatusColor = (status) => {
    if (status === "IN_TRANSIT") return "#2196f3";
    if (status === "DELAYED") return "#ff9800";
    if (status === "PENDING_APPROVAL") return "#888";
    if (status === "ARRIVED") return "#4caf50";
    return "#888";
  };

  return (
    <div className="tracker-panel" >
      <div className="tracker-header">
        <h2><div className="icon-box "><svg viewBox="0 0 24 24" fill="currentColor" width="24" height="24"><path d="M21 16.5c0 .38-.21.71-.53.88l-7.9 4.44c-.16.12-.36.18-.57.18s-.41-.06-.57-.18l-7.9-4.44A.991.991 0 0 1 3 16.5v-9c0-.38.21-.71.53-.88l7.9-4.44c.16-.12.36-.18.57-.18s.41.06.57.18l7.9 4.44c.32.17.53.5.53.88v9zM12 4.15L6.04 7.5 12 10.85l5.96-3.35L12 4.15z"/></svg></div> Cargo Tracking</h2>
        <div >
          <button 
            className="btn-secondary" 
            onClick={init}
            
          >
            Refresh
          </button>
          {hasPermission(session.role, PERMISSIONS.CARGO_RECEIVE) && (<button className="btn-primary" onClick={() => setShowModal(true)}>+ New Shipment</button>)}
        </div>
      </div>

      {notification && (
        <div style={{ 
          padding: "1rem", 
          marginBottom: "1rem", 
          backgroundColor: notification.type === "warning" ? "#3e2723" : "#1b5e20",
          borderLeft: `4px solid ${notification.type === "warning" ? "#ff9800" : "#4caf50"}`,
          color: "#fff"
        }}>
          {notification.message}
        </div>
      )}

      {loading && shipments.length === 0 ? (
        <div >
          Loading cargo data...
        </div>
      ) : (
        <div >
          {/* Active/In-Transit Shipments */}
          <div>
            <h3 >
              Inbound / Active ({inTransit.length})
            </h3>
            {inTransit.length === 0 ? (
              <p >No active incoming cargo.</p>
            ) : (
              <div className="cargo-section">
                {inTransit.map(shipment => (
                  <div key={shipment.id} className="cargo-row" >
                    <div >
                      <strong >{shipment.carrier_name}</strong>
                      <span >
                        {shipment.status.replace("_", " ")}
                      </span>
                    </div>
                    
                    <div >
                      <div><strong>Origin:</strong> {shipment.origin}</div>
                      <div>
                        <strong>HQ Approved:</strong> {shipment.hq_approved ? 
                          <span >Yes</span> : 
                          <span >Pending</span>
                        }
                      </div>
                      <div><strong>Departs:</strong> {new Date(shipment.departure_date).toLocaleString()}</div>
                      <div><strong>ETA:</strong> {new Date(shipment.expected_arrival).toLocaleString()}</div>
                    </div>

                    <div >
                      <strong >Manifest:</strong>
                      <ul >
                        {shipment.manifest.map((item, idx) => (
                          <li key={idx}>{item.quantity} {item.unit} - {item.name} <span >(SKU: {item.sku})</span></li>
                        ))}
                      </ul>
                    </div>

                    <div >
                      {hasPermission(session?.role, PERMISSIONS.CARGO_RECEIVE) && <button 
                        onClick={() => handleMarkArrived(shipment.id)}
                        disabled={actionLoadingId === shipment.id || !shipment.hq_approved}
                        
                        title={!shipment.hq_approved ? "Cannot mark arrived until HQ approves" : ""}
                      >
                        {actionLoadingId === shipment.id ? "Marking Arrived..." : "Mark Arrived"}
                      </button>}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Arrived Shipments */}
          <div>
            <h3 >
              Recently Arrived ({arrived.length})
            </h3>
            {arrived.length === 0 ? (
              <p >No recent arrivals.</p>
            ) : (
              <div className="cargo-section">
                {arrived.map(shipment => (
                  <div key={shipment.id} className="cargo-row" >
                    <div >
                      <strong >{shipment.carrier_name}</strong>
                      <span >ARRIVED</span>
                    </div>
                    
                    <div >
                      <strong>Arrived At:</strong> {new Date(shipment.arrived_at).toLocaleString()}
                    </div>

                    <div >
                      <strong >Manifest:</strong>
                      <ul >
                        {shipment.manifest.map((item, idx) => (
                          <li key={idx}>{item.quantity} {item.unit} - {item.name}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {showModal && <NewShipmentModal stationId={stationId} onClose={() => setShowModal(false)} onCreated={() => { setShowModal(false); init(); }} />}
    </div>
  );
}

function NewShipmentModal({ stationId, onClose, onCreated }) {
  const [submitting, setSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    carrier_name: "",
    origin: "",
    departure_date: "",
    expected_arrival: "",
  });
  
  const [manifest, setManifest] = useState([
    { sku: "", name: "", quantity: "", unit: "" }
  ]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);

    try {
      // Ensure numbers for quantity
      const processedManifest = manifest.map(m => ({
        ...m,
        quantity: parseFloat(m.quantity) || 0
      })).filter(m => m.sku.trim() !== "");

      const shipmentId = crypto.randomUUID();
      const now = new Date().toISOString();

      const payload = {
        id: shipmentId,
        station_id: stationId,
        carrier_name: formData.carrier_name,
        origin: formData.origin,
        departure_date: new Date(formData.departure_date).toISOString(),
        expected_arrival: new Date(formData.expected_arrival).toISOString(),
        manifest: processedManifest,
        status: "PENDING_APPROVAL",
        hq_approved: false,
        created_at: now
      };

      // 1. Save to Dexie
      await db.cargoShipments.add({
        ...payload,
        arrived_at: null
      });

      // 2. Queue outbox event
      await db.outboxEvents.add({
        id: crypto.randomUUID(), // outbox event needs its own id
        event_type: "CARGO_CREATED",
        payload: payload,
        timestamp: now,
        sync_status: "PENDING",
        station_id: stationId
      });

      onCreated();
    } catch (err) {
      console.error("Failed to create shipment locally:", err);
      alert("Failed to create shipment.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleItemChange = (index, field, value) => {
    const newManifest = [...manifest];
    newManifest[index][field] = value;
    setManifest(newManifest);
  };

  const addItem = () => {
    setManifest([...manifest, { sku: "", name: "", quantity: "", unit: "" }]);
  };

  const removeItem = (index) => {
    if (manifest.length > 1) {
      setManifest(manifest.filter((_, i) => i !== index));
    }
  };

  return (
    <div >
      <div >
        <h3 >Create New Shipment (Offline Ready)</h3>
        
        <form onSubmit={handleSubmit} >
          <div>
            <label >Carrier Name</label>
            <input required type="text" value={formData.carrier_name} onChange={e => setFormData({...formData, carrier_name: e.target.value})}  placeholder="e.g. IL-76 Flight" />
          </div>
          <div>
            <label >Origin</label>
            <input required type="text" value={formData.origin} onChange={e => setFormData({...formData, origin: e.target.value})}  placeholder="e.g. Goa, India" />
          </div>
          <div >
            <div >
              <label >Departure Date</label>
              <input required type="datetime-local" value={formData.departure_date} onChange={e => setFormData({...formData, departure_date: e.target.value})}  />
            </div>
            <div >
              <label >Expected Arrival</label>
              <input required type="datetime-local" value={formData.expected_arrival} onChange={e => setFormData({...formData, expected_arrival: e.target.value})}  />
            </div>
          </div>

          <div >
            <label >Manifest</label>
            {manifest.map((item, idx) => (
              <div key={idx} >
                <input required placeholder="SKU" value={item.sku} onChange={e => handleItemChange(idx, 'sku', e.target.value)}  />
                <input required placeholder="Name" value={item.name} onChange={e => handleItemChange(idx, 'name', e.target.value)}  />
                <input required type="number" step="any" placeholder="Qty" value={item.quantity} onChange={e => handleItemChange(idx, 'quantity', e.target.value)}  />
                <input required placeholder="Unit" value={item.unit} onChange={e => handleItemChange(idx, 'unit', e.target.value)}  />
                <button type="button" onClick={() => removeItem(idx)} disabled={manifest.length === 1} >X</button>
              </div>
            ))}
            <button type="button" onClick={addItem} >+ Add Item</button>
          </div>

          <div >
            <button type="button" onClick={onClose} disabled={submitting} >Cancel</button>
            <button type="submit" disabled={submitting} >
              {submitting ? "Creating..." : "Create Shipment"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
