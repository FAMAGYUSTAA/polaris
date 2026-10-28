import os
import sqlite3

_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'polar_station.db')

def clean_backend():
    conn = sqlite3.connect(_DB_PATH)
    cursor = conn.cursor()
    
    tables_to_clean = [
        'inventory_items', 
        'cargo_shipments', 
        'planned_expeditions', 
        'directives', 
        'sync_ledger'
    ]
    
    report = {}
    for t in tables_to_clean:
        cursor.execute(f"SELECT count(*) FROM {t} WHERE station_id='BHARATI'")
        count = cursor.fetchone()[0]
        
        cursor.execute(f"DELETE FROM {t} WHERE station_id='BHARATI'")
        report[t] = count
        
    conn.commit()
    conn.close()
    
    for k, v in report.items():
        print(f"Deleted {v} records from {k}")

clean_backend()
