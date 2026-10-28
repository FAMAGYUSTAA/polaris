import os

path = "src/components/EmergencyMuster.jsx"
with open(path, "r", encoding="utf-8") as f:
    txt = f.read()

txt = txt.replace(' style={{ backgroundColor: "#2d3748", borderLeftColor: "#4fd1c5" }}', '')
txt = txt.replace('className="btn-muster-confirm"', 'className="btn-danger"')
txt = txt.replace('className="btn-muster"', 'className="btn-danger"')

with open(path, "w", encoding="utf-8") as f:
    f.write(txt)
