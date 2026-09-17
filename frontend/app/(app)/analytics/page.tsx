import { TrendingUp, Users, Globe2, Mail } from "lucide-react";

const values=[35,48,42,59,54,68,61,79,71,87,78,94];

export default function AnalyticsPage() {
  return (
    <main className="page">
      <div className="page-header"><div><div className="page-title">Analytics</div><div className="page-description">Monitor discovery, qualification, demos and outreach performance.</div></div><select className="select"><option>Last 30 days</option><option>Last 90 days</option><option>This year</option></select></div>
      <div className="kpi-grid">
        {[
          { label: "Discovery Rate", value: "248", change: "+", icon: Users },
          { label: "Qualification Rate", value: "34.7%", change: "+5.4%", icon: TrendingUp },
          { label: "Demo Conversion", value: "16.9%", change: "+3.2%", icon: Globe2 },
          { label: "Outreach Response", value: "18.4%", change: "+2.1%", icon: Mail },
        ].map(({ label, value, change, icon: Icon }) => (
          <div className="kpi-card" key={label}>
            <div className="kpi-top">
              <div>
                <div className="kpi-label">{label}</div>
                <div className="kpi-value">{value}</div>
              </div>
              <div className="kpi-icon"><Icon size={18}/></div>
            </div>
            <div className="kpi-foot"><span className="up">{change}</span><span className="muted">vs previous period</span></div>
          </div>
        ))}
      </div>
      <div className="analytics-grid">
        <section className="panel"><div className="panel-header"><div><div className="panel-title">Lead Growth</div><div className="panel-subtitle">New leads discovered over time</div></div></div><div className="chart-large">{values.map((v,i)=><div className="bar-wrap" key={i}><div className="bar" style={{height:`${v}%`}}/></div>)}</div></section>
        <section className="panel"><div className="panel-header"><div><div className="panel-title">Pipeline Breakdown</div><div className="panel-subtitle">Current workflow distribution</div></div></div><div style={{padding:"8px 20px 18px"}}>{[["Discovered","248"],["Qualified","86"],["Demo Ready","42"],["Contacted","31"],["Enquiries","17"]].map(([a,b])=><div className="stat-line" key={a}><span>{a}</span><span>{b}</span></div>)}</div></section>
      </div>
    </main>
  );
}