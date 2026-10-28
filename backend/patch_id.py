import re

with open('test_authz_direct.py', 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace('"personnel_id": "123"', '"personnel_id": str(user_objs["STATION_LEADER"].id)')

with open('test_authz_direct.py', 'w', encoding='utf-8') as f:
    f.write(c)
