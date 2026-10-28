import re
with open('src/components/AssetInventory.jsx', 'r', encoding='utf-8') as f:
    txt = f.read()

# AssetInventory item-actions
txt = re.sub(
    r'(<div className="item-actions"[\s\S]*?</div>\s*</div>)',
    r'{hasPermission(session?.role, PERMISSIONS.INVENTORY_MANAGEMENT) && (\1)}',
    txt
)

# And replace <td className="actions-cell"> changes made by mistake earlier if any
txt = txt.replace('{hasPermission(session?.role, PERMISSIONS.INVENTORY_MANAGEMENT) ? <><button className="btn-consume"', '<button className="btn-consume"')
txt = txt.replace('</button></> : <span>View Only</span>}', '</button>')

with open('src/components/AssetInventory.jsx', 'w', encoding='utf-8') as f:
    f.write(txt)
