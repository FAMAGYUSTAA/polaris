import re

with open('frontend/src/components/ExpeditionPlanning.jsx', 'r', encoding='utf-8') as f:
    code = f.read()

# Add permissions import
code = code.replace(
    'import db from "../db/dexie.js";',
    'import db from "../db/dexie.js";\nimport { hasPermission, PERMISSIONS } from "../permissions.js";'
)

# Add session to props
code = code.replace(
    'export default function ExpeditionPlanning({ stationId }) {',
    'export default function ExpeditionPlanning({ stationId, session }) {'
)

# Hide Cancel Expedition block
cancel_block_orig = """                  {cancellingId === m.id ? (
                    <div style={{ display: "flex", gap: "0.5rem" }}>
                      <button 
                        onClick={() => setCancellingId(null)}
                        style={{ flex: 1, backgroundColor: "#555", color: "white", border: "none", borderRadius: "4px", padding: "0.5rem" }}
                      >
                        Abort Cancel
                      </button>
                      <button 
                        onClick={() => handleConfirmCancel(m)}
                        style={{ flex: 1, backgroundColor: "#d32f2f", color: "white", border: "none", borderRadius: "4px", padding: "0.5rem" }}
                      >
                        Confirm Cancel
                      </button>
                    </div>
                  ) : (
                    <button 
                      onClick={() => setCancellingId(m.id)}
                      style={{ width: "100%", backgroundColor: "transparent", color: "#ff5252", border: "1px solid #ff5252", borderRadius: "4px", padding: "0.5rem" }}
                    >
                      Cancel Expedition
                    </button>
                  )}"""

cancel_block_new = """                  {hasPermission(session.role, PERMISSIONS.FIELD_MISSION_MANAGEMENT) && (
                    cancellingId === m.id ? (
                      <div style={{ display: "flex", gap: "0.5rem" }}>
                        <button 
                          onClick={() => setCancellingId(null)}
                          style={{ flex: 1, backgroundColor: "#555", color: "white", border: "none", borderRadius: "4px", padding: "0.5rem" }}
                        >
                          Abort Cancel
                        </button>
                        <button 
                          onClick={() => handleConfirmCancel(m)}
                          style={{ flex: 1, backgroundColor: "#d32f2f", color: "white", border: "none", borderRadius: "4px", padding: "0.5rem" }}
                        >
                          Confirm Cancel
                        </button>
                      </div>
                    ) : (
                      <button 
                        onClick={() => setCancellingId(m.id)}
                        style={{ width: "100%", backgroundColor: "transparent", color: "#ff5252", border: "1px solid #ff5252", borderRadius: "4px", padding: "0.5rem" }}
                      >
                        Cancel Expedition
                      </button>
                    )
                  )}"""

code = code.replace(cancel_block_orig, cancel_block_new)

with open('frontend/src/components/ExpeditionPlanning.jsx', 'w', encoding='utf-8') as f:
    f.write(code)
