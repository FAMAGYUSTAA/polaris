import { ROLES, PERMISSIONS, hasPermission, hasAnyPermission, hasAllPermissions, rolePermissions } from './src/permissions.js';

console.log("=== Testing Station Role & Permission Architecture ===");

let passed = 0;
let failed = 0;

function assert(condition, message) {
  if (condition) {
    passed++;
    console.log(`[PASS] ${message}`);
  } else {
    failed++;
    console.error(`[FAIL] ${message}`);
  }
}

// 1. All five roles exist
assert(Object.keys(ROLES).length === 5, "Exactly 5 roles exist");
assert(ROLES.STATION_LEADER === 'STATION_LEADER', "STATION_LEADER exists");
assert(ROLES.LOGISTICS_ENGINEERING_OFFICER === 'LOGISTICS_ENGINEERING_OFFICER', "LOGISTICS_ENGINEERING_OFFICER exists");
assert(ROLES.CHIEF_SCIENTIST === 'CHIEF_SCIENTIST', "CHIEF_SCIENTIST exists");
assert(ROLES.MEDICAL_OFFICER === 'MEDICAL_OFFICER', "MEDICAL_OFFICER exists");
assert(ROLES.FIELD_TEAM_MEMBER === 'FIELD_TEAM_MEMBER', "FIELD_TEAM_MEMBER exists");

// 2. Offline capabilities are cross-cutting
const allRoles = Object.values(ROLES);
allRoles.forEach(role => {
  assert(hasPermission(role, PERMISSIONS.OFFLINE_OPERATION), `${role} has offline_operation`);
  assert(hasPermission(role, PERMISSIONS.OFFLINE_DATA_ENTRY), `${role} has offline_data_entry`);
});

// 3. Every permission listed is assigned correctly
// STATION_LEADER
assert(hasPermission(ROLES.STATION_LEADER, PERMISSIONS.FIELD_MISSION_MANAGEMENT), "STATION_LEADER has field_mission_management");
assert(hasPermission(ROLES.STATION_LEADER, PERMISSIONS.PERSONNEL_MANAGEMENT), "STATION_LEADER has personnel_management");
// LOGISTICS_ENGINEERING_OFFICER
assert(hasPermission(ROLES.LOGISTICS_ENGINEERING_OFFICER, PERMISSIONS.CARGO_TRACKING), "LOGISTICS_ENGINEERING_OFFICER has cargo_tracking");
assert(hasPermission(ROLES.LOGISTICS_ENGINEERING_OFFICER, PERMISSIONS.INVENTORY_MANAGEMENT), "LOGISTICS_ENGINEERING_OFFICER has inventory_management");
// CHIEF_SCIENTIST
assert(hasPermission(ROLES.CHIEF_SCIENTIST, PERMISSIONS.PLANNED_EXPEDITIONS), "CHIEF_SCIENTIST has planned_expeditions");
assert(hasPermission(ROLES.CHIEF_SCIENTIST, PERMISSIONS.FIELD_MISSION_MANAGEMENT_SCIENCE), "CHIEF_SCIENTIST has field_mission_management_science");
// MEDICAL_OFFICER
assert(hasPermission(ROLES.MEDICAL_OFFICER, PERMISSIONS.EMERGENCY_STATUS_REPORTING), "MEDICAL_OFFICER has emergency_status_reporting");
assert(hasPermission(ROLES.MEDICAL_OFFICER, PERMISSIONS.EMERGENCY_MUSTER_MEDICAL), "MEDICAL_OFFICER has emergency_muster_medical");
// FIELD_TEAM_MEMBER
assert(hasPermission(ROLES.FIELD_TEAM_MEMBER, PERMISSIONS.OWN_MISSION_CHECKOUT_CHECKIN), "FIELD_TEAM_MEMBER has own_mission_checkout_checkin");

// 4. Unknown roles do not accidentally receive permissions
assert(hasPermission("UNKNOWN_ROLE", PERMISSIONS.OFFLINE_OPERATION) === false, "Unknown role does not get offline_operation");
assert(hasPermission(undefined, PERMISSIONS.OFFLINE_OPERATION) === false, "undefined role does not get permissions");
assert(hasPermission(null, PERMISSIONS.OFFLINE_OPERATION) === false, "null role does not get permissions");

// 5. Unknown permissions do not accidentally grant access
assert(hasPermission(ROLES.STATION_LEADER, "super_admin_hack") === false, "STATION_LEADER does not have unknown permission");
assert(hasPermission(ROLES.FIELD_TEAM_MEMBER, PERMISSIONS.FIELD_MISSION_MANAGEMENT) === false, "FIELD_TEAM_MEMBER does not have field_mission_management");

// 6. Test helpers
assert(hasAnyPermission(ROLES.STATION_LEADER, [PERMISSIONS.HQ_DIRECTIVES, "fake_perm"]), "hasAnyPermission works");
assert(hasAllPermissions(ROLES.STATION_LEADER, [PERMISSIONS.HQ_DIRECTIVES, PERMISSIONS.EMERGENCY_MUSTER]), "hasAllPermissions works for true");
assert(hasAllPermissions(ROLES.STATION_LEADER, [PERMISSIONS.HQ_DIRECTIVES, "fake_perm"]) === false, "hasAllPermissions works for false");
assert(hasAnyPermission("UNKNOWN", [PERMISSIONS.HQ_DIRECTIVES]) === false, "hasAnyPermission fails safely for unknown role");
assert(hasAllPermissions("UNKNOWN", [PERMISSIONS.HQ_DIRECTIVES]) === false, "hasAllPermissions fails safely for unknown role");

console.log(`\n=== Test Results: ${passed} Passed, ${failed} Failed ===`);
if (failed > 0) {
  process.exit(1);
}
