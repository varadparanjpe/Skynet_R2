import requests
import json

print("Fetching simulation...")
res = requests.get("http://127.0.0.1:8000/simulate")
data = res.json()
sid = data["shipment"]["shipment_id"]
print(f"Got shipment {sid}")

payload = {"shipment_id": sid, "outcome": "SUCCESS"}
print("Resolving...")
r2 = requests.post("http://127.0.0.1:8000/resolve_shipment", json=payload)
print(r2.status_code, r2.text)
