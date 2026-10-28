with open("src/components/PersonnelTracker.jsx", "r", encoding="utf-8") as f:
    txt = f.read()

txt = txt.replace('className="personnel-columns"', 'className="personnel-grid"')
txt = txt.replace('className="personnel-item', 'className="personnel-card')
txt = txt.replace('<li ', '<div ')
txt = txt.replace('</li>', '</div>')
txt = txt.replace('<ul ', '<div ')
txt = txt.replace('</ul>', '</div>')
# Fix the avatar
txt = txt.replace('<div className="p-info">', '<div className="p-info"><div className="p-avatar"><svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg></div><div className="p-details">')
txt = txt.replace('</span>\n                </div>\n                <div className="p-meta">', '</span></div></div>\n                <div className="p-meta">')

# Also in the empty state of On Field Sortie
if "No personnel currently on field sortie" not in txt:
    txt = txt.replace(
        '<h3>On Field Sortie ({onField.length})</h3>\n          <div className="personnel-list">\n            {onField.map',
        '<h3>On Field Sortie ({onField.length})</h3>\n          <div className="personnel-list">\n            {onField.length === 0 && <div style={{textAlign: "center", padding: "2rem", opacity: 0.5}}><svg viewBox="0 0 24 24" fill="currentColor" width="48" height="48" style={{margin: "0 auto", display: "block"}}><path d="M14 6l-4 5-3-2-5 7h18z"/></svg><p style={{fontSize:"0.85rem", marginTop: "1rem"}}>No personnel currently on field sortie.</p></div>}\n            {onField.map'
    )
    
# Emergency muster button
txt = txt.replace('className="btn-checkin"', 'className="btn-primary"')
with open("src/components/PersonnelTracker.jsx", "w", encoding="utf-8") as f:
    f.write(txt)
print("Updated personnel tracker.")
