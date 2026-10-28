import os

with open('src/permissions.js', 'r', encoding='utf-8') as f:
    code = f.read()

# Add DATA_SYNC to CROSS-CUTTING and all roles.
# Wait, no need to move it in the PERMISSIONS object, just add to rolePermissions arrays.

# Replace for STATION_LEADER
code = code.replace(
"""  [ROLES.STATION_LEADER]: [
    PERMISSIONS.FIELD_MISSION_MANAGEMENT,""",
"""  [ROLES.STATION_LEADER]: [
    PERMISSIONS.DATA_SYNC,
    PERMISSIONS.FIELD_MISSION_MANAGEMENT,"""
)

# Replace for CHIEF_SCIENTIST
code = code.replace(
"""  [ROLES.CHIEF_SCIENTIST]: [
    PERMISSIONS.PLANNED_EXPEDITIONS,""",
"""  [ROLES.CHIEF_SCIENTIST]: [
    PERMISSIONS.DATA_SYNC,
    PERMISSIONS.PLANNED_EXPEDITIONS,"""
)

# Replace for MEDICAL_OFFICER
code = code.replace(
"""  [ROLES.MEDICAL_OFFICER]: [
    PERMISSIONS.EMERGENCY_STATUS_REPORTING,""",
"""  [ROLES.MEDICAL_OFFICER]: [
    PERMISSIONS.DATA_SYNC,
    PERMISSIONS.EMERGENCY_STATUS_REPORTING,"""
)

# Replace for FIELD_TEAM_MEMBER
code = code.replace(
"""  [ROLES.FIELD_TEAM_MEMBER]: [
    PERMISSIONS.OWN_MISSION_CHECKOUT_CHECKIN,""",
"""  [ROLES.FIELD_TEAM_MEMBER]: [
    PERMISSIONS.DATA_SYNC,
    PERMISSIONS.OWN_MISSION_CHECKOUT_CHECKIN,"""
)

# Move DATA_SYNC and SNEAKERNET in the PERMISSIONS dict so they are cross-cutting (optional, but requested implicitly by "Update the centralized permission definitions")
# The user said "Update the centralized permission definitions in the existing permission architecture."
code = code.replace(
"""  // CROSS-CUTTING (All Roles)
  OFFLINE_OPERATION: 'offline_operation',""",
"""  // CROSS-CUTTING (All Roles)
  DATA_SYNC: 'data_sync',
  OFFLINE_OPERATION: 'offline_operation',"""
)

code = code.replace(
"""  EQUIPMENT_ASSET_TRACKING: 'equipment_asset_tracking',
  DATA_SYNC: 'data_sync',
  SNEAKERNET: 'sneakernet',""",
"""  EQUIPMENT_ASSET_TRACKING: 'equipment_asset_tracking',
  SNEAKERNET: 'sneakernet',"""
)


with open('src/permissions.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("permissions.js patched successfully.")
