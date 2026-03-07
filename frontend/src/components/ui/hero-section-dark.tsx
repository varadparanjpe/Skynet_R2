import { ChevronRight } from "lucide-react"

export function HeroSection({ onLaunch }: { onLaunch: () => void }){

return (

<div style={{
height:"100vh",
display:"flex",
alignItems:"center",
justifyContent:"center",
background:"linear-gradient(to bottom, #111, #000)",
color:"white",
flexDirection:"column"
}}>

<h1 style={{fontSize:48, fontWeight: 700, margin: 0}}>AI Logistics Control Tower</h1>

<p style={{ color: '#a1a1aa', fontSize: '1.25rem', marginTop: '1rem' }}>Agentic AI for Supply Chain Operations</p>

<button 
  onClick={onLaunch}
  style={{
    marginTop: 40,
    padding:"14px 28px",
    background:"#7c3aed",
    border: 'none',
    color: 'white',
    fontSize: '1rem',
    fontWeight: '600',
    borderRadius: 12,
    display:"flex",
    alignItems:"center",
    gap: 8,
    cursor: "pointer",
    boxShadow: "0 4px 14px 0 rgba(124, 58, 237, 0.39)",
    transition: "transform 0.2s ease"
  }}
  onMouseOver={(e) => e.currentTarget.style.transform = 'scale(1.05)'}
  onMouseOut={(e) => e.currentTarget.style.transform = 'scale(1)'}
>
Launch Dashboard
<ChevronRight size={20}/>
</button>

</div>

)
}
