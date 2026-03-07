from langchain.tools import tool

@tool
def reroute_shipment(shipment_id: int, reason: str) -> str:
    """Use this tool to reroute a shipment when traffic or hub congestion is too high."""
    return f"Successfully rerouted shipment {shipment_id}. Reason: {reason}"

@tool
def prioritize_order(shipment_id: int, reason: str) -> str:
    """Use this tool to prioritize an order if it is delayed but cannot be rerouted."""
    return f"Priority increased for shipment {shipment_id}. Reason: {reason}"

@tool
def escalate_to_human(shipment_id: int, issue: str) -> str:
    """Use this tool to escalate a critical issue (e.g., carrier reliability very low) to a human manager."""
    return f"Escalated shipment {shipment_id} to human operator. Issue: {issue}"

@tool
def no_action(shipment_id: int, reason: str) -> str:
    """Use this tool when the shipment is healthy and no intervention is required."""
    return f"No action taken for shipment {shipment_id}. Reason: {reason}"

def get_logistics_tools():
    """Returns the list of tools available to the LangChain agent."""
    return [reroute_shipment, prioritize_order, escalate_to_human, no_action]
