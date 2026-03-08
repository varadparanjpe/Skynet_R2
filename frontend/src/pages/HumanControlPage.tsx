import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { ArrowLeft, GitMerge, AlertCircle, ShieldAlert } from 'lucide-react';
import { GlowingEffect } from '../components/ui/glowing-effect';

export default function HumanControlPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [shipmentIdInput, setShipmentIdInput] = useState(searchParams.get("shipment_id") || "");
  const [decision, setDecision] = useState("reroute");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const sid = searchParams.get("shipment_id");
    if (sid) {
       setShipmentIdInput(sid);
    }
  }, [searchParams]);

  const handleManualIntervention = (e: React.FormEvent) => {
    e.preventDefault();
    if (!shipmentIdInput) return;
    setLoading(true);

    fetch("http://127.0.0.1:8000/operator_action", {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ shipment_id: Number(shipmentIdInput), decision })
    })
    .then(async (r) => {
      if (!r.ok) {
        alert("Failed to update shipment. Make sure the ID is currently active in the simulator.");
      } else {
        alert(`Successfully forced ${decision.toUpperCase()} on Shipment ${shipmentIdInput}`);
        setShipmentIdInput("");
      }
    })
    .catch(() => alert("Network error connecting to backend."))
    .finally(() => setLoading(false));
  };

  return (
    <div className="min-h-screen bg-[#09090b] text-white p-8">
      <button 
        onClick={() => navigate('/')} 
        className="flex items-center gap-2 text-zinc-400 hover:text-white mb-8 transition-colors"
      >
        <ArrowLeft size={20} /> Back to Dashboard
      </button>

      <div className="max-w-3xl mx-auto">
        <div className="flex items-center gap-4 mb-8">
          <div className="p-3 bg-red-500/10 rounded-xl border border-red-500/20">
            <ShieldAlert size={40} className="text-red-500" />
          </div>
          <div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-red-400 to-orange-500 bg-clip-text text-transparent">
              Human-in--loop Intervention
            </h1>
            <p className="text-zinc-400 mt-2">Force systemic overrides on active agentic workflows.</p>
          </div>
        </div>

        <div className="relative rounded-[1.5rem] border-[0.75px] border-zinc-800 p-2 md:p-3 list-none">
          <GlowingEffect
            spread={40}
            glow={true}
            disabled={false}
            proximity={64}
            inactiveZone={0.01}
            borderWidth={3}
          />
          <div className="relative z-10 bg-[#09090b] rounded-xl border-[0.75px] border-zinc-800 p-8 shadow-sm">
            
            <div className="flex items-center gap-3 mb-6 p-4 bg-orange-500/10 border border-orange-500/20 rounded-lg text-orange-400 text-sm">
              <AlertCircle size={20} />
              Warning: Direct human intervention bypasses all standard AI Guardrails including Confidence and Cost Thresholds.
            </div>

            <form onSubmit={handleManualIntervention} className="space-y-6">
              <div className="space-y-2">
                <label className="text-sm font-medium text-zinc-300">Target Shipment ID</label>
                <input 
                  type="number" 
                  value={shipmentIdInput}
                  onChange={(e) => setShipmentIdInput(e.target.value)}
                  placeholder="e.g. 1024"
                  required
                  className="w-full bg-zinc-900 border border-zinc-700 text-white px-4 py-3 rounded-lg focus:outline-none focus:border-red-500 focus:ring-1 focus:ring-red-500 transition-all font-mono"
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-zinc-300">Force Operational Action</label>
                <select 
                  value={decision}
                  onChange={(e) => setDecision(e.target.value)}
                  className="w-full bg-zinc-900 border border-zinc-700 text-white px-4 py-3 rounded-lg focus:outline-none focus:border-red-500 focus:ring-1 focus:ring-red-500 transition-all"
                >
                  <option value="reroute">Emergency Reroute (Avoid Weather/Traffic)</option>
                  <option value="expedite">Expedite Priority (Jump Hub Queue)</option>
                  <option value="none">Hold Order (Do Nothing)</option>
                </select>
              </div>

              <button 
                type="submit" 
                disabled={loading || !shipmentIdInput}
                className={`w-full flex items-center justify-center gap-2 py-4 rounded-lg font-bold transition-all text-lg ${
                  loading || !shipmentIdInput 
                    ? 'bg-zinc-800 text-zinc-500 cursor-not-allowed' 
                    : 'bg-gradient-to-r from-red-600 to-red-500 hover:from-red-500 hover:to-red-400 text-white shadow-[0_0_20px_rgba(239,68,68,0.4)]'
                }`}
              >
                <GitMerge size={24} />
                {loading ? 'Executing Central Override...' : 'EXECUTE OVERRIDE'}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}
