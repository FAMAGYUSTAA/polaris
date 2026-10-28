
class ManifestItem(BaseModel):
    sku: str
    name: str
    quantity: float
    unit: str

class CargoShipmentCreate(BaseModel):
    station_id: str
    carrier_name: str
    origin: str
    manifest: List[ManifestItem]
    departure_date: datetime
    expected_arrival: datetime

class CargoShipmentRead(CargoShipmentCreate):
    id: str
    status: str
    arrived_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
