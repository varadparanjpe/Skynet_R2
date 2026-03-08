from backend.perception.context_builder import ShipmentContext

class GuardrailManager:
    """
    Enforces the Industry-Grade Guardrails before any Autonomous Action is executed.
    """
    @staticmethod
    def evaluate(decision_payload: dict, context: ShipmentContext) -> dict:
        """
        Runs the LLM's proposed decision through strict safety checks.
        decision_payload must include: 'decision', 'confidence', 'cost_impact_usd', 'reasoning'
        """
        safe_decision = decision_payload.copy()
        
        # Guardrail 1 - Confidence Threshold Control
        if safe_decision.get("confidence", 0.0) < 0.65:
            safe_decision["decision"] = "escalate_to_human"
            safe_decision["reasoning_trace"] = safe_decision.get("reasoning_trace", "") + " | Escalate triggered: Confidence < 0.65."

        # Guardrail 2 - Cost Impact Limitation
        if safe_decision.get("cost_impact_usd", 0.0) > context.cost_constraints_usd:
            safe_decision["decision"] = "escalate_to_human"
            safe_decision["reasoning_trace"] = safe_decision.get("reasoning_trace", "") + f" | Escalate triggered: Cost exceeds {context.cost_constraints_usd} limit."
            
        # Guardrail 5 - Safety Policy Enforcement
        if safe_decision["decision"] == "reroute" and context.transport_mode == "SEA":
            safe_decision["decision"] = "escalate_to_human"
            safe_decision["reasoning_trace"] = safe_decision.get("reasoning_trace", "") + " | Escalate triggered: Cannot autonomously reroute SEA vessels."

        return safe_decision
