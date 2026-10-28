import os
import re

def strip_inline_styles(content):
    # Very naive but effective replacements for these specific files
    content = content.replace(' style={{ backgroundColor: "#2b1c28", borderColor: "#5a3a52", marginBottom: "2rem" }}', '')
    content = content.replace(' style={{ backgroundColor: "#1e2a38", borderColor: "#2d4059" }}', '')
    content = content.replace(' style={{ backgroundColor: "#15202b" }}', '')
    return content

# 1. Patch DirectivesPanel.jsx
path = "src/components/DirectivesPanel.jsx"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

content = strip_inline_styles(content)
# Acknowledge button should use standard classes and we should wrap it with permission check if needed?
# Actually HQ_DIRECTIVES covers acknowledge, and it's already an overview? 
# Wait, if they just have overview, they shouldn't acknowledge.
if "hasPermission" not in content:
    content = content.replace('import db from "../db/dexie.js";', 'import db from "../db/dexie.js";\nimport { hasPermission, PERMISSIONS } from "../permissions.js";')

content = content.replace(
    'style={{ width: "100%", backgroundColor: "#ff9800", color: "#000", border: "none", borderRadius: "4px", padding: "0.5rem", fontWeight: "bold", cursor: "pointer" }}',
    'className="btn-primary"'
)
content = content.replace(
    '{!d.acknowledged ? (',
    '{(!d.acknowledged && hasPermission(session.role, PERMISSIONS.HQ_DIRECTIVES)) ? ('
)

# Dark card replacements in Directives
content = re.sub(r'style={{[^}]*borderColor:\s*d\.acknowledged[^}]*}}', 'className={d.acknowledged ? "mission-card ack" : "mission-card unack"}', content)
content = content.replace('style={{ color: d.acknowledged ? "#aaa" : "#ffb74d" }}', 'className="directive-from"')
content = content.replace('style={{ fontSize: "0.85em", color: "#888" }}', 'className="directive-time"')
content = content.replace('style={{ margin: "0 0 1rem 0", fontSize: "1.1em", fontWeight: d.acknowledged ? "normal" : "bold" }}', 'className="directive-msg"')
content = content.replace('style={{ textAlign: "right", fontSize: "0.85em", color: "#666", fontStyle: "italic" }}', 'className="directive-ack-time"')


with open(path, "w", encoding="utf-8") as f:
    f.write(content)

# 2. Patch ExpeditionPlanning.jsx
path = "src/components/ExpeditionPlanning.jsx"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

content = strip_inline_styles(content)
if "hasPermission" not in content:
    content = content.replace('import db from "../db/dexie.js";', 'import db from "../db/dexie.js";\nimport { hasPermission, PERMISSIONS } from "../permissions.js";')

# Button class replacements
content = content.replace('<button className="btn-action" onClick={() => setIsPlanOpen(!isPlanOpen)}>', '{hasPermission(session.role, PERMISSIONS.PLANNED_EXPEDITIONS) && (<button className="btn-secondary" onClick={() => setIsPlanOpen(!isPlanOpen)}>')
content = content.replace('{isPlanOpen ? "Cancel Planning" : "Plan New Expedition"}\n        </button>', '{isPlanOpen ? "Cancel Planning" : "Plan New Expedition"}\n        </button>)}')

content = content.replace('style={{ flex: 1, backgroundColor: "#555", color: "white", border: "none", borderRadius: "4px", padding: "0.5rem" }}', 'className="btn-secondary"')
content = content.replace('style={{ flex: 1, backgroundColor: "#d32f2f", color: "white", border: "none", borderRadius: "4px", padding: "0.5rem" }}', 'className="btn-danger"')
content = content.replace('style={{ width: "100%", backgroundColor: "transparent", color: "#ff5252", border: "1px solid #ff5252", borderRadius: "4px", padding: "0.5rem" }}', 'className="btn-cancel"')
content = content.replace('style={{ borderColor: "#4caf50", borderLeftWidth: "4px" }}', 'className="mission-card"')

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

# 3. Patch AssetInventory.jsx
path = "src/components/AssetInventory.jsx"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

if "hasPermission" not in content:
    content = content.replace('import db from "../db/dexie.js";', 'import db from "../db/dexie.js";\nimport { hasPermission, PERMISSIONS } from "../permissions.js";')

content = content.replace('<button className="btn-primary" onClick={() => setShowAddModal(true)}>', '{hasPermission(session?.role, PERMISSIONS.INVENTORY_MANAGEMENT) && (<button className="btn-primary" onClick={() => setShowAddModal(true)}>')
content = content.replace('+ Add New Item\n        </button>', '+ Add New Item\n        </button>)}')

# Wrap action buttons in the table
# <td><button className="btn-consume"...> and <button className="btn-delete"...>
content = re.sub(
    r'<td className="actions-cell">([\s\S]*?)</td>',
    lambda m: f'<td className="actions-cell">{{hasPermission(session?.role, PERMISSIONS.INVENTORY_MANAGEMENT) ? <>{m.group(1)}</> : <span>View Only</span>}}</td>',
    content
)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

# 4. Patch CargoTracking.jsx
path = "src/components/CargoTracking.jsx"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

if "hasPermission" not in content:
    content = content.replace('import db from "../db/dexie.js";', 'import db from "../db/dexie.js";\nimport { hasPermission, PERMISSIONS } from "../permissions.js";')

content = content.replace('<button className="btn-primary" onClick={() => setShowModal(true)}>+ New Shipment</button>', '{hasPermission(session?.role, PERMISSIONS.CARGO_TRACKING) && <button className="btn-primary" onClick={() => setShowModal(true)}>+ New Shipment</button>}')

content = re.sub(
    r'<td className="actions-cell">([\s\S]*?)</td>',
    lambda m: f'<td className="actions-cell">{{hasPermission(session?.role, PERMISSIONS.CARGO_RECEIVE) ? <>{m.group(1)}</> : <span>Restricted</span>}}</td>',
    content
)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Patch complete")
