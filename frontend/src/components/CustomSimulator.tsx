import React, { useState } from 'react';
import './Dashboard.css';
import { PlusCircle } from 'lucide-react';
import { GlowingEffect } from './ui/glowing-effect';

interface CustomSimulatorProps {
  onSimulate: (data: any) => void;
  loading: boolean;
}

export function CustomSimulator({ onSimulate, loading }: CustomSimulatorProps) {
  const [formData, setFormData] = useState({
    origin: 'New York',
    destination: 'Los Angeles',
    distance_remaining_km: 1000,
    weather_risk: 0.1,
    traffic_risk: 0.1,
    port_hub_queue_time_mins: 30,
    carrier_reliability: 0.9,
    transport_mode: 'TRUCK',
    shipment_priority: 1,
    cost_constraints_usd: 1000
  });

  const handleChange = (e: React.ChangeEvent<HTMLSelectElement | HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: isNaN(Number(value)) ? value : Number(value) }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSimulate(formData);
  };

  return (
    <div className="relative rounded-[1.25rem] border-[0.75px] border-zinc-800 p-2 md:rounded-[1.5rem] md:p-3 list-none">
      <GlowingEffect
        spread={40}
        glow={true}
        disabled={false}
        proximity={64}
        inactiveZone={0.01}
        borderWidth={3}
      />
      <div className="relative h-full flex flex-col justify-between gap-6 overflow-hidden rounded-xl border-[0.75px] bg-[#09090b] p-6 shadow-sm md:p-6 z-10">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-fit rounded-lg border-[0.75px] border-zinc-800 bg-zinc-900 p-2">
            <PlusCircle size={32} color="#10b981" />
          </div>
          <div>
            <h3 className="text-xl font-semibold tracking-[-0.04em] text-white">Spawn Custom Shipment</h3>
            <p className="text-sm text-zinc-400">Define precise parameters to test agent edge cases.</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1fr) minmax(0, 1fr)', gap: '1rem' }} className="w-full">
          <div className="flex flex-col gap-2">
            <label className="text-zinc-400 text-sm font-medium">Origin</label>
            <select name="origin" value={formData.origin} onChange={handleChange} className="bg-zinc-900 border border-zinc-700 text-white p-2 rounded-md outline-none focus:border-emerald-500">
              <option value="New York">New York</option>
              <option value="Los Angeles">Los Angeles</option>
              <option value="Chicago">Chicago</option>
              <option value="Houston">Houston</option>
            </select>
          </div>
          <div className="flex flex-col gap-2">
            <label className="text-zinc-400 text-sm font-medium">Destination</label>
            <select name="destination" value={formData.destination} onChange={handleChange} className="bg-zinc-900 border border-zinc-700 text-white p-2 rounded-md outline-none focus:border-emerald-500">
              <option value="Seattle">Seattle</option>
              <option value="Miami">Miami</option>
              <option value="Denver">Denver</option>
              <option value="Boston">Boston</option>
            </select>
          </div>
          <div className="flex flex-col gap-2">
            <label className="text-zinc-400 text-sm font-medium">Weather Risk</label>
            <select name="weather_risk" value={formData.weather_risk} onChange={handleChange} className="bg-zinc-900 border border-zinc-700 text-white p-2 rounded-md outline-none focus:border-emerald-500">
              <option value={0.1}>Low (0.1)</option>
              <option value={0.5}>Medium (0.5)</option>
              <option value={0.9}>Severe (0.9)</option>
            </select>
          </div>
          <div className="flex flex-col gap-2">
            <label className="text-zinc-400 text-sm font-medium">Traffic Risk</label>
            <select name="traffic_risk" value={formData.traffic_risk} onChange={handleChange} className="bg-zinc-900 border border-zinc-700 text-white p-2 rounded-md outline-none focus:border-emerald-500">
              <option value={0.1}>Light (0.1)</option>
              <option value={0.5}>Moderate (0.5)</option>
              <option value={0.9}>Heavy (0.9)</option>
            </select>
          </div>
          <div className="flex flex-col gap-2">
            <label className="text-zinc-400 text-sm font-medium">Port/Hub Queue (Mins)</label>
            <select name="port_hub_queue_time_mins" value={formData.port_hub_queue_time_mins} onChange={handleChange} className="bg-zinc-900 border border-zinc-700 text-white p-2 rounded-md outline-none focus:border-emerald-500">
              <option value={30}>30 mins</option>
              <option value={60}>1 hour</option>
              <option value={120}>2 hours</option>
              <option value={240}>4 hours</option>
            </select>
          </div>
          <div className="flex flex-col gap-2">
            <label className="text-zinc-400 text-sm font-medium">Carrier Reliability</label>
            <select name="carrier_reliability" value={formData.carrier_reliability} onChange={handleChange} className="bg-zinc-900 border border-zinc-700 text-white p-2 rounded-md outline-none focus:border-emerald-500">
              <option value={0.9}>High (0.9)</option>
              <option value={0.5}>Average (0.5)</option>
              <option value={0.1}>Poor (0.1)</option>
            </select>
          </div>
          <div className="flex flex-col gap-2">
            <label className="text-zinc-400 text-sm font-medium">Transport Mode</label>
            <select name="transport_mode" value={formData.transport_mode} onChange={handleChange} className="bg-zinc-900 border border-zinc-700 text-white p-2 rounded-md outline-none focus:border-emerald-500">
              <option value="TRUCK">Truck</option>
              <option value="RAIL">Rail</option>
              <option value="AIR">Air</option>
              <option value="SEA">Sea</option>
            </select>
          </div>
          <div className="flex flex-col gap-2">
            <label className="text-zinc-400 text-sm font-medium">Distance Remaining (km)</label>
            <input type="number" name="distance_remaining_km" value={formData.distance_remaining_km} onChange={handleChange} className="bg-zinc-900 border border-zinc-700 text-white p-2 rounded-md outline-none focus:border-emerald-500" />
          </div>

          <button type="submit" disabled={loading} style={{ gridColumn: 'span 2' }} className={`mt-4 w-full py-3 rounded-lg font-bold transition-all ${loading ? 'bg-zinc-600 text-zinc-400 cursor-not-allowed' : 'bg-emerald-500 hover:bg-emerald-400 text-white shadow-[0_0_15px_rgba(16,185,129,0.5)]'}`}>
              {loading ? 'Initializing Agent...' : 'Spawn & Analyze Shipment'}
          </button>
        </form>
      </div>
    </div>
  );
}
