import os
import re

components_dir = "src/components"

icons = {
    "CargoTracking.jsx": '<svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20" style={{marginRight: "8px"}}><path d="M20,8h-3V4c0-1.1-0.9-2-2-2H9C7.9,2,7,2.9,7,4v4H4c-1.1,0-2,0.9-2,2v10h20V10C22,8.9,21.1,8,20,8z M9,4h6v4H9V4z"/></svg>',
    "AssetInventory.jsx": '<svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20" style={{marginRight: "8px"}}><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/></svg>',
    "PersonnelTracker.jsx": '<svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20" style={{marginRight: "8px"}}><path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/></svg>',
    "ExpeditionPlanning.jsx": '<svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20" style={{marginRight: "8px"}}><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 9.36l-7.1 7.1a1 1 0 0 1-1.4 0l-2.83-2.83a1 1 0 0 1 0-1.4l7.1-7.1a6 6 0 0 1 9.36-7.94z"/></svg>',
    "DirectivesPanel.jsx": '<svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20" style={{marginRight: "8px"}}><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/></svg>',
    "EmergencyMuster.jsx": '<svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20" style={{marginRight: "8px"}}><path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/></svg>',
    "SneakernetExport.jsx": '<svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20" style={{marginRight: "8px"}}><path d="M21 12a9 9 0 1 1-9-9c2.52 0 4.93 1 6.74 2.74L21 8 M21 3v5h-5"/></svg>',
}

for comp, icon in icons.items():
    path = os.path.join(components_dir, comp)
    if not os.path.exists(path):
        continue
    
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # If the component already uses <svg, skip or replace the h2 logic
    # Find <h2>...</h2> and insert the icon at the beginning of the text
    # e.g. <h2>Cargo Tracking</h2> -> <h2><svg... /> Cargo Tracking</h2>
    
    # We can do this safely using regex
    def replacer(m):
        inner = m.group(1)
        # Strip existing emojis or SVGs if any (very naively)
        # Just simple strip
        inner = re.sub(r'<svg.*?</svg>', '', inner)
        # Strip emojis
        inner = re.sub(r'[\U00010000-\U0010ffff]', '', inner).strip()
        
        return f"<h2>{icon} {inner}</h2>"

    new_content = re.sub(r'<h2>(.*?)</h2>', replacer, content)
    
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)

print("Headers updated successfully.")
