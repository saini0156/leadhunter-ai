import Link from "next/link";
import { CheckCircle2, ExternalLink } from "lucide-react";
import { leads } from "../../../lib/data";

export default function QualifiedPage() {
  const qualified = leads.filter(l=>l.qualified);
  return (
    <main className="page">
      <div className="page-header"><div><div className="page-title">Qualified Leads</div><div className="page-description">Leads that passed qualification and are ready for human review or outreach.</div></div><span className="badge badge-green">{qualified.length} Qualified</span></div>
      <div className="panel">
        <div className="table-wrap"><table><thead><tr><th>Business</th><th>Score</th><th>Tier</th><th>Website</th><th>SEO Opportunity</th><th>Demo</th><th /></tr></thead>
        <tbody>{qualified.map(l=><tr key={l.id}>
          <td><div className="business-cell"><div className="business-avatar">{l.name[0]}</div><div><div className="business-name">{l.name}</div><div className="business-meta">{l.city}</div></div></div></td>
          <td><span className="score-value">{l.score}/100</span></td><td><span className={`badge badge-${l.tier.toLowerCase()}`}>{l.tier}</span></td>
          <td><span className={`badge ${l.websiteStatus==="No Website"?"badge-hot":"badge-gray"}`}>{l.websiteStatus}</span></td>
          <td className="cell-text">{l.seoOpportunity}</td><td>{l.demoStatus==="READY"?<span className="badge badge-green">READY</span>:<span className="badge badge-gray">{l.demoStatus}</span>}</td>
          <td><div style={{display:"flex",gap:6}}><Link href={`/leads/${l.id}`} className="secondary-btn" style={{height:31}}>Review</Link>{l.demoUrl&&<a href={l.demoUrl} target="_blank" rel="noreferrer" className="secondary-btn" style={{height:31}}><ExternalLink size={12}/></a>}</div></td>
        </tr>)}</tbody></table></div>
      </div>
    </main>
  );
}