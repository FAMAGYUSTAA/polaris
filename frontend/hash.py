
import json, hashlib
with open('temp_sn.json') as f:
    data = json.load(f)
canonical = json.dumps(data, sort_keys=True, separators=(',', ':'), default=str)
print(hashlib.sha256(canonical.encode('utf-8')).hexdigest(), end='')
  