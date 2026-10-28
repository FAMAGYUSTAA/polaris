import re

with open('test_authz_direct.py', 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace('"status": "MEDICAL_BAY"', '"new_status": "MEDICAL_BAY"')
c = c.replace("'status': 'MEDICAL_BAY'", "'new_status': 'MEDICAL_BAY'")

with open('test_authz_direct.py', 'w', encoding='utf-8') as f:
    f.write(c)
