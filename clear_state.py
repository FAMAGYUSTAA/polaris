import re

files = {
    "polar-hq-dashboard/src/components/ActiveMissionPanel.jsx": "setActiveMissions([]); setPersonnelMap({});",
    "polar-hq-dashboard/src/components/CargoApprovalPanel.jsx": "setShipments([]);",
    "polar-hq-dashboard/src/components/DirectiveComposer.jsx": "setDirectives([]);",
    "polar-hq-dashboard/src/components/FreshnessIndicator.jsx": "setStatus(null);",
    "polar-hq-dashboard/src/components/MusterAlerts.jsx": "setAlerts([]);",
    "polar-hq-dashboard/src/components/PlannedMissionsPanel.jsx": "setExpeditions([]); setPersonnelMap({});"
}

for filepath, clear_stmt in files.items():
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    # We want to insert the clear_stmt right after `useEffect(() => {`
    content = content.replace("useEffect(() => {\n", f"useEffect(() => {{\n    {clear_stmt}\n")
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

