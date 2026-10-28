import React, { useState, useEffect } from "react";
import db from "../db/dexie.js";
import { hasPermission, PERMISSIONS } from "../permissions.js";
import { syncInventoryFromServer } from "../services/syncService.js";

/**
 * AssetInventory.jsx
 * 
 * Displays and allows consumption/addition/deletion of inventory items.
 * All mutations are optimistic: written locally to Dexie and queued in the outbox
 * instantly without waiting for a backend round-trip.
 */
export default function AssetInventory({ stationId, session }) {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // Consume Modal state
  const [consumeModalItem, setConsumeModalItem] = useState(null);
  const [consumeAmount, setConsumeAmount] = useState("");
  const [consumeReason, setConsumeReason] = useState("");

  // Add Item Modal state
  const [showAddModal, setShowAddModal] = useState(false);
  const [addForm, setAddForm] = useState({
    sku: "", name: "", category: "Fuel", quantity: "", unit: "", minimum_threshold: ""
  });
  const [addError, setAddError] = useState("");

  // Delete inline confirmation state
  const [deletingId, setDeletingId] = useState(null);

  const loadLocalInventory = async () => {
    try {
      const allItems = await db.inventory.toArray();
      setItems(allItems.filter(i => i.station_id === stationId).sort((a, b) => a.name.localeCompare(b.name)));
    } catch (err) {
      console.error("[AssetInventory] Failed to read from Dexie", err);
    }
  };

  useEffect(() => {
    const init = async () => {
      await loadLocalInventory();
      setLoading(false);
      try {
        await syncInventoryFromServer(stationId);
        await loadLocalInventory();
      } catch (err) {
        console.warn("[AssetInventory] Could not pull ground truth from server (likely offline). Using local cache.", err);
      }
    };
    init();
  }, []);

  const handleConsumeSubmit = async (e) => {
    e.preventDefault();
    if (!consumeModalItem || !consumeAmount || isNaN(consumeAmount) || Number(consumeAmount) <= 0) return;

    const amount = Number(consumeAmount);
    const newQuantity = Math.max(0, consumeModalItem.quantity - amount);

    try {
      await db.inventory.update(consumeModalItem.id, { quantity: newQuantity });
      await db.outboxEvents.add({
        id: crypto.randomUUID(),
        event_type: "ASSET_DELTA",
        payload: {
          item_id: consumeModalItem.id,
          delta: -amount,
          reason: consumeReason || "Consumed via dashboard"
        },
        timestamp: new Date().toISOString(),
        sync_status: "PENDING",
        station_id: stationId
      });
      await loadLocalInventory();
      closeModal();
    } catch (err) {
      console.error("[AssetInventory] Failed to process consumption", err);
      alert("Failed to record consumption locally. See console.");
    }
  };

  const handleAddSubmit = async (e) => {
    e.preventDefault();
    const sku = addForm.sku.trim();
    const name = addForm.name.trim();
    const qty = Number(addForm.quantity);
    const minThresh = Number(addForm.minimum_threshold);

    if (!sku || !name) {
      setAddError("SKU and Name are required.");
      return;
    }
    if (qty < 0 || minThresh < 0) {
      setAddError("Quantity and minimum threshold cannot be negative.");
      return;
    }

    const newItem = {
      id: crypto.randomUUID(),
      station_id: stationId,
      sku,
      name,
      category: addForm.category,
      quantity: qty,
      unit: addForm.unit.trim(),
      minimum_threshold: minThresh
    };

    try {
      await db.inventory.add(newItem);
      await db.outboxEvents.add({
        id: crypto.randomUUID(),
        event_type: "ITEM_CREATED",
        payload: newItem,
        timestamp: new Date().toISOString(),
        sync_status: "PENDING",
        station_id: stationId
      });
      await loadLocalInventory();
      setShowAddModal(false);
      setAddForm({ sku: "", name: "", category: "Fuel", quantity: "", unit: "", minimum_threshold: "" });
      setAddError("");
    } catch (err) {
      console.error("[AssetInventory] Failed to process addition", err);
      setAddError("Failed to record item locally. See console.");
    }
  };

  const handleConfirmDelete = async (item) => {
    try {
      await db.inventory.delete(item.id);
      await db.outboxEvents.add({
        id: crypto.randomUUID(),
        event_type: "ITEM_DELETED",
        payload: { item_id: item.id },
        timestamp: new Date().toISOString(),
        sync_status: "PENDING",
        station_id: stationId
      });
      await loadLocalInventory();
      setDeletingId(null);
    } catch (err) {
      console.error("[AssetInventory] Failed to process deletion", err);
      alert("Failed to delete item locally. See console.");
    }
  };

  const closeModal = () => {
    setConsumeModalItem(null);
    setConsumeAmount("");
    setConsumeReason("");
  };

  if (loading) {
    return <div className="tracker-panel">Loading assets...</div>;
  }

  const priorityNames = ["Jet-A1 Fuel", "Oxygen Cylinders", "Medical Kits", "Rations"];

  const criticalItems = items.filter(i => priorityNames.some(pn => i.name.includes(pn)));
  const otherItems = items.filter(i => !criticalItems.includes(i));

  const renderItemCard = (item) => {
    let maxScale = 100;
    if (item.name.includes("Fuel") || item.category === "Fuel") maxScale = 50000;
    else if (item.name.includes("Medical") || item.category === "Medical") maxScale = 100;
    else if (item.name.includes("Oxygen") || item.category === "Life-Support") maxScale = 100;
    else maxScale = Math.max(item.quantity * 1.5, item.minimum_threshold * 3, 100);

    const fillPercent = Math.min(100, Math.max(0, (item.quantity / maxScale) * 100));
    
    let statusClass = "safe";
    if (item.quantity <= item.minimum_threshold) statusClass = "critical";
    else if (item.quantity <= item.minimum_threshold * 2) statusClass = "warning";

    return (
      <div key={item.id} className="inventory-card">
        <div className="item-header">
          <h3 className="item-name">{item.name}</h3>
          <span className="item-sku">{item.sku}</span>
        </div>
        <div className="item-stats">
          <span className="qty-current">{item.quantity.toLocaleString()}</span>
          <span className="qty-unit">{item.unit}</span>
          <span className={`qty-threshold ${statusClass}`}>
            (Min: {item.minimum_threshold.toLocaleString()})
          </span>
        </div>
        
        <div className="meter-container">
          <div 
            className={`meter-fill ${statusClass}`} 
            style={{ width: `${fillPercent}%` }}
          ></div>
        </div>

        <div className="item-actions" style={{ display: "flex", gap: "0.5rem", marginTop: "1rem" }}>
          {hasPermission(session?.role, PERMISSIONS.INVENTORY_MANAGEMENT) && (
            <>
              <button 
                className="btn-secondary"
                onClick={() => setConsumeModalItem(item)}
                style={{ flex: 1 }}
              >
                Consume
              </button>
              
              {deletingId === item.id ? (
                <div style={{ display: "flex", gap: "0.5rem", flex: 1 }}>
                  <button 
                    onClick={() => setDeletingId(null)}
                    className="btn-secondary"
                    style={{ flex: 1 }}
                  >
                    Cancel
                  </button>
                  <button 
                    onClick={() => handleConfirmDelete(item)}
                    className="btn-danger"
                    style={{ flex: 1 }}
                  >
                    Confirm
                  </button>
                </div>
              ) : (
                <button 
                  onClick={() => setDeletingId(item.id)}
                  className="btn-secondary"
                >
                  Delete
                </button>
              )}
            </>
          )}
        </div>
      </div>

    );
  };

  return (
    <div className="tracker-panel">
      <div className="tracker-header">
        <h2><div className="icon-box "><svg viewBox="0 0 24 24" fill="currentColor" width="24" height="24"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/></svg></div> Asset Inventory</h2>
        {hasPermission(session?.role, PERMISSIONS.INVENTORY_MANAGEMENT) && (<button 
          onClick={() => setShowAddModal(true)}
          className="btn-primary"
        >
          + Add New Item
        </button>)}
      </div>
      
      {items.length === 0 ? (
        <div className="empty-state" style={{ marginTop: "1rem" }}>
          <p>No inventory items found in local database.</p>
          <p className="text-muted">Wait for network connectivity to pull ground truth, or add a new item.</p>
        </div>
      ) : (
        <>
          {criticalItems.length > 0 && (
            <div className="inventory-group">
              <h3 className="group-title">Critical Assets (Monitored)</h3>
              <div className="inventory-grid">
                {criticalItems.map(renderItemCard)}
              </div>
            </div>
          )}

          {otherItems.length > 0 && (
            <div className="inventory-group" style={{ marginTop: "2rem" }}>
              <h3 className="group-title">General Inventory</h3>
              <div className="inventory-grid">
                {otherItems.map(renderItemCard)}
              </div>
            </div>
          )}
        </>
      )}

      {/* Consume Modal */}
      {consumeModalItem && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <h3>Consume: {consumeModalItem.name}</h3>
            <p>Current Quantity: {consumeModalItem.quantity.toLocaleString()} {consumeModalItem.unit}</p>
            
            <form onSubmit={handleConsumeSubmit}>
              <div className="form-group">
                <label>Amount to consume</label>
                <input 
                  type="number" 
                  min="1" 
                  max={consumeModalItem.quantity}
                  value={consumeAmount} 
                  onChange={e => setConsumeAmount(e.target.value)} 
                  required 
                  autoFocus
                />
              </div>
              <div className="form-group">
                <label>Reason (Optional)</label>
                <input 
                  type="text" 
                  placeholder="e.g. Generator Run" 
                  value={consumeReason} 
                  onChange={e => setConsumeReason(e.target.value)} 
                />
              </div>
              <div className="modal-actions">
                <button type="button" className="btn-secondary" onClick={closeModal}>Cancel</button>
                <button type="submit" className="btn-confirm">Confirm</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Add New Item Modal */}
      {showAddModal && (
        <div className="modal-overlay" onClick={() => setShowAddModal(false)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <h3 style={{ marginTop: 0 }}>Add New Item</h3>
            
            {addError && <div style={{ color: "#ff5252", marginBottom: "1rem" }}>{addError}</div>}
            
            <form onSubmit={handleAddSubmit}>
              <div className="form-group">
                <label>SKU</label>
                <input 
                  type="text" 
                  value={addForm.sku} 
                  onChange={e => setAddForm({...addForm, sku: e.target.value})} 
                  placeholder="e.g. NEW-SKU-01"
                />
              </div>
              <div className="form-group">
                <label>Name</label>
                <input 
                  type="text" 
                  value={addForm.name} 
                  onChange={e => setAddForm({...addForm, name: e.target.value})} 
                  placeholder="e.g. New Inventory Item"
                />
              </div>
              <div className="form-group">
                <label>Category</label>
                <select 
                  value={addForm.category} 
                  onChange={e => setAddForm({...addForm, category: e.target.value})}
                  style={{ width: "100%", padding: "0.5rem", backgroundColor: "#1e1e1e", color: "white", border: "1px solid #333", borderRadius: "4px" }}
                >
                  <option value="Fuel">Fuel</option>
                  <option value="Life-Support">Life-Support</option>
                  <option value="Food">Food</option>
                  <option value="Scientific">Scientific</option>
                  <option value="Medical">Medical</option>
                </select>
              </div>
              <div style={{ display: "flex", gap: "1rem" }}>
                <div className="form-group" style={{ flex: 1 }}>
                  <label>Quantity</label>
                  <input 
                    type="number" 
                    step="any"
                    value={addForm.quantity} 
                    onChange={e => setAddForm({...addForm, quantity: e.target.value})} 
                    placeholder="0"
                  />
                </div>
                <div className="form-group" style={{ flex: 1 }}>
                  <label>Unit</label>
                  <input 
                    type="text" 
                    value={addForm.unit} 
                    onChange={e => setAddForm({...addForm, unit: e.target.value})} 
                    placeholder="e.g. kg, L"
                  />
                </div>
              </div>
              <div className="form-group">
                <label>Minimum Threshold</label>
                <input 
                  type="number" 
                  step="any"
                  value={addForm.minimum_threshold} 
                  onChange={e => setAddForm({...addForm, minimum_threshold: e.target.value})} 
                  placeholder="0"
                />
              </div>
              
              <div className="modal-actions" style={{ marginTop: "1.5rem" }}>
                <button type="button" className="btn-secondary" onClick={() => setShowAddModal(false)}>Cancel</button>
                <button type="submit" className="btn-confirm">Add Item</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
