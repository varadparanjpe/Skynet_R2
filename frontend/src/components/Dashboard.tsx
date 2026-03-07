import React from 'react';
import './Dashboard.css';
import { 
  Package, Map, Activity, Layers, Droplets, 
  AlertTriangle, CheckCircle, Zap, Cpu, Route
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface ShipmentData {
  shipment_id: number;
  origin: string;
  destination: string;
  distance_remaining_km: number;
  weather_risk: number;
  traffic_risk: number;
  port_hub_queue_time_mins: number;
  carrier_reliability: number;
  transport_mode: string;
  shipment_priority: number;
  cost_constraints_usd: number;
}

interface AgentResult {
  shipment_id: number;
  eta: number;
  risk_score: number;
  decision: string;
  action: string | null;
  reasoning: {
    root_cause: string;
    confidence: number;
    evidence: any[];
  };
}

export function Dashboard({ 
  data, 
  loading, 
  onOperatorAction, 
  onResolve, 
  onNextRandom 
}: { 
  data: { shipment: ShipmentData, result: AgentResult } | null,
  loading: boolean,
  onOperatorAction: (id: number, decision: string) => void,
  onResolve: (id: number, outcome: string) => void,
  onNextRandom: () => void
}) {
  const navigate = useNavigate();

  if (loading || !data) {
    return (
      <div className="loading-container" style={{ margin: '4rem auto' }}>
        <div className="spinner"></div>
        <p style={{ fontSize: '1.25rem', fontWeight: 500, color: '#a1a1aa' }}>LangGraph ReAct Execution in Progress...</p>
      </div>
    );
  }

  const { shipment, result } = data;

  const toPercent = (val: number) => `${(val * 100).toFixed(1)}%`;

  return (
    <div className="dashboard-container" id="dashboard">
      <div className="dashboard-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2 className="dashboard-title">
          <Activity size={32} color="#a855f7" /> 
          Live Operations Overview
        </h2>
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <button 
            onClick={() => navigate('/human-control')}
            style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', background: 'transparent', border: '1px solid #ef4444', color: '#ef4444', padding: '0.5rem 1rem', borderRadius: '0.5rem', cursor: 'pointer', fontWeight: 'bold' }}
          >
            <AlertTriangle size={18} /> Human Control Panel
          </button>
          <div className="status-badge" style={{ backgroundColor: 'rgba(34, 197, 94, 0.2)', color: '#4ade80', border: '1px solid #22c55e' }}>
            LangGraph Agent Active
          </div>
        </div>
      </div>

      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-header">
            <span>Shipment Route</span>
            <Route size={20} color="#a1a1aa" />
          </div>
          <div className="metric-value" style={{ fontSize: '1.25rem' }}>{shipment.origin} → {shipment.destination}</div>
          <div style={{ color: '#a1a1aa', fontSize: '0.875rem', marginTop: '0.5rem' }}>
            ID: #{shipment.shipment_id} • {shipment.transport_mode} • Priority: {shipment.shipment_priority}
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-header">
            <span>Distance Remaining</span>
            <Map size={20} color="#a1a1aa" />
          </div>
          <div className="metric-value">{shipment.distance_remaining_km.toFixed(1)} km</div>
          <div className="progress-bar-bg">
            <div className="progress-bar-fill" style={{ width: `${Math.min((shipment.distance_remaining_km / 2000) * 100, 100)}%`, background: '#3b82f6' }}></div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-header">
            <span>Risk Factors (Weather / Traffic)</span>
            <AlertTriangle size={20} color="#a1a1aa" />
          </div>
          <div className="metric-value">{toPercent(shipment.weather_risk)} / {toPercent(shipment.traffic_risk)}</div>
          <div className="progress-bar-bg">
            <div className="progress-bar-fill" style={{ width: toPercent(Math.max(shipment.weather_risk, shipment.traffic_risk)), background: Math.max(shipment.weather_risk, shipment.traffic_risk) > 0.6 ? '#eab308' : '#3b82f6' }}></div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-header">
            <span>Carrier Reliability</span>
            <CheckCircle size={20} color="#a1a1aa" />
          </div>
          <div className="metric-value">{toPercent(shipment.carrier_reliability)}</div>
          <div className="progress-bar-bg">
            <div className="progress-bar-fill" style={{ width: toPercent(shipment.carrier_reliability), background: shipment.carrier_reliability > 0.8 ? '#22c55e' : '#f97316' }}></div>
          </div>
        </div>
      </div>

      <div className="agent-decision-panel">
        <div className="decision-header">
          <Cpu size={28} color="#ec4899" />
          Agent Reasoning Output
        </div>
        
        <div className="decision-content">
          <div className="decision-block">
            <div className="decision-label">Predicted ETA (Machine Learning)</div>
            <div className="decision-value" style={{ fontSize: '2.5rem', color: '#10b981' }}>
              {result.eta.toFixed(0)} mins
            </div>
            
            <div className="decision-label" style={{ marginTop: '1.5rem' }}>Delay Probability</div>
            <div className="decision-value" style={{ color: result.risk_score > 0.5 ? '#ef4444' : '#eab308' }}>
              {toPercent(result.risk_score)}
            </div>
          </div>

          <div className="decision-block">
            <div className="decision-label" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span>Recommended Action</span>
                <span className="status-badge" style={{ backgroundColor: 'rgba(236, 72, 153, 0.2)', color: '#ec4899', fontSize: '0.75rem', padding: '0.2rem 0.5rem' }}>
                    Confidence: {toPercent(result.reasoning.confidence)}
                </span>
            </div>
            <div className="decision-value" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#60a5fa' }}>
              <Zap size={20} />
              {result.decision.toUpperCase() || 'NO ACTION NEEDED'}
            </div>
            {result.action && (
              <p style={{ marginTop: '0.5rem', color: '#e4e4e7', fontStyle: 'italic', background: 'rgba(0,0,0,0.2)', padding: '0.75rem', borderRadius: '0.5rem', borderLeft: '3px solid #60a5fa' }}>
                {result.action}
              </p>
            )}

            <div className="decision-label" style={{ marginTop: '1.5rem' }}>Reasoning Trace (LLM Context + memory)</div>
            <div className="decision-value" style={{ fontSize: '1rem', lineHeight: '1.5', color: '#d4d4d8' }}>
              {result.reasoning.root_cause} 
            </div>
            
            {result.decision === "escalate_to_human" && (
                <div style={{ marginTop: '2rem', padding: '1rem', border: '1px solid #ef4444', borderRadius: '0.5rem', background: 'rgba(239, 68, 68, 0.1)' }}>
                    <h3 style={{ color: '#ef4444', margin: 0, marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <AlertTriangle size={20} />
                        Human Intervention Required
                    </h3>
                    <div style={{ display: 'flex', gap: '1rem' }}>
                        <button onClick={() => onOperatorAction(shipment.shipment_id, "reroute")} style={{ background: '#3b82f6', color: 'white', padding: '0.5rem 1rem', borderRadius: '0.25rem', border: 'none', cursor: 'pointer' }}>Force Reroute</button>
                        <button onClick={() => onOperatorAction(shipment.shipment_id, "expedite")} style={{ background: '#8b5cf6', color: 'white', padding: '0.5rem 1rem', borderRadius: '0.25rem', border: 'none', cursor: 'pointer' }}>Force Expedite</button>
                        <button onClick={() => onOperatorAction(shipment.shipment_id, "none")} style={{ background: '#71717a', color: 'white', padding: '0.5rem 1rem', borderRadius: '0.25rem', border: 'none', cursor: 'pointer' }}>Dismiss</button>
                    </div>
                </div>
            )}
            
            <div style={{ marginTop: '2rem', paddingTop: '1.5rem', borderTop: '1px solid #27272a', display: 'flex', justifyContent: 'space-between', gap: '1rem' }}>
                 <div style={{ display: 'flex', gap: '1rem' }}>
                    <button onClick={() => onResolve(shipment.shipment_id, "SUCCESS")} style={{ background: 'transparent', color: '#22c55e', border: '1px solid #22c55e', padding: '0.5rem 1rem', borderRadius: '0.25rem', cursor: 'pointer' }}>Learn: Mark Success</button>
                    <button onClick={() => onResolve(shipment.shipment_id, "DELAYED")} style={{ background: 'transparent', color: '#ef4444', border: '1px solid #ef4444', padding: '0.5rem 1rem', borderRadius: '0.25rem', cursor: 'pointer' }}>Learn: Mark Delayed</button>
                 </div>
                 <button onClick={onNextRandom} style={{ background: '#a855f7', color: 'white', border: 'none', padding: '0.5rem 1.5rem', borderRadius: '0.25rem', cursor: 'pointer', fontWeight: 'bold' }}>Simulate Next Ticket ➞</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
