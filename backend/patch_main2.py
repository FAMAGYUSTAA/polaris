import os

with open('backend/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

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
"""

if "login_for_access_token" not in content:
    content += login_endpoint

# Fix sync/delta and sneakernet dependencies to be require_station_user and require_hq_user appropriately.
# The prompt says: "Make /api/sync/delta capable of authenticating the Station user.
# A Station user associated with BHARATI must not be able to authenticate as an HQ user.
# Protect routes using the reusable authentication dependency."

delta_target = "current_user = Depends(dependencies.get_current_user)"
content = content.replace(delta_target, "current_user = Depends(dependencies.require_station_user())")

with open('backend/main.py', 'w', encoding='utf-8') as f:
    f.write(content)
