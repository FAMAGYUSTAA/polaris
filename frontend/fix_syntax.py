import re

# Fix AssetInventory.jsx
with open('src/components/AssetInventory.jsx', 'r', encoding='utf-8') as f:
    txt = f.read()

# We know we messed up item-actions, let's just find `renderItemCard` and fix the return explicitly.
# Or better, we can restore it from git if we could.
# Let's write a targeted replace for the messed up part.
# The messed up part starts at `<div className="item-actions"` and goes to the end of `renderItemCard`.

match_str = r'{hasPermission\(session\?\.role, PERMISSIONS\.INVENTORY_MANAGEMENT\) && \(<div className="item-actions"[\s\S]*?</div>\}[\s\S]*?</div>'

replacement = """<div className="item-actions" style={{ display: "flex", gap: "0.5rem", marginTop: "1rem" }}>
          {hasPermission(session?.role, PERMISSIONS.INVENTORY_MANAGEMENT) && (
            <>
              <button 
                className="btn-consume"
                onClick={() => setConsumeModalItem(item)}
                style={{ flex: 1 }}
              >
                Consume
              </button>
              
              {deletingId === item.id ? (
                <div style={{ display: "flex", gap: "0.5rem", flex: 1 }}>
                  <button 
                    onClick={() => setDeletingId(null)}
                    className="btn-cancel"
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
                  className="btn-cancel"
                >
                  Delete
                </button>
              )}
            </>
          )}
        </div>
      </div>
"""
txt = re.sub(match_str, replacement, txt)
with open('src/components/AssetInventory.jsx', 'w', encoding='utf-8') as f:
    f.write(txt)

# Fix ExpeditionPlanning.jsx duplicate className
with open('src/components/ExpeditionPlanning.jsx', 'r', encoding='utf-8') as f:
    txt = f.read()
txt = txt.replace('className="mission-card" className="mission-card"', 'className="mission-card"')
with open('src/components/ExpeditionPlanning.jsx', 'w', encoding='utf-8') as f:
    f.write(txt)

# Fix DirectivesPanel.jsx duplicate className
with open('src/components/DirectivesPanel.jsx', 'r', encoding='utf-8') as f:
    txt = f.read()
txt = txt.replace('className="mission-card" \n                className={d.acknowledged ? "mission-card ack" : "mission-card unack"}', 'className={d.acknowledged ? "mission-card ack" : "mission-card unack"}')
txt = txt.replace('className="mission-card" \n                  className={d.acknowledged ? "mission-card ack" : "mission-card unack"}', 'className={d.acknowledged ? "mission-card ack" : "mission-card unack"}')
with open('src/components/DirectivesPanel.jsx', 'w', encoding='utf-8') as f:
    f.write(txt)

print("Fixes applied.")
