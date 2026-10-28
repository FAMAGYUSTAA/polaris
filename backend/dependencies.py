from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database import get_db
import auth
import jwt
import crud
from stations import is_valid_station

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

def get_current_user_optional(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    if not token:
        return None
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
    except Exception:
        return None
        
    user = crud.get_user_by_username(db, username=username)
    if user and not user.is_active:
        return None
    return user

def get_current_user(current_user = Depends(get_current_user_optional)):
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user

def require_role(roles: list):
    def role_checker(current_user = Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        return current_user
    return role_checker

def require_hq_user():
    return require_role(["HQ"])

def require_station_user():
    def station_checker(current_user = Depends(get_current_user)):
        from permissions import Roles
        if current_user.role == Roles.HQ or current_user.station_id is None:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        return current_user
    return station_checker

from permissions import has_permission, Roles, Permissions

def require_permission(permission: str):
    def permission_checker(current_user = Depends(get_current_user)):
        if not has_permission(current_user.role, permission):
            raise HTTPException(status_code=403, detail="Not enough permissions")
        return current_user
    return permission_checker

def enforce_station_access(station_id: str, current_user):
    """
    If the user is a STATION user, they can only access their own station.
    If the user is HQ or not authenticated (for read-only endpoints), allow.
    Also validates that the station_id is a supported station.
    """
    if station_id is not None and not is_valid_station(station_id):
        raise HTTPException(status_code=400, detail=f"Unknown station ID: {station_id}")
        
    if current_user and current_user.role != Roles.HQ:
        if station_id and station_id != current_user.station_id:
            raise HTTPException(status_code=403, detail="Access denied to this station's data")

