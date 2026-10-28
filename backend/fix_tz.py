import sys

with open("main.py", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace(
    'is_stale = datetime.now(timezone.utc) - last_sync_at > timedelta(hours=24)',
    'last_sync_at_naive = last_sync_at.replace(tzinfo=None) if last_sync_at.tzinfo else last_sync_at\n    is_stale = datetime.utcnow() - last_sync_at_naive > timedelta(hours=24)'
)

with open("main.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Fixed timezone issue in main.py")
