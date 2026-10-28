import re

with open('frontend/src/components/EmergencyMuster.jsx', 'r', encoding='utf-8') as f:
    code = f.read()

# Add permissions
code = code.replace(
    'import db from "../db/dexie.js";',
    'import db from "../db/dexie.js";\nimport { hasPermission, PERMISSIONS } from "../permissions.js";'
)

# Add session to props
code = code.replace(
    'export default function EmergencyMuster({ stationId }) {',
    'export default function EmergencyMuster({ stationId, session }) {'
)

# Modify the render
button_orig = """      <div className="muster-controls">
        {!isConfirming ? (
          <button className="btn-muster" onClick={handleTriggerClick}>
            ⚠️ INITIATE EMERGENCY MUSTER ⚠️
          </button>
        ) : ("""

button_new = """      <div className="muster-controls">
        {hasPermission(session.role, PERMISSIONS.EMERGENCY_MUSTER) ? (
          !isConfirming ? (
            <button className="btn-muster" onClick={handleTriggerClick}>
              ⚠️ INITIATE EMERGENCY MUSTER ⚠️
            </button>
          ) : (
            <div className="muster-confirm-box">
              <p><strong>Are you sure?</strong> This will log a station-wide emergency event.</p>
              <div className="muster-actions">
                <button className="btn-muster-cancel" onClick={handleCancel}>Cancel</button>
                <button className="btn-muster-confirm" onClick={handleConfirm}>CONFIRM MUSTER</button>
              </div>
            </div>
          )
        ) : (
          <div className="muster-confirm-box" style={{ backgroundColor: "#2d3748", borderLeftColor: "#4fd1c5" }}>
            <p><strong>Medical Officer View:</strong> Awaiting station muster status. Medical emergency reporting and casualty tracking will appear here during active muster.</p>
          </div>
        )}
      </div>"""

# Wait, `!isConfirming ? (...) : (...)` goes until the end of the `muster-controls` div!
# I need to match it properly.

code_to_replace = """      <div className="muster-controls">
        {!isConfirming ? (
          <button className="btn-muster" onClick={handleTriggerClick}>
            ⚠️ INITIATE EMERGENCY MUSTER ⚠️
          </button>
        ) : (
          <div className="muster-confirm-box">
            <p><strong>Are you sure?</strong> This will log a station-wide emergency event.</p>
            <div className="muster-actions">
              <button className="btn-muster-cancel" onClick={handleCancel}>Cancel</button>
              <button className="btn-muster-confirm" onClick={handleConfirm}>CONFIRM MUSTER</button>
            </div>
          </div>
        )}
      </div>"""

code = code.replace(code_to_replace, button_new)

with open('frontend/src/components/EmergencyMuster.jsx', 'w', encoding='utf-8') as f:
    f.write(code)
