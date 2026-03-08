import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Layers, ShieldAlert, CheckCircle2 } from 'lucide-react';
import { GlowingEffect } from '../components/ui/glowing-effect';

interface AuditLog {
  id: number;
  shipment_id: number;
  timestamp: string;
  decision: string;
  confidence: number;
  reasoning: string;
  cost_impact_usd: number;
  actual_outcome: string | null;
  predicted_delay_prob: number;
}

export function TransactionLogsPage() {
  const navigate = useNavigate();
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/audit_logs")
      .then(res => res.json())
      .then(data => {
        setLogs(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to fetch logs", err);
        setLoading(false);
      });
  }, []);

  return (
    <div className="min-h-screen bg-[#09090b] text-white p-8">
      <button 
        onClick={() => navigate('/')} 
        className="flex items-center gap-2 text-zinc-400 hover:text-white mb-8 transition-colors"
      >
        <ArrowLeft size={20} /> Back to Dashboard
      </button>

      <div className="max-w-7xl mx-auto">
        <div className="flex items-center gap-4 mb-8">
          <div className="p-3 bg-blue-500/10 rounded-xl border border-blue-500/20">
            <Layers size={40} className="text-blue-500" />
          </div>
          <div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-indigo-500 bg-clip-text text-transparent">
              Immutable Transaction Audit Logs
            </h1>
            <p className="text-zinc-400 mt-2">Historical ledger of all AI Agent decisions, guardrail escalations, and Human-in-the-Loop overrides.</p>
          </div>
        </div>

        <div className="relative rounded-[1.5rem] border-[0.75px] border-zinc-800 p-2 list-none">
          <GlowingEffect
            spread={40}
            glow={true}
            disabled={loading}
            proximity={64}
            inactiveZone={0.01}
            borderWidth={3}
          />
          <div className="relative z-10 bg-[#121214] rounded-xl border-[0.75px] border-zinc-800 overflow-hidden shadow-sm">
            {loading ? (
              <div className="p-12 text-center text-zinc-500 font-mono">Loading securely from SQLite database...</div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm whitespace-nowrap">
                  <thead className="bg-[#18181b] border-b border-zinc-800 text-zinc-400 uppercase text-xs font-semibold">
                    <tr>
                      <th className="px-6 py-4">Transaction ID</th>
                      <th className="px-6 py-4">Shipment</th>
                      <th className="px-6 py-4">Timestamp (UTC)</th>
                      <th className="px-6 py-4">Decision</th>
                      <th className="px-6 py-4">AI Confidence</th>
                      <th className="px-6 py-4">Cost Auth (USD)</th>
                      <th className="px-6 py-4">Agent Reasoning</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-zinc-800">
                    {logs.map(log => {
                      const isHuman = log.decision.includes("HUMAN");
                      const isEscalate = log.decision === "escalate_to_human";
                      return (
                        <tr key={log.id} className="hover:bg-[#1f1f22] transition-colors">
                          <td className="px-6 py-4 font-mono text-zinc-300">TXN-{log.id.toString().padStart(4, '0')}</td>
                          <td className="px-6 py-4 font-mono text-blue-400">SHP-{log.shipment_id}</td>
                          <td className="px-6 py-4 text-zinc-500">{new Date(log.timestamp).toLocaleString()}</td>
                          <td className="px-6 py-4">
                            <span className={`px-2 py-1 rounded text-xs font-bold border ${
                              isHuman ? 'bg-orange-500/20 text-orange-400 border-orange-500/30' :
                              isEscalate ? 'bg-red-500/20 text-red-400 border-red-500/30' :
                              log.decision === 'none' ? 'bg-zinc-800 text-zinc-300 border-zinc-700' :
                              'bg-green-500/20 text-green-400 border-green-500/30'
                            }`}>
                              {isHuman ? <ShieldAlert size={12} className="inline mr-1"/> : null}
                              {log.decision.toUpperCase().substring(0, 20)}
                            </span>
                          </td>
                          <td className="px-6 py-4 font-mono">{(log.confidence * 100).toFixed(1)}%</td>
                          <td className="px-6 py-4 font-mono text-zinc-300">${log.cost_impact_usd.toFixed(2)}</td>
                          <td className="px-6 py-4 text-zinc-400 max-w-sm truncate" title={log.reasoning}>
                            {log.reasoning}
                          </td>
                        </tr>
                      );
                    })}
                    {logs.length === 0 && (
                      <tr>
                        <td colSpan={7} className="px-6 py-8 text-center text-zinc-500">
                          No transactions found in the SQLite ledger. Try simulating a shipment first.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
