import os

# 1. Update models.py
with open("backend/models.py", "r", encoding="utf-8") as f:
    models_txt = f.read()

models_txt = models_txt.replace(
    '__tablename__ = "field_missions"\n\n    id = Column',
    '__tablename__ = "field_missions"\n\n    id = Column(String, primary_key=True, default=_generate_uuid)\n    station_id = Column(String, index=True, nullable=False)\n    team_lead = Column'
)
# clean up any duplicate id column we just created if it existed
models_txt = models_txt.replace(
    'id = Column(String, primary_key=True, default=_generate_uuid)\n    station_id = Column(String, index=True, nullable=False)\n    team_lead = Column(String, nullable=False)\n    id = Column(String, primary_key=True, default=_generate_uuid)',
    'id = Column(String, primary_key=True, default=_generate_uuid)\n    station_id = Column(String, index=True, nullable=False)\n    team_lead = Column(String, nullable=False)'
)

with open("backend/models.py", "w", encoding="utf-8") as f:
    f.write(models_txt)


# 2. Update schemas.py
with open("backend/schemas.py", "r", encoding="utf-8") as f:
    schemas_txt = f.read()

schemas_txt = schemas_txt.replace(
    'class FieldMissionBase(BaseModel):\n    """Shared fields for field missions."""\n    team_lead: str',
    'class FieldMissionBase(BaseModel):\n    """Shared fields for field missions."""\n    station_id: Optional[str] = None\n    team_lead: str'
)
with open("backend/schemas.py", "w", encoding="utf-8") as f:
    f.write(schemas_txt)


# 3. Update crud.py
with open("backend/crud.py", "r", encoding="utf-8") as f:
    crud_txt = f.read()

crud_txt = crud_txt.replace(
    'def get_active_field_missions(db: Session) -> List[FieldMission]:\n    """\n    Return all currently active field missions (is_active == True).\n\n    Used by the operations dashboard to display teams currently in the field,\n    including their VHF channels and expected return times.\n    """\n    return (\n        db.query(FieldMission)\n        .filter(FieldMission.is_active == True)  # noqa: E712 \x97 SQLAlchemy filter\n        .all()\n    )',
    'def get_active_field_missions(db: Session, station_id: Optional[str] = None) -> List[FieldMission]:\n    query = db.query(FieldMission).filter(FieldMission.is_active == True)\n    if station_id:\n        query = query.filter(FieldMission.station_id == station_id)\n    return query.all()'
)
crud_txt = crud_txt.replace(
    'def get_active_field_missions(db: Session) -> List[FieldMission]:\n    """\n    Return all currently active field missions (is_active == True).\n\n    Used by the operations dashboard to display teams currently in the field,\n    including their VHF channels and expected return times.\n    """\n    return (\n        db.query(FieldMission)\n        .filter(FieldMission.is_active == True)  # noqa: E712  SQLAlchemy filter\n        .all()\n    )',
    'def get_active_field_missions(db: Session, station_id: Optional[str] = None) -> List[FieldMission]:\n    query = db.query(FieldMission).filter(FieldMission.is_active == True)\n    if station_id:\n        query = query.filter(FieldMission.station_id == station_id)\n    return query.all()'
)
# handle unicode dash variations
import re
crud_txt = re.sub(
    r'def get_active_field_missions\(db: Session\) -> List\[FieldMission\]:.*?\.all\(\)\n    \)',
    'def get_active_field_missions(db: Session, station_id: Optional[str] = None) -> List[FieldMission]:\n    query = db.query(FieldMission).filter(FieldMission.is_active == True)\n    if station_id:\n        query = query.filter(FieldMission.station_id == station_id)\n    return query.all()',
    crud_txt,
    flags=re.DOTALL
)

with open("backend/crud.py", "w", encoding="utf-8") as f:
    f.write(crud_txt)


# 4. Update sync_engine.py
with open("backend/sync_engine.py", "r", encoding="utf-8") as f:
    sync_txt = f.read()

sync_txt = sync_txt.replace(
    '    try:\n        handler(db, event.payload)\n    except (ValueError, KeyError, TypeError) as exc:',
    '    try:\n        event.payload["station_id"] = event.station_id\n        handler(db, event.payload)\n    except (ValueError, KeyError, TypeError) as exc:'
)

sync_txt = sync_txt.replace(
    '    mission_data = FieldMissionCreate(\n        id=payload.get("mission_id"),\n        team_lead=payload["team_lead"],',
    '    mission_data = FieldMissionCreate(\n        id=payload.get("mission_id"),\n        station_id=payload.get("station_id"),\n        team_lead=payload["team_lead"],'
)
with open("backend/sync_engine.py", "w", encoding="utf-8") as f:
    f.write(sync_txt)

# 5. Update main.py
with open("backend/main.py", "r", encoding="utf-8") as f:
    main_txt = f.read()

main_txt = main_txt.replace(
    'missions = crud.get_active_field_missions(db)',
    'missions = crud.get_active_field_missions(db, station_id=station_id)'
)
with open("backend/main.py", "w", encoding="utf-8") as f:
    f.write(main_txt)

print("Patching complete.")
