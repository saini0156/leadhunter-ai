import { Mail, MessageCircle, Send, CheckCircle2 } from "lucide-react";
import { leads } from "@/lib/data";

export default function OutreachPage() {
  const ready=leads.filter(l=>l.qualified);
  return (
    <main className="page">
      <div className="page-header"><div><div className="page-title">Outreach</div><div className="page-description">Review personalized messages and control outbound communication.</div></div><button className="primary-btn"><Send size={14}/> Create Campaign</button></div>
      <div className="kpi-grid">
        {[["Ready to Send",12,"Approved leads"],["Email",31,"Messages generated"],["WhatsApp",22,"Messages generated"],["Sent",18,"This month"]].map(([a,b,c])=><div className="kpi-card" key={String(a)}><div className="kpi-label">{a}</div><div className="kpi-value">{b}</div><div className="muted" style={{fontSize:10,marginTop:5}}>{c}</div></div>)}
      </div>
      <div className="panel">
        <div className="table-wrap"><table><thead><tr><th>Lead</th><th>Channel</th><th>Subject / Preview</th><th>Status</th><th /></tr></thead><tbody>
          {ready.map(l=><tr key={l.id}><td><div className="business-name">{l.name}</div><div className="business-meta">{l.city}</div></td><td><div style={{display:"flex",gap:5}}><span className="badge badge-blue"><Mail size={10}/> Email</span><span className="badge badge-green"><MessageCircle size={10}/> WhatsApp</span></div></td><td><div className="cell-text">{l.emailSubject}</div></td><td><span className="badge badge-gray">PENDING APPROVAL</span></td><td><button className="secondary-btn" style={{height:31}}><CheckCircle2 size={12}/> Review</button></td></tr>)}
        </tbody></table></div>
      </div>
    </main>
  );
}