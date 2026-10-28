export const ROLES = {
  STATION_LEADER: 'STATION_LEADER',
  LOGISTICS_ENGINEERING_OFFICER: 'LOGISTICS_ENGINEERING_OFFICER',
  CHIEF_SCIENTIST: 'CHIEF_SCIENTIST',
  MEDICAL_OFFICER: 'MEDICAL_OFFICER',
  FIELD_TEAM_MEMBER: 'FIELD_TEAM_MEMBER'
};

export const ROLE_LABELS = {
  [ROLES.STATION_LEADER]: 'Station Leader',
  [ROLES.LOGISTICS_ENGINEERING_OFFICER]: 'Logistics/Engineering Officer',
  [ROLES.CHIEF_SCIENTIST]: 'Chief Scientist',
  [ROLES.MEDICAL_OFFICER]: 'Medical Officer',
  [ROLES.FIELD_TEAM_MEMBER]: 'Field Team Member'
};

export const PERMISSIONS = {
  // STATION_LEADER
  FIELD_MISSION_MANAGEMENT: 'field_mission_management',
  PERSONNEL_MANAGEMENT: 'personnel_management',
  PERSONNEL_MOVEMENT: 'personnel_movement',
  HQ_DIRECTIVES: 'hq_directives',
  EMERGENCY_MUSTER: 'emergency_muster',
  STATION_OVERVIEW: 'station_overview',
  OPERATIONAL_ALERTS: 'operational_alerts',
  
  // LOGISTICS_ENGINEERING_OFFICER
  INVENTORY_MANAGEMENT: 'inventory_management',
  CARGO_TRACKING: 'cargo_tracking',
  CARGO_RECEIVE: 'cargo_receive',
  SUPPLY_REQUESTS: 'supply_requests',
  LOGISTICS_REQUESTS: 'logistics_requests',
  EQUIPMENT_ASSET_TRACKING: 'equipment_asset_tracking',
  SNEAKERNET: 'sneakernet',
  CONNECTIVITY_STATUS: 'connectivity_status',
  
  // CHIEF_SCIENTIST
  PLANNED_EXPEDITIONS: 'planned_expeditions',
  SCIENTIFIC_EQUIPMENT: 'scientific_equipment',
  FIELD_MISSION_MANAGEMENT_SCIENCE: 'field_mission_management_science',
  
  // MEDICAL_OFFICER
  EMERGENCY_STATUS_REPORTING: 'emergency_status_reporting',
  EMERGENCY_MUSTER_MEDICAL: 'emergency_muster_medical',
  
  // FIELD_TEAM_MEMBER
  OWN_MISSION_CHECKOUT_CHECKIN: 'own_mission_checkout_checkin',
  OWN_EMERGENCY_STATUS_REPORTING: 'own_emergency_status_reporting',
  
  // CROSS-CUTTING (All Roles)
  DATA_SYNC: 'data_sync',
  OFFLINE_OPERATION: 'offline_operation',
  OFFLINE_DATA_ENTRY: 'offline_data_entry'
};

export const rolePermissions = {
  [ROLES.STATION_LEADER]: [
    PERMISSIONS.DATA_SYNC,
    PERMISSIONS.FIELD_MISSION_MANAGEMENT,
    PERMISSIONS.PERSONNEL_MANAGEMENT,
    PERMISSIONS.PERSONNEL_MOVEMENT,
    PERMISSIONS.HQ_DIRECTIVES,
    PERMISSIONS.EMERGENCY_MUSTER,
    PERMISSIONS.STATION_OVERVIEW,
    PERMISSIONS.OPERATIONAL_ALERTS,
    PERMISSIONS.OFFLINE_OPERATION,
    PERMISSIONS.OFFLINE_DATA_ENTRY
  ],
  [ROLES.LOGISTICS_ENGINEERING_OFFICER]: [
    PERMISSIONS.INVENTORY_MANAGEMENT,
    PERMISSIONS.CARGO_TRACKING,
    PERMISSIONS.CARGO_RECEIVE,
    PERMISSIONS.SUPPLY_REQUESTS,
    PERMISSIONS.LOGISTICS_REQUESTS,
    PERMISSIONS.EQUIPMENT_ASSET_TRACKING,
    PERMISSIONS.DATA_SYNC,
    PERMISSIONS.SNEAKERNET,
    PERMISSIONS.CONNECTIVITY_STATUS,
    PERMISSIONS.OFFLINE_OPERATION,
    PERMISSIONS.OFFLINE_DATA_ENTRY
  ],
  [ROLES.CHIEF_SCIENTIST]: [
    PERMISSIONS.DATA_SYNC,
    PERMISSIONS.PLANNED_EXPEDITIONS,
    PERMISSIONS.SCIENTIFIC_EQUIPMENT,
    PERMISSIONS.FIELD_MISSION_MANAGEMENT_SCIENCE,
    PERMISSIONS.OFFLINE_OPERATION,
    PERMISSIONS.OFFLINE_DATA_ENTRY
  ],
  [ROLES.MEDICAL_OFFICER]: [
    PERMISSIONS.DATA_SYNC,
    PERMISSIONS.EMERGENCY_STATUS_REPORTING,
    PERMISSIONS.EMERGENCY_MUSTER_MEDICAL,
    PERMISSIONS.OFFLINE_OPERATION,
    PERMISSIONS.OFFLINE_DATA_ENTRY
  ],
  [ROLES.FIELD_TEAM_MEMBER]: [
    PERMISSIONS.DATA_SYNC,
    PERMISSIONS.OWN_MISSION_CHECKOUT_CHECKIN,
    PERMISSIONS.OWN_EMERGENCY_STATUS_REPORTING,
    PERMISSIONS.OFFLINE_OPERATION,
    PERMISSIONS.OFFLINE_DATA_ENTRY
  ]
};

/**
 * Check if a specific role has a specific permission.
 * @param {string} role - The role key (e.g., ROLES.STATION_LEADER)
 * @param {string} permission - The permission key (e.g., PERMISSIONS.HQ_DIRECTIVES)
 * @returns {boolean} - True if the role has the permission, false otherwise.
 */
export function hasPermission(role, permission) {
  if (!role || !permission || !rolePermissions[role]) {
    return false;
  }
  return rolePermissions[role].includes(permission);
}

/**
 * Check if a role has AT LEAST ONE of the specified permissions.
 * @param {string} role - The role key
 * @param {string[]} permissions - Array of permissions to check
 * @returns {boolean}
 */
export function hasAnyPermission(role, permissions) {
  if (!role || !permissions || !Array.isArray(permissions) || !rolePermissions[role]) {
    return false;
  }
  return permissions.some(permission => rolePermissions[role].includes(permission));
}

/**
 * Check if a role has ALL of the specified permissions.
 * @param {string} role - The role key
 * @param {string[]} permissions - Array of permissions to check
 * @returns {boolean}
 */
export function hasAllPermissions(role, permissions) {
  if (!role || !permissions || !Array.isArray(permissions) || permissions.length === 0 || !rolePermissions[role]) {
    return false;
  }
  return permissions.every(permission => rolePermissions[role].includes(permission));
}
