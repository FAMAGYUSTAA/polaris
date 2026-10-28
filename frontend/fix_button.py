import re

path = 'src/components/AssetInventory.jsx'
with open(path, 'r', encoding='utf-8') as f:
    txt = f.read()

txt = txt.replace('</button>\n)}', '</button>')
txt = txt.replace('</button>\n)', '</button>')

# Now wrap it properly
txt = re.sub(
    r'(<button\s*onClick={\(\) => setShowAddModal\(true\)}[^>]*>[\s\S]*?</button>)',
    r'{hasPermission(session?.role, PERMISSIONS.INVENTORY_MANAGEMENT) && (\1)}',
    txt
)

# Wait, the button has inline style style={{ backgroundColor: "#1976d2", color: "white", padding: "0.5rem 1rem", border: "none", borderRadius: "4px", cursor: "pointer" }}
# I should also replace it with className="btn-primary"
txt = txt.replace('style={{ backgroundColor: "#1976d2", color: "white", padding: "0.5rem 1rem", border: "none", borderRadius: "4px", cursor: "pointer" }}', 'className="btn-primary"')

with open(path, 'w', encoding='utf-8') as f:
    f.write(txt)
