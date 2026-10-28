with open("src/components/EmergencyMuster.jsx", "r", encoding="utf-8") as f:
    txt = f.read()

txt = txt.replace('<h3>Emergency Protocols</h3>\n            <button className="btn-danger"', '<>\n              <h3>Emergency Protocols</h3>\n              <button className="btn-danger"')
txt = txt.replace('INITIATE EMERGENCY MUSTER</button>\n          ) : (', 'INITIATE EMERGENCY MUSTER</button>\n            </>\n          ) : (')

with open("src/components/EmergencyMuster.jsx", "w", encoding="utf-8") as f:
    f.write(txt)
