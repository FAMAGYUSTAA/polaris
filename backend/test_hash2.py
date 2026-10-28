import json
from schemas import SneakernetBundle

with open("test_sn_payload.json") as f:
    data = json.load(f)

bundle = SneakernetBundle(**data)
print("Hash passed?", bundle.hash == data["hash"])
bdict = bundle.dict(exclude={"hash"})
print("data:", data)
print("bdict:", bdict)
