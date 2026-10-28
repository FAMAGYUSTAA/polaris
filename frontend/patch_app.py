import re

with open('frontend/src/App.jsx', 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace(
    'import { restoreSession, logout as authLogout, getCurrentSession } from "./services/authService.js";',
    'import { restoreSession, logout as authLogout, getCurrentSession } from "./services/authService.js";\nimport { hasPermission, hasAnyPermission, PERMISSIONS } from "./permissions.js";'
)

# Replace components block
components_block = """        {hasPermission(session.role, PERMISSIONS.HQ_DIRECTIVES) && <DirectivesPanel stationId={session.station_id} session={session} />}
        {hasPermission(session.role, PERMISSIONS.CARGO_TRACKING) && <CargoTracking stationId={session.station_id} session={session} />}
        {hasPermission(session.role, PERMISSIONS.INVENTORY_MANAGEMENT) && <AssetInventory stationId={session.station_id} session={session} />}
        {hasAnyPermission(session.role, [PERMISSIONS.PERSONNEL_MANAGEMENT, PERMISSIONS.OWN_MISSION_CHECKOUT_CHECKIN, PERMISSIONS.EMERGENCY_STATUS_REPORTING]) && <PersonnelTracker stationId={session.station_id} session={session} />}
        {hasAnyPermission(session.role, [PERMISSIONS.PLANNED_EXPEDITIONS, PERMISSIONS.FIELD_MISSION_MANAGEMENT]) && <ExpeditionPlanning stationId={session.station_id} session={session} />}
        {hasAnyPermission(session.role, [PERMISSIONS.EMERGENCY_MUSTER, PERMISSIONS.EMERGENCY_MUSTER_MEDICAL]) && <EmergencyMuster stationId={session.station_id} session={session} />}
        {hasPermission(session.role, PERMISSIONS.SNEAKERNET) && <SneakernetExport stationId={session.station_id} session={session} />}"""

code = re.sub(r'<DirectivesPanel.*?/>.*?<SneakernetExport.*?/>', components_block, code, flags=re.DOTALL)

with open('frontend/src/App.jsx', 'w', encoding='utf-8') as f:
    f.write(code)
