with open("src/components/EmergencyMuster.jsx", "r", encoding="utf-8") as f:
    txt = f.read()

txt = txt.replace('className="muster-controls"', 'className="emergency-container"')
txt = txt.replace('<button className="btn-danger" onClick={handleTriggerClick}>\n               INITIATE EMERGENCY MUSTER \n            </button>', '<button className="btn-danger" onClick={handleTriggerClick}><svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20"><path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/></svg> INITIATE EMERGENCY MUSTER</button>')

# Also, wrap the button in an h3 so it looks like the design
txt = txt.replace('<button className="btn-danger"', '<h3>Emergency Protocols</h3>\n            <button className="btn-danger"')

with open("src/components/EmergencyMuster.jsx", "w", encoding="utf-8") as f:
    f.write(txt)
