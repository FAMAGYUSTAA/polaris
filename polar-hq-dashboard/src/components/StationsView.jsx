import React, { useState, useEffect } from "react";
import FreshnessIndicator from "./FreshnessIndicator.jsx";

export default function StationsView() {
  const stations = ["BHARATI", "MAITRI", "HIMADRI"];

  return (
    <div className="hq-main" style={{ gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))" }}>
      {stations.map(st => (
        <div key={st} className="panel">
          <div className="panel-header">
            <h2>{st} Station</h2>
          </div>
          <div className="panel-body">
            <div style={{ marginBottom: "1rem" }}>
              <FreshnessIndicator stationId={st} />
            </div>
            <div style={{ fontSize: "0.9rem", color: "var(--text-muted)", lineHeight: 1.6 }}>
              <strong>Location: </strong> 
              {st === "BHARATI" ? "69.41° S, 76.23° E" : st === "MAITRI" ? "70.76° S, 11.73° E" : "78.92° N, 11.93° E"}<br/>
              <strong>Status: </strong> Active
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
