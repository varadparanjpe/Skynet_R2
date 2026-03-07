import json
import requests
from backend.actions.actions import get_logistics_tools
from backend.agent.memory import AgentMemory

class LogisticsAgent:
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model = "llama3"
        self.memory = AgentMemory()
        
    def _call_ollama(self, prompt: str) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        try:
            response = requests.post(self.ollama_url, json=payload, timeout=60)
            response.raise_for_status()
            return response.json().get("response", "")
        except Exception as e:
            print(f"Error calling Ollama: {e}")
            return ""

    def run(self, shipment):
        # Format the input state
        input_data = f"""
        NEW SHIPMENT EVENT:
        Shipment ID: {shipment['shipment_id']}
        Distance: {shipment['distance']} km
        Traffic Level: {shipment['traffic_level']:.2f}
        Hub Congestion: {shipment['hub_congestion']:.2f}
        Carrier Reliability: {shipment['carrier_reliability']:.2f}
        Warehouse Load: {shipment['warehouse_load']:.2f}
        Delay Probability: {shipment['delay_probability']:.2f}
        """
        
        system_prompt = f"""You are an intelligent Supply Chain Agent controlling a logistics network.
Your job is to observe incoming shipment events, reason about the root causes of delays or congestion, and take appropriate action to minimize SLA breaches.

RULES & GUARDRAILS:
1. Always analyze the 'Delay Probability', 'Traffic Level', and 'Hub Congestion'.
2. If Delay Probability > 0.75 and Hub Congestion > 0.8, your decision MUST be 'reroute'.
3. If Carrier Reliability < 0.3, your decision MUST be 'escalate_to_human'.
4. If Delay Probability > 0.8 but Hub Congestion is low, your decision MUST be 'prioritize'.
5. If no intervention is required (Delay Probability < 0.5), your decision MUST be 'none'.

Below is the historical state of the network (Memory):
{self.memory.get_summary()}

You must respond in ONLY valid JSON format conforming exactly to this structure:
{{
    "decision": "<reroute | prioritize | escalate_to_human | none>",
    "action": "<A sentence describing the action taken>",
    "root_cause": "<Your brief analysis of the root cause of the risk>",
    "confidence": <float between 0.0 and 1.0>
}}

Based on the rules and memory, analyze this new shipment:
{input_data}
"""

        # Execute the agent
        response_text = self._call_ollama(system_prompt)
        
        # Parse the JSON response
        decision = "none"
        action_taken = "No action"
        root_cause = "Analysis complete."
        confidence = 0.8
        
        try:
            # Clean up potential markdown formatting from LLM
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
                
            parsed = json.loads(response_text.strip())
            decision = parsed.get("decision", decision).lower()
            action_taken = parsed.get("action", action_taken)
            root_cause = parsed.get("root_cause", root_cause)
            confidence = parsed.get("confidence", confidence)
        except Exception as e:
            print(f"Agent Parsing Error: {e}\nRaw Reponse: {response_text}")
            root_cause = "Failed to parse LLM response cleanly."
            
        # Update memory
        self.memory.add_event(shipment['shipment_id'], decision, root_cause)
        
        # Predict ETA using the heuristic model
        from backend.models.eta_model import ETAModel
        eta_model = ETAModel()
        eta = eta_model.predict([shipment["distance"], shipment["traffic_level"], shipment["hub_congestion"]])

        return {
            "shipment_id": shipment["shipment_id"],
            "eta": eta,
            "risk_score": shipment["delay_probability"],
            "decision": decision,
            "action": action_taken,
            "reasoning": {
                "root_cause": root_cause,
                "confidence": confidence,
                "evidence": []
            }
        }
