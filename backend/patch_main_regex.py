import os
import re

filepath = 'backend/main.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Delta Sync
delta_sig = """def sync_delta(
    request: SyncDeltaRequest,
    db: Session = Depends(get_db),
    current_user = Depends(dependencies.require_station_user())
) -> SyncDeltaResponse:
    for event in request.events:
        if event.station_id != current_user.station_id:
            raise HTTPException(status_code=403, detail=f"Unauthorized station_id: {event.station_id}")
"""
content = re.sub(r'def sync_delta\(\s*request: SyncDeltaRequest,\s*db: Session = Depends\(get_db\),\s*\)\s*->\s*SyncDeltaResponse:', delta_sig, content)

# 2. Sneakernet
sneakernet_sig = """async def sneakernet_import(
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(dependencies.require_station_user())
) -> SyncDeltaResponse:"""
content = re.sub(r'async def sneakernet_import\(\s*request: Request,\s*db: Session = Depends\(get_db\),\s*\)\s*->\s*SyncDeltaResponse:', sneakernet_sig, content)

# 3. Cargo Create
cargo_create_sig = """def create_cargo_shipment(
    shipment: dict, # Take dict and validate manually to avoid modifying global schemas import at top
    db: Session = Depends(get_db),
    current_user = Depends(dependencies.require_station_user())
):"""
content = re.sub(r'def create_cargo_shipment\(\s*shipment: dict, # Take dict and validate manually to avoid modifying global schemas import at top\s*db: Session = Depends\(get_db\),\s*\):', cargo_create_sig, content)

# 4. Cargo Mark Arrived
cargo_arrive_sig = """def mark_cargo_arrived(
    shipment_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(dependencies.require_station_user())
):"""
content = re.sub(r'def mark_cargo_arrived\(\s*shipment_id: str,\s*db: Session = Depends\(get_db\),\s*\):', cargo_arrive_sig, content)

# 5. Cargo Approve
cargo_appr_sig = """def approve_cargo_shipment(
    shipment_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(dependencies.require_hq_user())
):"""
content = re.sub(r'def approve_cargo_shipment\(\s*shipment_id: str,\s*db: Session = Depends\(get_db\),\s*\):', cargo_appr_sig, content)

# 6. Directives Create
dir_create_sig = """def create_directive(
    directive: dict,
    db: Session = Depends(get_db),
    current_user = Depends(dependencies.require_hq_user())
):"""
content = re.sub(r'def create_directive\(\s*directive: dict,\s*db: Session = Depends\(get_db\),\s*\):', dir_create_sig, content)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Regex replacements executed!")
