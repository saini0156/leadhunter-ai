import Link from "next/link";
import { ArrowUpRight, CheckCircle2, Globe2, Mail, PanelsTopLeft, Search, Users } from "lucide-react";
import { activities, leads } from "@/lib/data";

const bars = [32, 47, 39, 61, 48, 72, 55, 82, 67, 90, 76, 96];

export default function DashboardPage() {
  const qualified = leads.filter(x => x.qualified).length;
  const hot = leads.filter(x => x.tier === "HOT").length;
  const noWebsite = leads.filter(x => x.websiteStatus === "No Website").length;

  return (
    <main className="page">
      <div className="page-header">
        <div>
          <div className="page-title">Good morning 👋</div>
          <div className="page-description">Here&apos;s what&apos;s happening with your lead generation today.</div>
        </div>
        <Link className="primary-btn" href="/discover"><Search size={15} /> Discover Leads</Link>
      </div>

      <div className="kpi-grid">
        {[
          { label: "Total Leads", value: "248", change: "+18.4%", foot: "vs last month", icon: Users },
          { label: "Qualified Leads", value: String(qualified + 80), change: "+12.8%", foot: "34.7% qualification rate", icon: CheckCircle2 },
          { label: "Demo Websites", value: "42", change: "+9.2%", foot: "12 awaiting approval", icon: PanelsTopLeft },
          { label: "Enquiries", value: "17", change: "+24.1%", foot: "from generated demos", icon: Mail }
        ].map(({ label, value, change, foot, icon: Icon }) => (
          <div className="kpi-card" key={label}>
            <div className="kpi-top">
              <div>
                <div className="kpi-label">{label}</div>
                <div className="kpi-value">{value}</div>
              </div>
              <div className="kpi-icon"><Icon size={18} /></div>
            </div>
            <div className="kpi-foot"><span className="up">{change}</span><span className="muted">{foot}</span></div>
          </div>
        ))}
      </div>

      <div className="grid-2">
        <section className="panel">
          <div className="panel-header">
            <div><div className="panel-title">Lead Pipeline</div><div className="panel-subtitle">Current lead distribution</div></div>
            <select className="select"><option>Last 30 days</option><option>Last 7 days</option><option>This year</option></select>
          </div>
          <div className="chart">
            <div className="chart-bars">
              {bars.map((height, i) => <div className="bar-wrap" key={i}><div className="bar" style={{ height: `${height}%` }} /></div>)}
            </div>
            <div className="chart-labels">{["Apr","","","May","","","Jun","","","Sep","",""].map((x,i)=><span key={i}>{x}</span>)}</div>
          </div>
        </section>

        <section className="panel">
          <div className="panel-header">
            <div><div className="panel-title">Recent Activity</div><div className="panel-subtitle">Latest automation events</div></div>
          </div>
          <div className="activity-list">
            {activities.map(([icon,title,business,time]) => (
              <div className="activity" key={title + business}>
                <div className="activity-icon">{icon}</div>
                <div className="activity-main"><div className="activity-title">{title}</div><div className="activity-business">{business}</div></div>
                <div className="activity-time">{time}</div>
              </div>
            ))}
          </div>
        </section>
      </div>

      <section className="panel table-panel">
        <div className="panel-header">
          <div><div className="panel-title">Priority Leads</div><div className="panel-subtitle">Highest scoring leads requiring attention</div></div>
          <Link href="/leads" className="secondary-btn">View all <ArrowUpRight size={13} /></Link>
        </div>
        <div className="table-wrap">
          <table>
            <thead><tr><th>Business</th><th>Category</th><th>Website</th><th>Score</th><th>Tier</th><th>Status</th><th /></tr></thead>
            <tbody>
              {leads.slice(0,5).map(lead => (
                <tr key={lead.id}>
                  <td><div className="business-cell"><div className="business-avatar">{lead.name[0]}</div><div><div className="business-name">{lead.name}</div><div className="business-meta">{lead.city}</div></div></div></td>
                  <td className="cell-text">{lead.category}</td>
                  <td><span className={`badge ${lead.websiteStatus === "No Website" ? "badge-hot" : "badge-gray"}`}>{lead.websiteStatus}</span></td>
                  <td><div className="score"><div className="score-track"><div className="score-fill" style={{width:`${lead.score}%`}} /></div><span className="score-value">{lead.score}</span></div></td>
                  <td><span className={`badge badge-${lead.tier.toLowerCase()}`}>{lead.tier}</span></td>
                  <td><span className={`badge ${lead.qualified ? "badge-green" : "badge-gray"}`}>{lead.status}</span></td>
                  <td><Link href={`/leads/${lead.id}`} className="secondary-btn" style={{height:32,padding:"0 10px"}}>View</Link></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <div className="grid-3" style={{marginTop:20}}>
        {[
          ["Lead Discovery", "Automation is running normally.", "green"],
          ["Website Generation", "3 demos generated today.", "green"],
          ["Outreach", `${hot + 9} leads waiting for approval.`, "yellow"]
        ].map(([title,text,state]) => (
          <div className="panel" style={{padding:18}} key={title}>
            <div style={{display:"flex",alignItems:"center",gap:8,fontSize:12,fontWeight:700}}>
              <span style={{width:8,height:8,borderRadius:"50%",background:state==="green"?"#10b981":"#f59e0b"}} />
              {title}
            </div>
            <div className="muted" style={{fontSize:10,marginTop:10}}>{text}</div>
          </div>
        ))}
      </div>
    </main>
  );
}