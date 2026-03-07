from pydantic import BaseModel, Field
from typing import Optional, List

class ShipmentContext(BaseModel):
    """
    Standardized schema for all shipment data entering the Intelligence Layer.
    This enforces Data Integrity Validation (Guardrail 4).
    """
    shipment_id: int = Field(..., description="Unique identifier for the shipment")
    
    # Core Operations Data
    origin: str = Field(..., description="Origin location")
    destination: str = Field(..., description="Destination location")
    distance_remaining_km: float = Field(..., ge=0, description="Distance remaining to destination")
    
    # External Signals (Simulated)
    weather_risk: float = Field(..., ge=0.0, le=1.0, description="0 to 1 score of adverse weather")
    traffic_risk: float = Field(..., ge=0.0, le=1.0, description="0 to 1 score of traffic congestion")
    port_hub_queue_time_mins: int = Field(..., ge=0, description="Expected wait time at next hub")
    
    # Carrier Attributes
    carrier_reliability: float = Field(..., ge=0.0, le=1.0, description="Historical on-time score of carrier")
    transport_mode: str = Field(default="TRUCK", description="TRUCK, RAIL, AIR, or SEA")
    
    # Business Constraints
    shipment_priority: int = Field(default=1, ge=1, le=5, description="1=Low, 5=Critical")
    cost_constraints_usd: float = Field(default=1000.0, ge=0.0, description="Max acceptable added cost")

    # Outputs calculated downstream by ML pipeline
    delay_probability: Optional[float] = Field(None, ge=0.0, le=1.0)
    predicted_eta_mins: Optional[float] = Field(None, ge=0.0)

class DecisionAuditLog(BaseModel):
    """
    Schema for Logging decisions (Guardrail 7).
    """
    shipment_id: int
    predicted_delay_prob: float
    reasoning: str
    decision: str
    confidence: float
    cost_impact: float
    timestamp: str

def validate_shipment(raw_data: dict) -> ShipmentContext:
    """
    Validates a raw dictionary into a strict ShipmentContext object.
    Raises ValueError if data violates integrity constraints.
    """
    return ShipmentContext(**raw_data)
