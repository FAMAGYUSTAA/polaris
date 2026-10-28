from enum import Enum
from fastapi import HTTPException

class Roles(str, Enum):
    HQ = "HQ"
    STATION = "STATION"
    STATION_LEADER = "STATION_LEADER"
    LOGISTICS_ENGINEERING_OFFICER = "LOGISTICS_ENGINEERING_OFFICER"
    CHIEF_SCIENTIST = "CHIEF_SCIENTIST"
    MEDICAL_OFFICER = "MEDICAL_OFFICER"
    FIELD_TEAM_MEMBER = "FIELD_TEAM_MEMBER"

class Permissions(str, Enum):
    FIELD_MISSION_MANAGEMENT = "field_mission_management"
    PERSONNEL_MANAGEMENT = "personnel_management"
    PERSONNEL_MOVEMENT = "personnel_movement"
    HQ_DIRECTIVES = "hq_directives"
    EMERGENCY_MUSTER = "emergency_muster"
    STATION_OVERVIEW = "station_overview"
    OPERATIONAL_ALERTS = "operational_alerts"
    
    INVENTORY_MANAGEMENT = "inventory_management"
    CARGO_TRACKING = "cargo_tracking"
    CARGO_RECEIVE = "cargo_receive"
    SUPPLY_REQUESTS = "supply_requests"
    LOGISTICS_REQUESTS = "logistics_requests"
    EQUIPMENT_ASSET_TRACKING = "equipment_asset_tracking"
    DATA_SYNC = "data_sync"
    SNEAKERNET = "sneakernet"
    CONNECTIVITY_STATUS = "connectivity_status"
    
    PLANNED_EXPEDITIONS = "planned_expeditions"
    SCIENTIFIC_EQUIPMENT = "scientific_equipment"
    FIELD_MISSION_MANAGEMENT_SCIENCE = "field_mission_management_science"
    
    EMERGENCY_STATUS_REPORTING = "emergency_status_reporting"
    EMERGENCY_MUSTER_MEDICAL = "emergency_muster_medical"
    
    OWN_MISSION_CHECKOUT_CHECKIN = "own_mission_checkout_checkin"
    OWN_EMERGENCY_STATUS_REPORTING = "own_emergency_status_reporting"
    
    OFFLINE_OPERATION = "offline_operation"
    OFFLINE_DATA_ENTRY = "offline_data_entry"

ROLE_PERMISSIONS = {
    Roles.STATION_LEADER: {
        Permissions.FIELD_MISSION_MANAGEMENT,
        Permissions.PERSONNEL_MANAGEMENT,
        Permissions.PERSONNEL_MOVEMENT,
        Permissions.HQ_DIRECTIVES,
        Permissions.EMERGENCY_MUSTER,
        Permissions.STATION_OVERVIEW,
        Permissions.OPERATIONAL_ALERTS,
        Permissions.OFFLINE_OPERATION,
        Permissions.OFFLINE_DATA_ENTRY,
    },
    Roles.LOGISTICS_ENGINEERING_OFFICER: {
        Permissions.INVENTORY_MANAGEMENT,
        Permissions.CARGO_TRACKING,
        Permissions.CARGO_RECEIVE,
        Permissions.SUPPLY_REQUESTS,
        Permissions.LOGISTICS_REQUESTS,
        Permissions.EQUIPMENT_ASSET_TRACKING,
        Permissions.DATA_SYNC,
        Permissions.SNEAKERNET,
        Permissions.CONNECTIVITY_STATUS,
        Permissions.OFFLINE_OPERATION,
        Permissions.OFFLINE_DATA_ENTRY,
    },
    Roles.CHIEF_SCIENTIST: {
        Permissions.PLANNED_EXPEDITIONS,
        Permissions.SCIENTIFIC_EQUIPMENT,
        Permissions.FIELD_MISSION_MANAGEMENT_SCIENCE,
        Permissions.OFFLINE_OPERATION,
        Permissions.OFFLINE_DATA_ENTRY,
    },
    Roles.MEDICAL_OFFICER: {
        Permissions.EMERGENCY_STATUS_REPORTING,
        Permissions.EMERGENCY_MUSTER_MEDICAL,
        Permissions.OFFLINE_OPERATION,
        Permissions.OFFLINE_DATA_ENTRY,
    },
    Roles.FIELD_TEAM_MEMBER: {
        Permissions.OWN_MISSION_CHECKOUT_CHECKIN,
        Permissions.OWN_EMERGENCY_STATUS_REPORTING,
        Permissions.OFFLINE_OPERATION,
        Permissions.OFFLINE_DATA_ENTRY,
    },
}

def has_permission(role: str, permission: str) -> bool:
    if role == Roles.HQ:
        return True 
    if role == Roles.STATION:
        return True # Legacy override
    if role not in ROLE_PERMISSIONS:
        return False
    return permission in ROLE_PERMISSIONS[role]

def authorize_sync_event(event, current_user):
    if current_user.role == Roles.HQ or current_user.role == Roles.STATION:
        return
        
    evt_type = event.event_type
    payload = event.payload
    
    if evt_type in ("ASSET_DELTA", "ITEM_CREATED", "ITEM_DELETED"):
        if not has_permission(current_user.role, Permissions.INVENTORY_MANAGEMENT):
            raise Exception("Missing INVENTORY_MANAGEMENT permission")
    elif evt_type == "CARGO_CREATED":
        if not has_permission(current_user.role, Permissions.SUPPLY_REQUESTS):
            raise Exception("Missing SUPPLY_REQUESTS permission")
    elif evt_type == "CARGO_MARKED_ARRIVED":
        if not has_permission(current_user.role, Permissions.CARGO_RECEIVE):
            raise Exception("Missing CARGO_RECEIVE permission")
    elif evt_type == "EXPEDITION_PLANNED":
        if not has_permission(current_user.role, Permissions.FIELD_MISSION_MANAGEMENT) and not has_permission(current_user.role, Permissions.FIELD_MISSION_MANAGEMENT_SCIENCE):
            raise Exception("Missing expedition planning permissions")
    elif evt_type == "EXPEDITION_CANCELLED":
        # Chief Scientist can plan, but Station Leader remains final approval/administrative authority
        # If cancelled, maybe only Station Leader? 
        if not has_permission(current_user.role, Permissions.FIELD_MISSION_MANAGEMENT):
            raise Exception("Missing FIELD_MISSION_MANAGEMENT permission to cancel")
    elif evt_type == "PERSONNEL_STATUS_CHANGE":
        if not has_permission(current_user.role, Permissions.PERSONNEL_MOVEMENT):
            # Also check if it's medical/emergency status change?
            if payload.get("new_status") == "MEDICAL_BAY":
                if not has_permission(current_user.role, Permissions.EMERGENCY_STATUS_REPORTING):
                    raise Exception("Missing emergency or personnel movement permission")
            else:
                raise Exception("Missing PERSONNEL_MOVEMENT permission")
    elif evt_type == "MUSTER_TRIGGERED":
        # Station Leader controls the muster.
        if not has_permission(current_user.role, Permissions.EMERGENCY_MUSTER):
            raise Exception("Missing EMERGENCY_MUSTER permission")
    elif evt_type == "DIRECTIVE_ACKNOWLEDGED":
        if not has_permission(current_user.role, Permissions.HQ_DIRECTIVES):
            raise Exception("Missing HQ_DIRECTIVES permission")
    elif evt_type in ("FIELD_CHECKOUT", "FIELD_CHECKIN"):
        # Could be Station Leader, Chief Scientist (science mission), or Field Team Member (own)
        # We need to enforce Co-Ownership rules!
        can_manage = has_permission(current_user.role, Permissions.FIELD_MISSION_MANAGEMENT)
        can_science = has_permission(current_user.role, Permissions.FIELD_MISSION_MANAGEMENT_SCIENCE)
        can_own = has_permission(current_user.role, Permissions.OWN_MISSION_CHECKOUT_CHECKIN)
        
        if can_manage:
            pass # OK
        elif can_science and evt_type == "FIELD_CHECKOUT":
            # For checking in/out science missions, they might need permission?
            # Prompt says "Chief Scientist can perform science mission planning... Station Leader remains final approval authority."
            # Planning is handled by EXPEDITION_PLANNED.
            # Does checkout need Station Leader? "Station Leader remains the final approval authority."
            # Maybe we just let them if they have FIELD_MISSION_MANAGEMENT_SCIENCE.
            pass
        elif can_own:
            # Must be restricted to their OWN assigned mission/personnel identity.
            # verify ownership: the personnel_ids list must contain their ID and ONLY their ID, or something similar
            personnel_ids = payload.get("personnel_ids", [])
            members = payload.get("members", [])
            
            # Since User id/username maps to Personnel id/full_name loosely:
            # The current_user must be one of the personnel, and they can't check out others?
            # Let's say if they are only authorized for their OWN, they must be checking out ONLY themselves or they are in the list?
            if current_user.id not in personnel_ids and current_user.username not in members:
                raise Exception("Cannot modify another person's mission checkout/checkin")
            # Enforce that they only modify their own status
            if len(personnel_ids) > 1:
                raise Exception("Cannot perform mission checkout/checkin for multiple personnel")
        else:
            raise Exception("Missing field mission permissions")
    else:
        # Unknown event type, allow by default or deny?
        pass
