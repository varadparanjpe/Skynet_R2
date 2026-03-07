from sqlalchemy import create_engine, Column, Integer, Float, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import json
import os

Base = declarative_base()

class DecisionRecord(Base):
    __tablename__ = 'decision_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    shipment_id = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Inputs
    shipment_context_json = Column(Text, nullable=False)
    predicted_delay_prob = Column(Float, nullable=False)
    
    # Outputs
    agent_reasoning = Column(Text, nullable=False)
    decision = Column(String(50), nullable=False)
    confidence = Column(Float, nullable=False)
    cost_impact_usd = Column(Float, default=0.0)

    # Learning Loop Feedback
    actual_outcome = Column(String(50), nullable=True) # e.g. "SUCCESS", "DELAYED"
    human_override = Column(String(50), nullable=True)

class AuditLogger:
    """
    Handles Guardrail 7 (Decision Logging & Auditability) and the Learning Loop feedback.
    """
    def __init__(self, db_path="sqlite:///backend/learning/audit_logs.db"):
        os.makedirs('backend/learning', exist_ok=True)
        self.engine = create_engine(db_path, connect_args={"check_same_thread": False})
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def log_decision(self, shipment_id: int, context: dict, prob: float, reasoning: str, decision: str, confidence: float, cost: float):
        db = self.SessionLocal()
        try:
            record = DecisionRecord(
                shipment_id=shipment_id,
                shipment_context_json=json.dumps(context),
                predicted_delay_prob=prob,
                agent_reasoning=reasoning,
                decision=decision,
                confidence=confidence,
                cost_impact_usd=cost
            )
            db.add(record)
            db.commit()
            return record.id
        finally:
            db.close()
            
    def query_recent_decisions(self, limit=10):
        db = self.SessionLocal()
        try:
            return db.query(DecisionRecord).order_by(DecisionRecord.timestamp.desc()).limit(limit).all()
        finally:
            db.close()
