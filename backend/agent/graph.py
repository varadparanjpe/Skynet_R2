from typing import TypedDict, Annotated, Optional
from langgraph.graph import StateGraph, END
import joblib
import json

from backend.perception.context_builder import ShipmentContext
from backend.memory.long_term_memory import VectorMemoryFAISS
from backend.agent.llm_client import OllamaClient
from backend.guardrails.manager import GuardrailManager
from backend.agent.tools import AVAILABLE_TOOLS

# Load ML Models globally in memory
delay_model = joblib.load('backend/predictive/models/delay_model.pkl')
eta_model = joblib.load('backend/predictive/models/eta_model.pkl')

class GraphState(TypedDict):
    """
    State representing the short-term working memory of the LangGraph flow.
    """
    raw_shipment_dict: dict
    context: Optional[ShipmentContext]
    ml_predictions: dict
    memory_context: list
    tool_results: list
    llm_decision: dict
    final_output: dict

class AgentWorkflow:
    def __init__(self):
        self.memory_db = VectorMemoryFAISS()
        self.llm = OllamaClient()
        
        # Define the Graph
        workflow = StateGraph(GraphState)
        
        # Add Nodes
        workflow.add_node("perception", self.node_perception)
        workflow.add_node("predict", self.node_predict)
        workflow.add_node("query_memory", self.node_query_memory)
        workflow.add_node("reason", self.node_reason)
        workflow.add_node("guardrails", self.node_guardrails)
        
        # Edges
        workflow.set_entry_point("perception")
        workflow.add_edge("perception", "predict")
        workflow.add_edge("predict", "query_memory")
        workflow.add_edge("query_memory", "reason")
        workflow.add_edge("reason", "guardrails")
        workflow.add_edge("guardrails", END)
        
        self.app = workflow.compile()

    def run(self, raw_shipment_data: dict):
        initial_state = {
            "raw_shipment_dict": raw_shipment_data,
            "context": None,
            "ml_predictions": {},
            "memory_context": [],
            "tool_results": [],
            "llm_decision": {},
            "final_output": {}
        }
        # Run graph
        result = self.app.invoke(initial_state)
        return result["final_output"]

    # --- NODE IMPLEMENTATIONS ---
    
    def node_perception(self, state: GraphState):
        """Guardrail 4: Validates strict typing via Pydantic"""
        try:
            context = ShipmentContext(**state["raw_shipment_dict"])
            return {"context": context}
        except Exception as e:
            print(f"Data Validation Error: {e}")
            raise e

    def node_predict(self, state: GraphState):
        """Uses Scikit-Learn pipelines to predict delay and ETA"""
        ctx = state["context"]
        features = [[
            ctx.distance_remaining_km, 
            ctx.weather_risk, 
            ctx.traffic_risk, 
            ctx.port_hub_queue_time_mins, 
            ctx.carrier_reliability, 
            ctx.shipment_priority
        ]]
        
        # Predict
        prob = float(delay_model.predict_proba(features)[0][1])
        eta = float(eta_model.predict(features)[0])
        
        return {"ml_predictions": {"delay_prob": prob, "eta_mins": eta}}

    def node_query_memory(self, state: GraphState):
        """FAISS Vector Retrieval for long-term intelligence"""
        similar = self.memory_db.retrieve_similar(state["raw_shipment_dict"], top_k=2)
        return {"memory_context": similar}

    def node_reason(self, state: GraphState):
        """LLM Prompting for Tradeoffs and Action Protocol, with Tool Execution"""
        ctx = state["context"]
        preds = state["ml_predictions"]
        mem = state["memory_context"]
        
        # We manually execute the tools before the final prompt to simulate ReAct gathering in a single graph turn
        tool_outputs = []
        try:
            w = AVAILABLE_TOOLS["get_live_weather"](ctx.origin, ctx.destination)
            c = AVAILABLE_TOOLS["get_alternate_route_cost"](ctx.destination)
            tool_outputs.append(f"Tool Result [get_live_weather]: {w}")
            tool_outputs.append(f"Tool Result [get_alternate_route_cost]: ${c}")
        except Exception as e:
            pass

        prompt = f"""You are a multi-agent logistics control intelligence. Evaluate this shipment:
- ID: {ctx.shipment_id}
- Delay Prob: {preds['delay_prob']:.2f}
- Traffic/Weather Risks: {ctx.traffic_risk:.2f} / {ctx.weather_risk:.2f}
- Hub Queue: {ctx.port_hub_queue_time_mins} mins
- Carrier Reliability: {ctx.carrier_reliability:.2f}

Historical FAISS Context: {mem}

Live Tool Execution Results: {tool_outputs}

Generate exactly the following JSON structure analyzing tradeoffs:
{{
    "decision": "<reroute | expedite | evaluate | none>",
    "action_plan": "<What action and why>",
    "reasoning_trace": "<Explain the top contributing factors and risks, mentioning tool results if relevant>",
    "confidence": <float 0-1>,
    "cost_impact_usd": <estimated cost, e.g. 500 for reroute, 0 for none>
}}
"""
        response_text = self.llm.generate(prompt)
        payload = self.llm.parse_json(response_text)
        
        # Fallback if parsing fails
        if not payload or 'decision' not in payload:
            payload = {
                "decision": "escalate_to_human",
                "action_plan": "Failed to parse LLM reasoning",
                "reasoning_trace": "LLM format error",
                "confidence": 0.0,
                "cost_impact_usd": 0.0
            }
        return {"llm_decision": payload, "tool_results": tool_outputs}

    def node_guardrails(self, state: GraphState):
        """Intercepts the LLM decision to enforce safety thresholds."""
        decision = state["llm_decision"]
        ctx = state["context"]
        
        final_decision = GuardrailManager.evaluate(decision, ctx)
        
        preds = state["ml_predictions"]
        
        final_output = {
            "shipment_id": ctx.shipment_id,
            "eta": preds["eta_mins"],
            "risk_score": preds["delay_prob"],
            "decision": final_decision["decision"],
            "action": final_decision["action_plan"],
            "reasoning": {
                "root_cause": final_decision["reasoning_trace"],
                "confidence": final_decision["confidence"],
                "evidence": [] # Could populate with FAISS ids
            }
        }
        
        # Ensure memory adds decision (Learning Loop step 1)
        self.memory_db.add_experience(state["raw_shipment_dict"], final_decision["decision"], "PENDING")
        
        return {"final_output": final_output}
