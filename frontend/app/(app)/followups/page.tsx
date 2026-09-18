import { CalendarClock, CheckCircle2, Clock3 } from "lucide-react";
import { leads } from "../../../lib/data";

export default function FollowupsPage() {
  return (
    <main className="page">
      <div className="page-header"><div><div className="page-title">Follow-ups</div><div className="page-description">Manage automated follow-up sequences for contacted leads.</div></div><button className="primary-btn"><CalendarClock size={14}/> Schedule Follow-up</button></div>
      <div className="grid-3" style={{marginBottom:20}}>
        {[
          { label: "Due Today", value: "7", icon: Clock3 },
          { label: "Scheduled", value: "19", icon: CalendarClock },
          { label: "Completed", value: "34", icon: CheckCircle2 },
        ].map(({ label, value, icon: Icon }) => (
          <div className="kpi-card" key={label}>
            <div className="kpi-top">
              <div>
                <div className="kpi-label">{label}</div>
                <div className="kpi-value">{value}</div>
              </div>
              <div className="kpi-icon"><Icon size={18}/></div>
            </div>
          </div>
        ))}
      </div>
      <div className="panel"><div className="table-wrap"><table><thead><tr><th>Lead</th><th>Sequence</th><th>Next Action</th><th>Due</th><th>Status</th><th /></tr></thead><tbody>
        {leads.filter(l=>l.qualified).map((l,i)=><tr key={l.id}><td><div className="business-name">{l.name}</div><div className="business-meta">Lead #{l.id}</div></td><td className="cell-text">Website + SEO Outreach</td><td className="cell-text">Follow-up #{i+1}</td><td className="business-meta">{i<2?"Today":"Tomorrow"}</td><td><span className={`badge ${i<2?"badge-green":"badge-gray"}`}>{i<2?"DUE":"SCHEDULED"}</span></td><td><button className="secondary-btn" style={{height:31}}>Manage</button></td></tr>)}
      </tbody></table></div></div>
    </main>
  );
}