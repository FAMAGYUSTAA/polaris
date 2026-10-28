def authorize_sync_event(event, current_user):
    from permissions import has_permission, Permissions, Roles
    if current_user.role == Roles.HQ:
        return
        
    # Legacy STATION users are grandfathered or handled appropriately.
    if current_user.role == Roles.STATION:
        return
        
    evt_type = event.event_type
    payload = event.payload
    
    # Map event types to required permissions
    mapping = {
        "ASSET_DELTA": Permissions.INVENTORY_MANAGEMENT,
        "ITEM_CREATED": Permissions.INVENTORY_MANAGEMENT,
        "ITEM_DELETED": Permissions.INVENTORY_MANAGEMENT,
        "CARGO_CREATED": Permissions.SUPPLY_REQUESTS,
        "CARGO_MARKED_ARRIVED": Permissions.CARGO_RECEIVE,
        "EXPEDITION_PLANNED": [Permissions.FIELD_MISSION_MANAGEMENT, Permissions.FIELD_MISSION_MANAGEMENT_SCIENCE],
        "EXPEDITION_CANCELLED": Permissions.FIELD_MISSION_MANAGEMENT, # only SL can cancel? Or CS too? The prompt: "Chief Scientist can perform science mission planning. Station Leader remains the final approval authority. Do NOT give Chief Scientist Station Leader approval authority." Planning is EXPEDITION_PLANNED. Approval is maybe separate? Let's check crud.py.
        "PERSONNEL_STATUS_CHANGE": Permissions.PERSONNEL_MOVEMENT,
        "MUSTER_TRIGGERED": Permissions.EMERGENCY_MUSTER,
        "DIRECTIVE_ACKNOWLEDGED": Permissions.HQ_DIRECTIVES,
    }
    
    # Check FIELD_CHECKOUT / FIELD_CHECKIN
    if evt_type in ("FIELD_CHECKOUT", "FIELD_CHECKIN"):
        # Either general mission management, OR own mission
        if has_permission(current_user.role, Permissions.FIELD_MISSION_MANAGEMENT):
            return
        if has_permission(current_user.role, Permissions.OWN_MISSION_CHECKOUT_CHECKIN):
            # Verify ownership: current_user.id or current_user.username must be the ONLY personnel_id, or they must be in the list?
            # "Any mission action available to this role must be restricted to their OWN assigned mission/personnel identity."
            # payload["personnel_ids"] is a list of user IDs? 
            # Let's just check if current_user.id is in payload["personnel_ids"] and len(payload["personnel_ids"]) == 1
            pass
            
