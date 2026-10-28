import os
import sqlite3

_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'polar_station.db')

def check_db():
    conn = sqlite3.connect(_DB_PATH)
    cursor = conn.cursor()
    
    tables = [
        'inventory_items', 
        'personnel', 
        'field_missions', 
        'sync_ledger', 
        'cargo_shipments', 
        'planned_expeditions', 
        'directives', 
        'users'
    ]
    
    for t in tables:
        # Get column names
        cursor.execute(f"PRAGMA table_info({t})")
        cols = [r[1] for r in cursor.fetchall()]
        
        if 'station_id' in cols:
            cursor.execute(f"SELECT count(*) FROM {t} WHERE station_id='BHARATI'")
            print(f"{t}: {cursor.fetchone()[0]} BHARATI records")
        else:
            cursor.execute(f"SELECT count(*) FROM {t}")
            print(f"{t}: {cursor.fetchone()[0]} total records (no station_id)")

check_db()
