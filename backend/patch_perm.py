import re

with open('permissions.py', 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace('payload.get("status")', 'payload.get("new_status")')

with open('permissions.py', 'w', encoding='utf-8') as f:
    f.write(c)
