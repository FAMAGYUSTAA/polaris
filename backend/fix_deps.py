import re

with open('dependencies.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace enforce_station_access and add require_permission
new_code = """
from permissions import has_permission, Roles, Permissions

def require_permission(permission: str):
    def permission_checker(current_user = Depends(get_current_user)):
        if not has_permission(current_user.role, permission):
            raise HTTPException(status_code=403, detail="Not enough permissions")
        return current_user
    return permission_checker

def enforce_station_access(station_id: str, current_user):
    \"\"\"
    If the user is a STATION user, they can only access their own station.
    If the user is HQ or not authenticated (for read-only endpoints), allow.
    Also validates that the station_id is a supported station.
    \"\"\"
    if station_id is not None and not is_valid_station(station_id):
        raise HTTPException(status_code=400, detail=f"Unknown station ID: {station_id}")
        
    if current_user and current_user.role != Roles.HQ:
        if station_id and station_id != current_user.station_id:
            raise HTTPException(status_code=403, detail="Access denied to this station's data")
"""

code = code.replace(
"""def enforce_station_access(station_id: str, current_user):
    \"\"\"
    If the user is a STATION user, they can only access their own station.
    If the user is HQ or not authenticated (for read-only endpoints), allow.
    Also validates that the station_id is a supported station.
    \"\"\"
    if station_id is not None and not is_valid_station(station_id):
        raise HTTPException(status_code=400, detail=f"Unknown station ID: {station_id}")
        
    if current_user and current_user.role == "STATION":
        if station_id and station_id != current_user.station_id:
            raise HTTPException(status_code=403, detail="Access denied to this station's data")""",
new_code.strip()
)

with open('dependencies.py', 'w', encoding='utf-8') as f:
    f.write(code)
