import fs from 'fs';

const filepath = 'backend/sync_engine.py';
let content = fs.readFileSync(filepath, 'utf8');

const handlersCode = `
def _handle_cargo_created(db: Session, payload: dict) -> None:
    schema = schemas.CargoShipmentCreate(**payload)
    crud.create_cargo_shipment(db, schema)

def _handle_cargo_marked_arrived(db: Session, payload: dict) -> None:
    _require_keys(payload, ["shipment_id"])
    import models
    db_shipment = db.query(models.CargoShipment).filter(models.CargoShipment.id == payload["shipment_id"]).first()
    if not db_shipment:
        raise ValueError(f"CargoShipment {payload['shipment_id']} not found")
    if db_shipment.status == "ARRIVED":
        # Already arrived, prevent duplicate inventory updates
        return
    crud.mark_cargo_arrived(db, payload["shipment_id"])

# Handler dispatch table`;

content = content.replace("# Handler dispatch table", handlersCode);

const dictCode = `_EVENT_HANDLERS: Dict[str, Any] = {
    "ASSET_DELTA": _handle_asset_delta,
    "FIELD_CHECKOUT": _handle_field_checkout,
    "FIELD_CHECKIN": _handle_field_checkin,
    "PERSONNEL_STATUS_CHANGE": _handle_personnel_status_change,
    "MUSTER_TRIGGERED": _handle_muster_triggered,
    "ITEM_CREATED": _handle_item_created,
    "ITEM_DELETED": _handle_item_deleted,
    "EXPEDITION_PLANNED": _handle_expedition_planned,
    "EXPEDITION_CANCELLED": _handle_expedition_cancelled,
    "DIRECTIVE_ACKNOWLEDGED": _handle_directive_acknowledged,
    "CARGO_CREATED": _handle_cargo_created,
    "CARGO_MARKED_ARRIVED": _handle_cargo_marked_arrived,
}`;

content = content.replace(/_EVENT_HANDLERS: Dict\[str, Any\] = \{[^}]+\}/, dictCode);

fs.writeFileSync(filepath, content);
console.log("Updated sync_engine.py with cargo handlers.");
