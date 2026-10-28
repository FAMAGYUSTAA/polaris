
# ---------------------------------------------------------------------------
# Cargo Tracking (Online-only)
# ---------------------------------------------------------------------------

@app.get("/api/cargo")
def list_cargo_shipments(
    station_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    import schemas
    shipments = crud.get_cargo_shipments(db, station_id=station_id)
    return [schemas.CargoShipmentRead.model_validate(s).model_dump(mode="json") for s in shipments]

@app.post("/api/cargo")
def create_cargo_shipment(
    shipment: dict, # Take dict and validate manually to avoid modifying global schemas import at top
    db: Session = Depends(get_db),
):
    import schemas
    shipment_obj = schemas.CargoShipmentCreate(**shipment)
    db_shipment = crud.create_cargo_shipment(db, shipment_obj)
    return schemas.CargoShipmentRead.model_validate(db_shipment).model_dump(mode="json")

@app.post("/api/cargo/{shipment_id}/mark-arrived")
def mark_cargo_arrived(
    shipment_id: str,
    db: Session = Depends(get_db),
):
    import schemas
    try:
        db_shipment, unmatched = crud.mark_cargo_arrived(db, shipment_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    return {
        "shipment": schemas.CargoShipmentRead.model_validate(db_shipment).model_dump(mode="json"),
        "unmatched_skus": unmatched,
        "warning": f"Some SKUs were unmatched: {unmatched}" if unmatched else None
    }
