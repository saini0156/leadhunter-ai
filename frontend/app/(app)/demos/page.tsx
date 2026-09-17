import Link from "next/link";
import { ExternalLink, PanelsTopLeft } from "lucide-react";
import { leads } from "@/lib/data";

export default function DemosPage() {
  const demos=leads.filter(l=>l.demoStatus==="READY"||l.demoStatus==="PENDING");
  return (
    <main className="page">
      <div className="page-header"><div><div className="page-title">Demo Websites</div><div className="page-description">Generated customer-facing previews for qualified leads.</div></div><span className="badge badge-blue">{demos.length} in queue</span></div>
      <div className="grid-3">
        {demos.map(l=><div className="panel" key={l.id}>
          <div style={{height:145,background:"linear-gradient(135deg,#151a32,#34327a)",display:"grid",placeItems:"center",color:"#fff"}}><PanelsTopLeft size={38} opacity={.8}/></div>
          <div style={{padding:17}}><div className="business-name">{l.name}</div><div className="business-meta">{l.city}</div><div style={{display:"flex",gap:7,marginTop:13}}><span className={`badge ${l.demoStatus==="READY"?"badge-green":"badge-gray"}`}>{l.demoStatus}</span><span className={`badge badge-${l.tier.toLowerCase()}`}>{l.tier}</span></div><div style={{display:"flex",gap:7,marginTop:15}}>{l.demoUrl&&<a className="primary-btn" href={l.demoUrl} target="_blank" rel="noreferrer"><ExternalLink size={12}/> Open Demo</a>}<Link className="secondary-btn" href={`/leads/${l.id}`}>Details</Link></div></div>
        </div>)}
      </div>
    </main>
  );
}