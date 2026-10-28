import os

filepath = 'backend/main.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add imports
imports_to_add = """
from fastapi.security import OAuth2PasswordRequestForm
import auth
import dependencies
import crud
"""
content = content.replace("from database import Base, SessionLocal, engine, get_db", "from database import Base, SessionLocal, engine, get_db\n" + imports_to_add)

# 2. Modify startup
startup_code = """    Base.metadata.create_all(bind=engine)
    
    # Seed Demo Users
    with SessionLocal() as db:
        from schemas import UserCreate
        if not crud.get_user_by_username(db, "hq_operator"):
            crud.create_user(db, UserCreate(username="hq_operator", password="hq_password", role="HQ", is_active=True))
        if not crud.get_user_by_username(db, "bharati_operator"):
            crud.create_user(db, UserCreate(username="bharati_operator", password="bharati_password", role="STATION", station_id="BHARATI", is_active=True))
"""
content = content.replace("    Base.metadata.create_all(bind=engine)", startup_code)

# 3. Add Login Endpoint
login_endpoint = """
@app.post("/api/auth/login", response_model=schemas.Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = crud.get_user_by_username(db, username=form_data.username)
    if not user or not auth.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
        
    access_token_expires = auth.timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username, "role": user.role, "station_id": user.station_id}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# ---------------------------------------------------------------------------
"""
content = content.replace("# ---------------------------------------------------------------------------\n# Health check", login_endpoint + "# Health check")

# 4. Protect /api/sync/delta
delta_sig = """@app.post("/api/sync/delta", response_model=SyncDeltaResponse)
def sync_delta(
    request: SyncDeltaRequest,
    db: Session = Depends(get_db),
    current_user = Depends(dependencies.get_current_user)
):
    if current_user.role == "STATION":
        for event in request.events:
            if event.station_id != current_user.station_id:
                raise HTTPException(status_code=403, detail=f"Unauthorized station_id: {event.station_id}")"""
content = content.replace("""@app.post("/api/sync/delta", response_model=SyncDeltaResponse)
def sync_delta(
    request: SyncDeltaRequest,
    db: Session = Depends(get_db),
):""", delta_sig)

# 5. Protect sneakernet
sneakernet_sig = """@app.post("/api/sync/sneakernet-import", response_model=SyncDeltaResponse)
async def sneakernet_import(
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(dependencies.get_current_user)
):"""
content = content.replace("""@app.post("/api/sync/sneakernet-import", response_model=SyncDeltaResponse)
async def sneakernet_import(
    request: Request,
    db: Session = Depends(get_db),
):""", sneakernet_sig)

# 6. Protect cargo POST endpoints
cargo_post_sig = """@app.post("/api/cargo")
def create_cargo_shipment(
    shipment: dict, # Take dict and validate manually to avoid modifying global schemas import at top
    db: Session = Depends(get_db),
    current_user = Depends(dependencies.require_station_user())
):"""
content = content.replace("""@app.post("/api/cargo")
def create_cargo_shipment(
    shipment: dict, # Take dict and validate manually to avoid modifying global schemas import at top
    db: Session = Depends(get_db),
):""", cargo_post_sig)

mark_arrived_sig = """@app.post("/api/cargo/{shipment_id}/mark-arrived")
def mark_cargo_arrived(
    shipment_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(dependencies.require_station_user())
):"""
content = content.replace("""@app.post("/api/cargo/{shipment_id}/mark-arrived")
def mark_cargo_arrived(
    shipment_id: str,
    db: Session = Depends(get_db),
):""", mark_arrived_sig)

approve_sig = """@app.post("/api/cargo/{shipment_id}/approve")
def approve_cargo_shipment(
    shipment_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(dependencies.require_hq_user())
):"""
content = content.replace("""@app.post("/api/cargo/{shipment_id}/approve")
def approve_cargo_shipment(
    shipment_id: str,
    db: Session = Depends(get_db),
):""", approve_sig)

# 7. Protect directives
directives_sig = """@app.post("/api/directives")
def create_directive(
    directive: dict,
    db: Session = Depends(get_db),
    current_user = Depends(dependencies.require_hq_user())
):"""
content = content.replace("""@app.post("/api/directives")
def create_directive(
    directive: dict,
    db: Session = Depends(get_db),
):""", directives_sig)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("main.py updated!")
