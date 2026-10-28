import re

with open('frontend/src/components/PersonnelTracker.jsx', 'r', encoding='utf-8') as f:
    code = f.read()

# Add permissions
code = code.replace(
    'import db from "../db/dexie.js";',
    'import db from "../db/dexie.js";\nimport { hasPermission, PERMISSIONS, ROLES } from "../permissions.js";'
)

# Add session to props
code = code.replace(
    'export default function PersonnelTracker({ stationId }) {',
    'export default function PersonnelTracker({ stationId, session }) {'
)

# Replace "New Field Checkout" button rendering
checkout_btn_orig = """      <div className="tracker-header">
        <h2>Whiteout Safety Board</h2>
        <button className="btn-action" onClick={() => setIsCheckoutOpen(!isCheckoutOpen)}>
          {isCheckoutOpen ? "Cancel Checkout" : "New Field Checkout"}
        </button>
      </div>"""

checkout_btn_new = """      <div className="tracker-header">
        <h2>Whiteout Safety Board</h2>
        {hasPermission(session.role, PERMISSIONS.OWN_MISSION_CHECKOUT_CHECKIN) && (
          <button className="btn-action" onClick={() => setIsCheckoutOpen(!isCheckoutOpen)}>
            {isCheckoutOpen ? "Cancel Checkout" : "New Field Checkout"}
          </button>
        )}
      </div>"""

code = code.replace(checkout_btn_orig, checkout_btn_new)

# Replace the checkin button rendering
checkin_orig = """                  <button className="btn-checkin" onClick={() => handleCheckin(m)}>Check In Mission</button>"""

checkin_new = """                  { (hasPermission(session.role, PERMISSIONS.FIELD_MISSION_MANAGEMENT) || (hasPermission(session.role, PERMISSIONS.OWN_MISSION_CHECKOUT_CHECKIN) && (m.team_lead === session.username || (m.members && m.members.includes(session.username))))) && (
                    <button className="btn-checkin" onClick={() => handleCheckin(m)}>Check In Mission</button>
                  )}"""

code = code.replace(checkin_orig, checkin_new)


# Restrict checkboxes in personnel list for Field Team Member
checkbox_orig = """                {isCheckoutOpen && (
                  <input 
                    type="checkbox" 
                    checked={selectedPersonnelIds.has(p.id)}
                    onChange={() => toggleSelection(p.id)}
                  />
                )}"""

checkbox_new = """                {isCheckoutOpen && (
                  <input 
                    type="checkbox" 
                    checked={selectedPersonnelIds.has(p.id)}
                    onChange={() => toggleSelection(p.id)}
                    disabled={session.role === ROLES.FIELD_TEAM_MEMBER && p.full_name !== session.username}
                  />
                )}"""

code = code.replace(checkbox_orig, checkbox_new)

with open('frontend/src/components/PersonnelTracker.jsx', 'w', encoding='utf-8') as f:
    f.write(code)
