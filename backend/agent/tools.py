import requests

def get_live_weather(origin: str, destination: str) -> str:
    """Tool: Get live simulated weather risk for a given route."""
    # In a real app, this calls an external API. Here we simulate a response.
    if "Miami" in destination or "Houston" in origin:
        return "Severe thunderstorm warnings active along the route. High risk of delay."
    return "Weather is clear. Normal operating conditions."

def check_carrier_status(carrier_id: str = "DEFAULT") -> str:
    """Tool: Check if a carrier is currently experiencing network outages."""
    return f"Carrier {carrier_id} is operating normally with no reported systemic outages."

def get_alternate_route_cost(destination: str) -> float:
    """Tool: Returns the estimated cost in USD to reroute a shipment to this destination."""
    return 850.50

AVAILABLE_TOOLS = {
    "get_live_weather": get_live_weather,
    "check_carrier_status": check_carrier_status,
    "get_alternate_route_cost": get_alternate_route_cost
}
