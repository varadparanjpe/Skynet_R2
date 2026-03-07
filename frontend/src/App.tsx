import { useEffect, useState } from "react"
import { Routes, Route } from "react-router-dom"
import { HeroSection } from "./components/ui/hero-section-dark"
import { Dashboard } from "./components/Dashboard"
import { CustomSimulator } from "./components/CustomSimulator"
import HumanControlPage from "./pages/HumanControlPage"

export default function App() {
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  const fetchRandomSimulate = () => {
    setLoading(true)
    fetch("http://127.0.0.1:8000/simulate")
      .then(r => r.json())
      .then(setData)
      .finally(() => setLoading(false))
  }

  const handleCustomSimulate = (customData: any) => {
    setLoading(true)
    fetch("http://127.0.0.1:8000/custom_simulate", {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(customData)
    })
      .then(r => r.json())
      .then(setData)
      .finally(() => setLoading(false))
  }

  const handleOperatorAction = (shipment_id: number, decision: string) => {
    fetch("http://127.0.0.1:8000/operator_action", {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ shipment_id, decision })
    })
    .then(r => r.json())
    .then(res => {
        setData((prev: any) => ({
            ...prev,
            shipment: res.updated_shipment,
            result: { ...prev.result, decision: decision + " (HUMAN OVERRIDE)" }
        }))
    });
  }

  const handleResolve = (shipment_id: number, outcome: string) => {
    fetch("http://127.0.0.1:8000/resolve_shipment", {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ shipment_id, outcome })
    }).then(async (r) => {
        if (!r.ok) {
            console.error("Learn backend failed:", await r.text());
            alert("Error saving outcome to memory.");
        } else {
            alert("Shipment Outcome Learned & Saved to FAISS Vector DB.");
            fetchRandomSimulate();
        }
    });
  }

  useEffect(() => {
    fetchRandomSimulate()
  }, [])

  const handleLaunch = () => {
    const dashboardElement = document.getElementById("dashboard");
    if (dashboardElement) {
      dashboardElement.scrollIntoView({ behavior: 'smooth' });
    } else {
      window.scrollTo({ top: window.innerHeight, behavior: 'smooth' });
    }
  }

  return (
    <Routes>
      <Route path="/" element={
        <div style={{ backgroundColor: '#09090b', minHeight: '100vh', paddingBottom: '4rem' }}>
          <HeroSection onLaunch={handleLaunch} />
          
          <div style={{ maxWidth: '1200px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '2rem' }}>
              <Dashboard 
                data={data} 
                loading={loading}
                onOperatorAction={handleOperatorAction}
                onResolve={handleResolve}
                onNextRandom={fetchRandomSimulate}
              />
              
              <CustomSimulator onSimulate={handleCustomSimulate} loading={loading} />
          </div>
        </div>
      } />
      <Route path="/human-control" element={<HumanControlPage />} />
    </Routes>
  )
}
