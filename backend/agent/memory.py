class AgentMemory:
    """
    Maintains state and history for the agent.
    In a production system, this would be a Redis or DB backed memory store.
    """
    def __init__(self):
        self.history = []
        self.max_history = 10

    def add_event(self, shipment_id: int, decision: str, reasoning: str):
        self.history.append({
            "shipment_id": shipment_id,
            "decision": decision,
            "reasoning": reasoning
        })
        
        # Prune history to keep context window manageable
        if len(self.history) > self.max_history:
            self.history.pop(0)

    def get_summary(self) -> str:
        if not self.history:
            return "No previous actions taken in this session."
            
        summary = "Recent Agent Actions:\n"
        for idx, event in enumerate(self.history[-5:]):  # Only show last 5 for context
            summary += f"- Shipment {event['shipment_id']}: Decided to '{event['decision']}' because '{event['reasoning']}'\n"
        return summary
