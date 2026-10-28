import sys

with open("main.py", "r", encoding="utf-8") as f:
    content = f.read()

old_block = """    last_sync_at = latest_event.server_received_at
    # 24 hours is a configurable arbitrary threshold
    last_sync_at_naive = last_sync_at.replace(tzinfo=None) if last_sync_at.tzinfo else last_sync_at
    is_stale = datetime.utcnow() - last_sync_at_naive > timedelta(hours=24)
    return {"station_id": station_id, "last_sync_at": last_sync_at.isoformat(), "is_stale": is_stale}"""

new_block = """    last_sync_at = latest_event.server_received_at
    # 24 hours is a configurable arbitrary threshold
    is_stale = datetime.now(timezone.utc) - last_sync_at > timedelta(hours=24)
    return {"station_id": station_id, "last_sync_at": last_sync_at.isoformat(), "is_stale": is_stale}"""

content = content.replace(old_block, new_block)

with open("main.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Updated main.py")
