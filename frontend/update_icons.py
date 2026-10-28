import re

def update_panel_advanced(filepath, title, icon_svg, icon_color_class=""):
    with open(filepath, 'r', encoding='utf-8') as f:
        txt = f.read()

    # The header usually starts with <h2> or <div className="tracker-header">...<h2>
    # We want to replace it with:
    # <div className="tracker-header">
    #   <h2><div className="icon-box {icon_color_class}">{icon_svg}</div> {title}</h2>
    #   {action_buttons}
    # </div>
    
    # Actually, in AssetInventory it's:
    # <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
    #   <h2><svg...> Asset Inventory</h2>
    #   {button}
    # </div>
    # Let's standardize it:
    
    txt = txt.replace('className="inventory-panel"', 'className="tracker-panel"')
    txt = txt.replace('className="emergency-panel"', 'className="tracker-panel emergency-panel"')
    
    # We will just do manual replace for the <h2> tag
    h2_regex = r'<h2>\s*<svg[\s\S]*?</svg>\s*(.*?)\s*</h2>'
    
    def repl(m):
        return f'<h2><div className="icon-box {icon_color_class}">{icon_svg}</div> {m.group(1)}</h2>'
        
    txt = re.sub(h2_regex, repl, txt)
    
    # Also standardize the header wrapper if it's not tracker-header
    txt = txt.replace('<div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>', '<div className="tracker-header">')
    txt = txt.replace('<div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>', '<div className="tracker-header">')
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(txt)

# Cargo Tracking
update_panel_advanced(
    "src/components/CargoTracking.jsx",
    'Cargo Tracking',
    '<svg viewBox="0 0 24 24" fill="currentColor" width="24" height="24"><path d="M21 16.5c0 .38-.21.71-.53.88l-7.9 4.44c-.16.12-.36.18-.57.18s-.41-.06-.57-.18l-7.9-4.44A.991.991 0 0 1 3 16.5v-9c0-.38.21-.71.53-.88l7.9-4.44c.16-.12.36-.18.57-.18s.41.06.57.18l7.9 4.44c.32.17.53.5.53.88v9zM12 4.15L6.04 7.5 12 10.85l5.96-3.35L12 4.15z"/></svg>'
)

# Asset Inventory
update_panel_advanced(
    "src/components/AssetInventory.jsx",
    'Asset Inventory',
    '<svg viewBox="0 0 24 24" fill="currentColor" width="24" height="24"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/></svg>'
)

# Personnel Tracker
update_panel_advanced(
    "src/components/PersonnelTracker.jsx",
    'Whiteout Safety Board',
    '<svg viewBox="0 0 24 24" fill="currentColor" width="24" height="24"><path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/></svg>'
)

# Expedition Planning
update_panel_advanced(
    "src/components/ExpeditionPlanning.jsx",
    'Upcoming Expeditions (Planned)',
    '<svg viewBox="0 0 24 24" fill="currentColor" width="24" height="24"><path d="M14 6m-3 0a3 3 0 1 0 6 0 3 3 0 1 0 -6 0M1 21h22L15 10 10 16 7 12 1 21z"/></svg>'
)

# Emergency Muster
update_panel_advanced(
    "src/components/EmergencyMuster.jsx",
    'Emergency Protocols',
    '<svg viewBox="0 0 24 24" fill="currentColor" width="24" height="24"><path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/></svg>',
    'danger'
)

# Sneakernet Export
update_panel_advanced(
    "src/components/SneakernetExport.jsx",
    'Offline Export',
    '<svg viewBox="0 0 24 24" fill="currentColor" width="24" height="24"><path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/></svg>'
)

print("Icons and headers updated via regex.")
