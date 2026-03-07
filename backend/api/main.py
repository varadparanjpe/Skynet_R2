from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from backend.simulator.simulator import LogisticsSimulator
from fastapi.middleware.cors import CORSMiddleware
import traceback

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
simulator = LogisticsSimulator()

# Initialize LangGraph globally but lazily
graph_agent = None
audit_logger = None

def get_agent():
    global graph_agent, audit_logger
    if graph_agent is None:
        from backend.agent.graph import AgentWorkflow
        from backend.learning.audit_logger import AuditLogger
        graph_agent = AgentWorkflow()
        audit_logger = AuditLogger()
    return graph_agent, audit_logger

class CustomShipmentRequest(BaseModel):
    origin: str
    destination: str
    distance_remaining_km: float
    weather_risk: float
    traffic_risk: float
    port_hub_queue_time_mins: int
    carrier_reliability: float
    transport_mode: str
    shipment_priority: int
    cost_constraints_usd: float

class ActRequest(BaseModel):
    shipment_id: int
    decision: str
    
class LearnRequest(BaseModel):
    shipment_id: int
    outcome: str # "SUCCESS" or "DELAYED"

@app.get("/simulate")
def simulate():
    """Generates a random state shipment and runs reasoning"""
    _, _ = get_agent() # Ensure init
    shipment = simulator.generate_random_event()
    return _process_shipment_with_agent(shipment)

@app.post("/custom_simulate")
def custom_simulate(req: CustomShipmentRequest):
    """Spawns a custom shipment created by the User UI"""
    shipment = simulator.create_custom_shipment(req.model_dump())
    return _process_shipment_with_agent(shipment)

def _process_shipment_with_agent(shipment: dict):
    agent, audit = get_agent()
    try:
        result = agent.run(shipment)
        
        # If the agent made an autonomous action, execute it in the simulator (The ACT Loop)
        if result["decision"] in ["reroute", "expedite"]:
             shipment = simulator.execute_action(shipment["shipment_id"], result["decision"])
             
        # Log to SQLite
        audit.log_decision(
            shipment_id=shipment["shipment_id"],
            context=shipment,
            prob=result["risk_score"],
            reasoning=result["reasoning"]["root_cause"],
            decision=result["decision"],
            confidence=result["reasoning"]["confidence"],
            cost=500.0 if result["decision"] != "none" else 0.0
        )

        return {"shipment": shipment, "result": result}
    except Exception as e:
        print(f"Agent Error: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/operator_action")
def operator_action(req: ActRequest):
    """The HITL endpoint where a human forces an action on an escalated shipment"""
    updated_shipment = simulator.execute_action(req.shipment_id, req.decision)
    if "error" in updated_shipment:
        raise HTTPException(status_code=404, detail="Shipment not active.")
        
    _, audit = get_agent()
    # Log human override
    audit.log_decision(req.shipment_id, updated_shipment, 1.0, "Human Override Triggered", req.decision, 1.0, 0.0)
    
    return {"status": "success", "updated_shipment": updated_shipment}

@app.post("/resolve_shipment")
def resolve_shipment(req: LearnRequest):
    """The LEARN Loop: Closes out a shipment and writes result to FAISS Vectors"""
    final_shipment = simulator.resolve_shipment(req.shipment_id)
    if not final_shipment:
        raise HTTPException(status_code=404, detail="Shipment not found in simulator memory.")
        
    agent, audit = get_agent()
    
    # Push the exact context and the final outcome to FAISS
    # Next time a similar context arises, the agent will see if this outcome was SUCCESS or DELAYED.
    agent.memory_db.add_experience(final_shipment, "RESOLVED", req.outcome)
    
    return {"status": "success", "message": f"Learned from shipment {req.shipment_id}"}

