
# ---------------------------------------------------------------------------
# Cargo Tracking (Online-only)
# ---------------------------------------------------------------------------

def get_cargo_shipments(db: Session, station_id: Optional[str] = None):
    import models
    query = db.query(models.CargoShipment)
    if station_id:
        query = query.filter(models.CargoShipment.station_id == station_id)
    return query.order_by(models.CargoShipment.expected_arrival.asc()).all()

def create_cargo_shipment(db: Session, shipment):
    import models
    db_shipment = models.CargoShipment(**shipment.model_dump())
    db.add(db_shipment)
    db.commit()
    db.refresh(db_shipment)
    return db_shipment

def mark_cargo_arrived(db: Session, shipment_id: str):
    import models
    db_shipment = db.query(models.CargoShipment).filter(models.CargoShipment.id == shipment_id).first()
    if not db_shipment:
        raise ValueError(f"CargoShipment with id {shipment_id} not found")
    
    db_shipment.status = "ARRIVED"
    db_shipment.arrived_at = datetime.now(timezone.utc)
    
    unmatched = []
    # parse manifest which is a list of dicts
    manifest = db_shipment.manifest
    for item in manifest:
        sku = item.get("sku")
        qty = item.get("quantity")
        inv_item = db.query(models.InventoryItem).filter(
            models.InventoryItem.station_id == db_shipment.station_id,
            models.InventoryItem.sku == sku
        ).first()
        if inv_item:
            apply_inventory_delta(db, inv_item.id, float(qty))
        else:
            unmatched.append(sku)
            
    db.commit()
    db.refresh(db_shipment)
    return db_shipment, unmatched
