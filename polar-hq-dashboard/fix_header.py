import re

with open('src/App.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

new_header = """      <header className="ministry-header" style={{ padding: "0.75rem 2rem", display: "flex", justifyContent: "space-between", alignItems: "center", backgroundColor: "var(--bg-white)", borderBottom: "1.5px solid var(--border-color)" }}>
        
        {/* LEFT: Government Branding */}
        <div className="logos left-logos" style={{ display: "flex", alignItems: "center", gap: "0.75rem", flex: 1 }}>
          <img src="/emblem-dark.png" alt="Emblem" style={{ height: "50px" }} onError={(e) => e.target.style.display='none'} />
          <div style={{ lineHeight: 1.2 }}>
            <div style={{ fontWeight: "700", color: "var(--text-primary)", fontSize: "0.95rem" }}>पृथ्वी विज्ञान मंत्रालय</div>
            <div style={{ fontWeight: "700", color: "var(--text-primary)", fontSize: "0.95rem" }}>Ministry of Earth Sciences</div>
            <div style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>Government of India</div>
          </div>
        </div>

        {/* CENTER: Logo + NCPOR Heading */}
        <div className="logos center-logos" style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "1rem", flex: 2 }}>
          <img src="/ncpor-circular-logo.jpg" alt="NCPOR Logo" style={{ height: "65px", borderRadius: "50%", objectFit: "contain" }} onError={(e) => e.target.style.display='none'} />
          <div style={{ textAlign: "center", lineHeight: 1.2 }}>
            <div style={{ fontWeight: "800", fontSize: "1.2rem", letterSpacing: "0.5px", color: "var(--ncpor-navy)" }}>NATIONAL CENTRE FOR POLAR AND OCEAN RESEARCH</div>
            <div style={{ fontWeight: "700", color: "var(--ncpor-navy)", fontSize: "0.95rem", marginTop: "0.15rem" }}>Earth System Sciences Organization</div>
            <div style={{ fontStyle: "italic", color: "var(--text-muted)", fontSize: "0.9rem", marginTop: "0.15rem" }}>Science for a Sustainable Planet</div>
          </div>
        </div>

        {/* RIGHT: NCPOR Hindi/English Branding */}
        <div className="logos right-logos" style={{ display: "flex", flexDirection: "column", justifyContent: "center", textAlign: "right", gap: "0.15rem", lineHeight: 1.2, flex: 1 }}>
          <div style={{ fontWeight: "700", color: "var(--text-primary)", fontSize: "0.95rem" }}>राष्ट्रीय ध्रुवीय एवं समुद्री अनुसंधान केंद्र</div>
          <div style={{ fontWeight: "700", color: "var(--text-primary)", fontSize: "0.95rem" }}>National Centre for Polar and Ocean Research</div>
          <div style={{ color: "var(--text-muted)", fontSize: "0.8rem" }}>(An Autonomous Institution under MoES, Govt. of India)</div>
        </div>
        
      </header>"""

content = re.sub(r'<header className="ministry-header".*?</header>', new_header, content, flags=re.DOTALL)

with open('src/App.jsx', 'w', encoding='utf-8') as f:
    f.write(content)
