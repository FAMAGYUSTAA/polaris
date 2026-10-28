import os

path = "src/components/HeaderStatus.jsx"
with open(path, "r", encoding="utf-8") as f:
    txt = f.read()

placeholder = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
            <circle cx="12" cy="12" r="10" />
            <path d="M2 12h20 M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
          </svg>"""

logo = '<img src="/ncpor-circular-logo.jpg" alt="NCPOR Logo" style={{width: "100%", height: "100%", borderRadius: "50%"}} />'

txt = txt.replace(placeholder, logo)

with open(path, "w", encoding="utf-8") as f:
    f.write(txt)
