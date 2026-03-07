import requests

def test_custom():
    payload = {
        "origin": "New York",
        "destination": "Los Angeles",
        "distance_remaining_km": 1000,
        "weather_risk": 0.9,
        "traffic_risk": 0.1,
        "port_hub_queue_time_mins": 30,
        "carrier_reliability": 0.9,
        "transport_mode": "TRUCK",
        "shipment_priority": 1,
        "cost_constraints_usd": 1000
    }
    print("Sending POST request to custom_simulate on port 8001...")
    r = requests.post("http://127.0.0.1:8001/custom_simulate", json=payload, timeout=20)
    print("Status:", r.status_code)
    try:
        print("Response:", r.json())
    except:
        print(r.text)

test_custom()
