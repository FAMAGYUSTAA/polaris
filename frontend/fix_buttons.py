import re

def fix_buttons(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        txt = f.read()

    txt = txt.replace('className="btn-sync"', 'className="btn-secondary"')
    
    # CargoTracking New Shipment button
    if "CargoTracking" in filepath:
        txt = txt.replace(
            '<button \n            className="btn-secondary" \n            onClick={() => setShowModal(true)}\n            \n          >\n            + New Shipment\n          </button>',
            '{hasPermission(session.role, PERMISSIONS.CARGO_RECEIVE) && (<button className="btn-primary" onClick={() => setShowModal(true)}>+ New Shipment</button>)}'
        )
        
        # CargoTracking rows styling
        txt = txt.replace('className="mission-grid"', 'className="cargo-section"')
        txt = txt.replace('className="mission-card"', 'className="cargo-row"')
        
    if "AssetInventory" in filepath:
        txt = txt.replace('className="btn-consume"', 'className="btn-secondary"')
        txt = txt.replace('className="btn-cancel"', 'className="btn-secondary"')

    if "PersonnelTracker" in filepath:
        txt = txt.replace('className="btn-action"', 'className="btn-secondary"')
        
    if "EmergencyMuster" in filepath:
        txt = txt.replace('className="btn-emergency"', 'className="btn-danger"')
        
    if "SneakernetExport" in filepath:
        txt = txt.replace('className="btn-action"', 'className="btn-primary"')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(txt)

for f in ["src/components/CargoTracking.jsx", "src/components/AssetInventory.jsx", "src/components/PersonnelTracker.jsx", "src/components/ExpeditionPlanning.jsx", "src/components/EmergencyMuster.jsx", "src/components/SneakernetExport.jsx"]:
    fix_buttons(f)
print("Buttons fixed.")
