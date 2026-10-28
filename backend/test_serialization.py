import sys
import json
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Directive, Base, _utcnow
import schemas

engine = create_engine("sqlite:///polar_station.db")
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

# Create dummy directive
d = Directive(
    station_id="BHARATI",
    message="Test Directive",
    issued_by="HQ",
    # issued_at is omitted to test the default _utcnow
)
db.add(d)
db.commit()
db.refresh(d)

print("--- SQLALCHEMY ---")
print("issued_at from DB:", repr(d.issued_at))
print("tzinfo:", d.issued_at.tzinfo)

print("\n--- PYDANTIC ---")
p = schemas.DirectiveRead.model_validate(d)
print("Pydantic model issued_at:", repr(p.issued_at))
print("JSON dump:", p.model_dump(mode="json")['issued_at'])
print("JSON serialized:", json.dumps(p.model_dump(mode="json")))

