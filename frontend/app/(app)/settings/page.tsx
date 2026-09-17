"use client";

import { useState } from "react";
import { Save } from "lucide-react";

export default function SettingsPage() {
  const [auto,setAuto]=useState(true);
  const [follow,setFollow]=useState(true);
  const [approval,setApproval]=useState(true);

  return (
    <main className="page">
      <div className="page-header"><div><div className="page-title">Settings</div><div className="page-description">Configure your LeadHunter workspace and automation rules.</div></div><button className="primary-btn"><Save size={14}/> Save Changes</button></div>
      <div className="settings-grid">
        <section className="panel settings-nav"><button className="settings-tab active">Workspace</button><button className="settings-tab">Pipeline</button><button className="settings-tab">Outreach</button><button className="settings-tab">Integrations</button><button className="settings-tab">Security</button></section>
        <section className="panel settings-content">
          <div className="detail-heading">Workspace</div>
          <div className="form-grid"><div className="form-group"><label className="form-label">Workspace Name</label><input className="input" defaultValue="LeadHunter AI"/></div><div className="form-group"><label className="form-label">Target Market</label><input className="input" defaultValue="Surrey, BC, Canada"/></div><div className="form-group"><label className="form-label">Primary Category</label><input className="input" defaultValue="Roofing Contractor"/></div><div className="form-group"><label className="form-label">LLM Provider</label><input className="input" defaultValue="Groq"/></div></div>
          <div className="detail-heading" style={{marginTop:28}}>Automation</div>
          {[
            { title: "Automatic lead qualification", desc: "Score and qualify discovered leads automatically.", value: auto, setter: setAuto },
            { title: "Human approval before outreach", desc: "Require approval before any email or WhatsApp dispatch.", value: approval, setter: setApproval },
            { title: "Automated follow-ups", desc: "Create follow-up tasks after outreach.", value: follow, setter: setFollow }
          ].map(({ title, desc, value, setter }) => (
            <div className="toggle-row" key={title}>
              <div>
                <div style={{fontSize:11,fontWeight:700}}>{title}</div>
                <div className="muted" style={{fontSize:10,marginTop:4}}>{desc}</div>
              </div>
              <button className={`toggle ${value?"on":""}`} onClick={()=>setter(!value)}><span/></button>
            </div>
          ))}
        </section>
      </div>
    </main>
  );
}