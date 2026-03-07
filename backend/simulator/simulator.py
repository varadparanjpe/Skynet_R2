import random
import uuid

class LogisticsSimulator:
    def __init__(self):
        self.current_hub_congestion = random.uniform(0.1, 0.4)
        self.weather_event_active = False
        self.event_counter = 0
        self.active_shipments = {} # State store for the Act Loop

    def create_custom_shipment(self, data: dict):
        shipment_id = random.randint(1000, 9999)
        shipment = data.copy()
        shipment["shipment_id"] = shipment_id
        self.active_shipments[shipment_id] = shipment
        return shipment

    def generate_random_event(self):
        self.event_counter += 1
        
        # Simulate cascading events
        if self.event_counter % 5 == 0:
            self.weather_event_active = True
            self.current_hub_congestion = min(1.0, self.current_hub_congestion + 0.5)
        elif self.weather_event_active and self.event_counter % 2 == 0:
            self.weather_event_active = False
            self.current_hub_congestion = max(0.1, self.current_hub_congestion - 0.4)
            
        self.current_hub_congestion = max(0.0, min(1.0, self.current_hub_congestion + random.uniform(-0.1, 0.1)))

        shipment = {
            "shipment_id": random.randint(1000, 9999),
            "origin": random.choice(["Los Angeles", "New York", "Chicago", "Houston"]),
            "destination": random.choice(["Seattle", "Miami", "Denver", "Boston"]),
            "distance_remaining_km": random.uniform(50.0, 1500.0),
            
            "weather_risk": random.uniform(0.6, 1.0) if self.weather_event_active else random.uniform(0.0, 0.3),
            "traffic_risk": random.uniform(0.5, 1.0) if self.weather_event_active else random.uniform(0.1, 0.4),
            "port_hub_queue_time_mins": int(self.current_hub_congestion * 200),
            
            "carrier_reliability": random.uniform(0.1, 0.5) if self.weather_event_active else random.uniform(0.7, 1.0),
            "transport_mode": random.choice(["TRUCK", "RAIL", "AIR", "SEA"]),
            
            "shipment_priority": random.randint(1, 5),
            "cost_constraints_usd": random.uniform(500.0, 5000.0)
        }
        
        self.active_shipments[shipment["shipment_id"]] = shipment
        return shipment

    def execute_action(self, shipment_id: int, action_type: str) -> dict:
        """
        The ACT Loop: Mutates the shipment state based on the AI's autonomous decision.
        """
        if shipment_id not in self.active_shipments:
            return {"error": "shipment_not_found"}
            
        shipment = self.active_shipments[shipment_id]
        
        if action_type == "reroute":
            # Rerouting drops traffic risk significantly, but adds a flat 150km penalty
            shipment["traffic_risk"] = max(0.0, shipment["traffic_risk"] - 0.4)
            shipment["distance_remaining_km"] += 150.0
        elif action_type == "expedite":
            # Expediting forces priority up and drops hub wait time
            shipment["shipment_priority"] = 5
            shipment["port_hub_queue_time_mins"] = int(shipment["port_hub_queue_time_mins"] * 0.2)
            
        # Ensure it stays in state
        self.active_shipments[shipment_id] = shipment
        return shipment
        
    def resolve_shipment(self, shipment_id: int) -> dict:
        """Removes the shipment from active tracking (for the Learn Loop)."""
        return self.active_shipments.pop(shipment_id, None)
