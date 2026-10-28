import sys
import os

from sqlalchemy.orm import Session
import database
import models
import crud
import auth

db = database.SessionLocal()

stations = [
    ("BHARATI", "bharati_password", "bharati"),
    ("MAITRI", "maitri_password", "maitri"),
    ("HIMADRI", "himadri_password", "himadri"),
]

roles = [
    ("leader", "STATION_LEADER"),
    ("logistics", "LOGISTICS_ENGINEERING_OFFICER"),
    ("scientist", "CHIEF_SCIENTIST"),
    ("medical", "MEDICAL_OFFICER"),
    ("field", "FIELD_TEAM_MEMBER"),
]

print("Existing Users:")
for user in db.query(models.User).all():
    print(f" - {user.username} ({user.role}) @ {user.station_id}")

# Delete old operator accounts if they exist
for station_name, _, prefix in stations:
    old_username = f"{prefix}_operator"
    old_user = crud.get_user_by_username(db, username=old_username)
    if old_user:
        print(f"Deleting deprecated account: {old_username}")
        db.delete(old_user)
        db.commit()

# Create or update new accounts
for station_name, pwd, prefix in stations:
    for suffix, role_enum in roles:
        username = f"{prefix}_{suffix}"
        user = crud.get_user_by_username(db, username=username)
        pwd_hash = auth.get_password_hash(pwd)
        
        if user:
            print(f"Updating existing user: {username}")
            user.password_hash = pwd_hash
            user.role = role_enum
            user.station_id = station_name
        else:
            print(f"Creating new user: {username}")
            new_user = models.User(
                username=username,
                password_hash=pwd_hash,
                role=role_enum,
                station_id=station_name,
                is_active=True
            )
            db.add(new_user)
            
db.commit()
print("Done creating 15 role-specific accounts.")
db.close()
