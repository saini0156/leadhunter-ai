"use client";

import { Mail, Phone, Search } from "lucide-react";
import { useState } from "react";
import { enquiries } from "@/lib/data";

export default function EnquiriesPage() {
  const [query,setQuery]=useState("");
  const filtered=enquiries.filter(x=>`${x.name} ${x.email} ${x.service}`.toLowerCase().includes(query.toLowerCase()));
  return (
    <main className="page">
      <div className="page-header"><div><div className="page-title">Enquiries</div><div className="page-description">Customer enquiries submitted through generated demo websites.</div></div><span className="badge badge-green">Live form connected</span></div>
      <section className="panel">
        <div className="table-toolbar"><div style={{position:"relative",maxWidth:360,width:"100%"}}><Search size={14} style={{position:"absolute",left:11,top:12,color:"#94a3b8"}}/><input className="input" style={{paddingLeft:34}} placeholder="Search enquiries..." value={query} onChange={e=>setQuery(e.target.value)}/></div></div>
        <div className="table-wrap"><table><thead><tr><th>Customer</th><th>Contact</th><th>Service</th><th>Status</th><th>Received</th><th /></tr></thead><tbody>
          {filtered.map(e=><tr key={e.id}><td><div className="business-name">{e.name}</div><div className="business-meta">Lead #{e.leadId}</div></td><td><div className="cell-text"><Phone size={11} style={{verticalAlign:"middle",marginRight:5}}/>{e.phone}</div><div className="business-meta"><Mail size={10} style={{verticalAlign:"middle",marginRight:5}}/>{e.email}</div></td><td className="cell-text">{e.service}</td><td><span className={`badge ${e.status==="NEW"?"badge-green":"badge-blue"}`}>{e.status}</span></td><td className="business-meta">{e.time}</td><td><button className="secondary-btn" style={{height:31}}>Open</button></td></tr>)}
        </tbody></table></div>
      </section>
    </main>
  );
}