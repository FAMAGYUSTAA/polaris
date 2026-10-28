import sys

def append_to_file(filepath, text):
    with open(filepath, 'a', encoding='utf-8') as f:
        f.write("\n" + text + "\n")

# models.py
append_to_file('models.py', '''
class PlannedExpedition(Base):
    """
    Future planned expedition scheduling.
    """
    __tablename__ = "planned_expeditions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    station_id = Column(String, index=True, nullable=False)
    team_lead = Column(String, nullable=False)
    members = Column(JSON, nullable=False)
    purpose = Column(String, nullable=False)
    destination_coords = Column(String, nullable=False)
    vhf_channel = Column(String, nullable=False)
    planned_departure = Column(DateTime, nullable=False)
    planned_return = Column(DateTime, nullable=False)
    status = Column(String, default="PLANNED", nullable=False)
    created_at = Column(DateTime, default=_utcnow, nullable=False)
    cancelled_at = Column(DateTime, nullable=True)

    def __repr__(self) -> str:
        return f"<PlannedExpedition {self.id} lead={self.team_lead} status={self.status}>"
''')

# schemas.py
append_to_file('schemas.py', '''
class PlannedExpeditionCreate(BaseModel):
    id: Optional[str] = None
    station_id: str
    team_lead: str
    members: List[str]
    purpose: str
    destination_coords: str
    vhf_channel: str
    planned_departure: datetime
    planned_return: datetime

class PlannedExpeditionRead(PlannedExpeditionCreate):
    id: str
    status: str
    created_at: datetime
    cancelled_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
''')

# crud.py
append_to_file('crud.py', '''
from models import PlannedExpedition
def get_planned_expeditions(db: Session, station_id: Optional[str] = None, include_cancelled: bool = False) -> List[PlannedExpedition]:
    query = db.query(PlannedExpedition)
    if station_id:
        query = query.filter(PlannedExpedition.station_id == station_id)
    if not include_cancelled:
        query = query.filter(PlannedExpedition.status == "PLANNED")
    return query.order_by(PlannedExpedition.planned_departure.asc()).all()

def create_planned_expedition(db: Session, expedition) -> PlannedExpedition:
    db_exp = PlannedExpedition(**expedition.model_dump(exclude_unset=True, exclude_none=True))
    db.add(db_exp)
    db.commit()
    db.refresh(db_exp)
    return db_exp

def cancel_planned_expedition(db: Session, expedition_id: str) -> bool:
    from datetime import datetime, timezone
    exp = db.query(PlannedExpedition).filter(PlannedExpedition.id == expedition_id).first()
    if exp:
        exp.status = "CANCELLED"
        exp.cancelled_at = datetime.now(timezone.utc)
        db.commit()
        return True
    return False
''')

# main.py
append_to_file('main.py', '''
@app.get("/api/expeditions")
def get_expeditions(
    station_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    import schemas
    expeditions = crud.get_planned_expeditions(db, station_id=station_id)
    return [schemas.PlannedExpeditionRead.model_validate(e).model_dump(mode="json") for e in expeditions]
''')

# sync_engine.py
sync_content = open('sync_engine.py', 'r', encoding='utf-8').read()

new_handlers = '''
def _handle_expedition_planned(db: Session, payload: dict) -> None:
    from schemas import PlannedExpeditionCreate
    _require_keys(payload, ["station_id", "team_lead", "members", "purpose", "destination_coords", "vhf_channel", "planned_departure", "planned_return"])
    
    exp_create = PlannedExpeditionCreate(**payload)
    crud.create_planned_expedition(db, exp_create)

def _handle_expedition_cancelled(db: Session, payload: dict) -> None:
    _require_keys(payload, ["expedition_id"])
    cancelled = crud.cancel_planned_expedition(db, payload["expedition_id"])
    if not cancelled:
        logger.info("EXPEDITION_CANCELLED expedition not found or already cancelled: %s - treated as success", payload["expedition_id"])

# Handler dispatch table
'''
sync_content = sync_content.replace('# Handler dispatch table', new_handlers)

dict_replacement = '''_EVENT_HANDLERS: Dict[str, Any] = {
    "ASSET_DELTA": _handle_asset_delta,
    "FIELD_CHECKOUT": _handle_field_checkout,
    "FIELD_CHECKIN": _handle_field_checkin,
    "PERSONNEL_STATUS_CHANGE": _handle_personnel_status_change,
    "MUSTER_TRIGGERED": _handle_muster_triggered,
    "ITEM_CREATED": _handle_item_created,
    "ITEM_DELETED": _handle_item_deleted,
    "EXPEDITION_PLANNED": _handle_expedition_planned,
    "EXPEDITION_CANCELLED": _handle_expedition_cancelled,
}'''
import re
sync_content = re.sub(r'_EVENT_HANDLERS: Dict\[str, Any\] = \{.*\}', dict_replacement, sync_content, flags=re.DOTALL)

with open('sync_engine.py', 'w', encoding='utf-8') as f:
    f.write(sync_content)

print("Update script completed successfully.")
