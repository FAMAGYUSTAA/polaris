import React, { useState } from "react";
import { exportSneakernetSnapshot } from "../services/syncService.js";
import { getOutboxPendingCount } from "../db/dexie.js";

export default function SneakernetExport({ stationId }) {
  const [isExporting, setIsExporting] = useState(false);
  const [exportResult, setExportResult] = useState(null);

  const handleExport = async () => {
    try {
      setIsExporting(true);
      setExportResult(null);

      const pendingCount = await getOutboxPendingCount();
      if (pendingCount === 0) {
        setExportResult({ type: "info", msg: "No pending events to export." });
        return;
      }

      const bundle = await exportSneakernetSnapshot(stationId);
      
      const filename = `sneakernet-export-${stationId}-${bundle.exported_at.replace(/[:.]/g, "-")}.json`;
      setExportResult({ 
        type: "success", 
        msg: `Exported ${bundle.events.length} pending events to ${filename} - transfer this file via USB for physical transport.` 
      });

    } catch (err) {
      console.error("[SneakernetExport] Export failed:", err);
      setExportResult({ type: "error", msg: `Export failed: ${err.message}` });
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div className="tracker-panel">
      <div className="tracker-header">
        <h2><div className="icon-box"><svg viewBox="0 0 24 24" fill="currentColor" width="24" height="24"><path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/></svg></div> Offline Export</h2>
      </div>
      <p style={{marginBottom: "1rem"}}>
        If satellite connectivity is unavailable for an extended period, export pending data to a secure USB drive for physical transfer.
      </p>
      
      <button 
        className="btn-primary" 
        onClick={handleExport}
        disabled={isExporting}
      >
        <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20" style={{marginRight:"8px"}}><path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/></svg>
        {isExporting ? "Generating..." : "Export Encrypted Snapshot (Sneakernet)"}
      </button>

      {exportResult && (
        <div style={{marginTop: "1rem", color: exportResult.type === "error" ? "red" : "#16A34A", fontWeight: "600"}}>
          {exportResult.msg}
        </div>
      )}
    </div>
  );
}
