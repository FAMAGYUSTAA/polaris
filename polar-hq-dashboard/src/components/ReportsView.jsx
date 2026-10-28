import React, { useState, useEffect } from "react";

export default function ReportsView({ stationId }) {
  const [data, setData] = useState({ inventory: 0, cargo: 0, personnel: 0 });

  useEffect(() => {
    const fetchData = async () => {
      try {
        const invRes = await fetch(`/api/inventory?station_id=${stationId}`);
        const invData = invRes.ok ? await invRes.json() : [];
        
        const cargoRes = await fetch(`/api/cargo?station_id=${stationId}`);
        const cargoData = cargoRes.ok ? await cargoRes.json() : [];
        
        const perRes = await fetch(`/api/personnel?station_id=${stationId}`);
        const perData = perRes.ok ? await perRes.json() : { personnel: [] };

        setData({
          inventory: invData.length,
          cargo: cargoData.length,
          personnel: perData.personnel ? perData.personnel.length : 0
        });
      } catch (err) {
        console.error("Failed to fetch report data", err);
      }
    };
    fetchData();
  }, [stationId]);

  return (
    <div className="hq-main" style={{ gridTemplateColumns: "1fr" }}>
      <div className="panel">
        <div className="panel-header">
          <h2>Summary Report - {stationId}</h2>
        </div>
        <div className="panel-body">
          <p>This is a high-level summary of the {stationId} station resources.</p>
          <ul style={{ lineHeight: 1.8 }}>
            <li><strong>Total Inventory Logged:</strong> {data.inventory} items</li>
            <li><strong>Total Cargo Shipments Logged:</strong> {data.cargo} shipments</li>
            <li><strong>Total Personnel:</strong> {data.personnel} members</li>
          </ul>
          <p style={{ color: "var(--text-muted)", fontSize: "0.85rem", marginTop: "2rem" }}>
            * Detailed reporting backend is not currently available.
          </p>
        </div>
      </div>
    </div>
  );
}
