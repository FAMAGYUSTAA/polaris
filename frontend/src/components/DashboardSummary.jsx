import React, { useState, useEffect } from "react";
import db from "../db/dexie.js";
import { hasPermission, PERMISSIONS } from "../permissions.js";

export default function DashboardSummary({ session }) {
  const stationId = session.station_id;
  const role = session.role;

  const [stats, setStats] = useState({
    shipments: { total: 0, inbound: 0, outbound: 0 },
    inventory: { total: 0, lowStock: 0 },
    personnel: { total: 0, incoming: 0, outgoing: 0 },
    directives: { total: 0, highPriority: 0 }
  });

  useEffect(() => {
    if (!stationId) return;

    const fetchStats = async () => {
      let shipmentsData = { total: 0, inbound: 0, outbound: 0 };
      let inventoryData = { total: 0, lowStock: 0 };
      let personnelData = { total: 0, incoming: 0, outgoing: 0 };
      let directivesData = { total: 0, highPriority: 0 };

      try {
        if (hasPermission(role, PERMISSIONS.CARGO_TRACKING) && db.cargoShipments) {
          const items = await db.cargoShipments.filter(i => i.station_id === stationId && i.status !== "DELIVERED").toArray();
          shipmentsData.total = items.length;
          shipmentsData.inbound = items.filter(i => i.origin !== stationId).length;
          shipmentsData.outbound = items.filter(i => i.origin === stationId).length;
        }

        if (hasPermission(role, PERMISSIONS.INVENTORY_MANAGEMENT) && db.inventory) {
          const items = await db.inventory.toArray(); // Inventory usually global to station in DB structure
          inventoryData.total = items.length;
          inventoryData.lowStock = items.filter(i => i.quantity <= i.minimum_threshold).length;
        }

        if (hasPermission(role, PERMISSIONS.PERSONNEL_MANAGEMENT) && db.personnel) {
          const items = await db.personnel.toArray(); // Filtered by syncService anyway
          personnelData.total = items.filter(i => i.status === "ON_STATION").length;
          // Placeholder for incoming/outgoing if tracking not implemented in schema
        }

        if (hasPermission(role, PERMISSIONS.HQ_DIRECTIVES) && db.directives) {
          const items = await db.directives.filter(i => !i.acknowledged).toArray();
          directivesData.total = items.length;
          // Priority not in schema yet, default to all unack
          directivesData.highPriority = items.length;
        }
      } catch (err) {
        console.error("[DashboardSummary] Error fetching KPI data:", err);
      }

      setStats({
        shipments: shipmentsData,
        inventory: inventoryData,
        personnel: personnelData,
        directives: directivesData
      });
    };

    fetchStats();
    // Refresh periodically
    const interval = setInterval(fetchStats, 10000);
    return () => clearInterval(interval);
  }, [stationId, role]);

  return (
    <div className="dashboard-summary">
      {hasPermission(role, PERMISSIONS.CARGO_TRACKING) && (
        <div className="kpi-card">
          <div className="kpi-icon kpi-shipments">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M20,8h-3V4c0-1.1-0.9-2-2-2H9C7.9,2,7,2.9,7,4v4H4c-1.1,0-2,0.9-2,2v10h20V10C22,8.9,21.1,8,20,8z M9,4h6v4H9V4z"/>
            </svg>
          </div>
          <div className="kpi-content">
            <h3>Active Shipments</h3>
            <div className="kpi-value">{stats.shipments.total}</div>
            <div className="kpi-meta">
              <span>{stats.shipments.inbound} inbound</span> • <span>{stats.shipments.outbound} outbound</span>
            </div>
          </div>
        </div>
      )}

      {hasPermission(role, PERMISSIONS.INVENTORY_MANAGEMENT) && (
        <div className="kpi-card">
          <div className="kpi-icon kpi-inventory">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
            </svg>
          </div>
          <div className="kpi-content">
            <h3>Inventory Items</h3>
            <div className="kpi-value">{stats.inventory.total}</div>
            <div className="kpi-meta">
              <span className="kpi-warning">{stats.inventory.lowStock} low stock</span>
            </div>
          </div>
        </div>
      )}

      {hasPermission(role, PERMISSIONS.PERSONNEL_MANAGEMENT) && (
        <div className="kpi-card">
          <div className="kpi-icon kpi-personnel">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/>
            </svg>
          </div>
          <div className="kpi-content">
            <h3>Personnel On Station</h3>
            <div className="kpi-value">{stats.personnel.total}</div>
            <div className="kpi-meta">
              <span>{stats.personnel.incoming} incoming</span> • <span>{stats.personnel.outgoing} outgoing</span>
            </div>
          </div>
        </div>
      )}

      {hasPermission(role, PERMISSIONS.HQ_DIRECTIVES) && (
        <div className="kpi-card">
          <div className="kpi-icon kpi-directives">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/>
            </svg>
          </div>
          <div className="kpi-content">
            <h3>Open HQ Directives</h3>
            <div className="kpi-value">{stats.directives.total}</div>
            <div className="kpi-meta">
              <span className="kpi-critical">{stats.directives.highPriority} unacknowledged</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
