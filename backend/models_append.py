
class CargoShipment(Base):
    """
    Tracks incoming supply shipments to the polar station.
    Cargo Tracking is online-only in this version; offline sync integration is planned for a future redesign.
    """
    __tablename__ = "cargo_shipments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    station_id = Column(String, index=True, nullable=False)
    carrier_name = Column(String, nullable=False)
    origin = Column(String, nullable=False)
    manifest = Column(JSON, nullable=False)
    departure_date = Column(DateTime, nullable=False)
    expected_arrival = Column(DateTime, nullable=False)
    status = Column(String, default="IN_TRANSIT", nullable=False)
    arrived_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=_utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<CargoShipment {self.carrier_name} to={self.station_id} status={self.status}>"
