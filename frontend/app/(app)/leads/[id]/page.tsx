"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import {
  ArrowLeft,
  ExternalLink,
  Copy,
  Check,
  Zap,
  Star,
  Activity,
  Globe,
  Mail,
  MessageSquare,
  ShieldCheck,
  AlertTriangle,
} from "lucide-react";

type Lead = {
  id: number;
  name: string;
  category?: string | null;
  city?: string | null;
  address?: string | null;
  phone?: string | null;
  email?: string | null;
  website?: string | null;
  website_verified?: string | null;
  website_status?: string | null;
  rating?: number | null;
  reviews?: number | null;

  status?: string | null;
  score?: number | null;
  tier?: string | null;
  qualified?: boolean;
  qualification_notes?: string | null;

  demo_url?: string | null;

  email_subject?: string | null;
  email_message?: string | null;
  whatsapp_message?: string | null;
  personalized_message?: string | null;

  site_profile?: {
    url?: string;
    final_url?: string;
    status_code?: number | null;
    title?: string;
    error?: string | null;
    is_matching?: boolean;
    load_time_sec?: number | null;
    classification?: string | null;

    seo_audit?: {
      load_time_sec?: number | null;
      speed_category?: string | null;
      seo_health_score?: number | null;
      seo_issues?: string[];
      seo_opportunities?: string[];
      passed_checks?: string[];
      estimated_lost_monthly_revenue_min?: number | null;
      estimated_lost_monthly_revenue_max?: number | null;
      formatted_loss_range?: string | null;
      conversion_drop_percent?: number | null;
    };
  };

  seo?: {
    health_score?: number | null;
    load_time_sec?: number | null;
    speed_category?: string | null;
    issues?: string[];
  };
};

export default function LeadDetailPage() {
  const params = useParams();
  const id = params?.id;

  const apiBase =
    process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8500";

  const [lead, setLead] = useState<Lead | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [copied, setCopied] = useState("");

  async function loadLead() {
    if (!id) return;

    try {
      setLoading(true);
      setError("");

      const response = await fetch(`${apiBase}/api/leads/${id}`);

      if (!response.ok) {
        throw new Error(`Unable to load lead (${response.status})`);
      }

      const data = await response.json();

      if (!data.lead) {
        throw new Error("Lead data not found");
      }

      setLead(data.lead);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load lead");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadLead();
  }, [id]);

  const seo = lead?.seo || {};
  const audit = lead?.site_profile?.seo_audit || {};

  const seoScore =
    seo.health_score ??
    audit.seo_health_score ??
    null;

  const speed =
    seo.load_time_sec ??
    audit.load_time_sec ??
    lead?.site_profile?.load_time_sec ??
    null;

  const seoIssues =
    seo.issues ||
    audit.seo_issues ||
    [];

  const seoOpportunities =
    audit.seo_opportunities || [];

  const lossRange =
    audit.formatted_loss_range ||
    (audit.estimated_lost_monthly_revenue_min != null &&
    audit.estimated_lost_monthly_revenue_max != null
      ? `$${audit.estimated_lost_monthly_revenue_min.toLocaleString()} - $${audit.estimated_lost_monthly_revenue_max.toLocaleString()}`
      : null);

  const scoreLabel = useMemo(() => {
    const score = lead?.score ?? 0;

    if (score >= 85) return "High Opportunity";
    if (score >= 60) return "Good Opportunity";
    if (score >= 40) return "Moderate Opportunity";
    return "Low Opportunity";
  }, [lead?.score]);

  async function copyText(text: string | null | undefined, label: string) {
    if (!text) return;

    try {
      await navigator.clipboard.writeText(text);
      setCopied(label);

      setTimeout(() => {
        setCopied("");
      }, 1800);
    } catch {
      // Ignore clipboard errors.
    }
  }

  if (loading) {
    return (
      <main className="page">
        <div className="panel" style={{ padding: 40, textAlign: "center", color: "var(--muted)" }}>
          Loading lead details...
        </div>
      </main>
    );
  }

  if (error || !lead) {
    return (
      <main className="page">
        <Link href="/leads" className="secondary-btn" style={{ height: 34, marginBottom: 20 }}>
          <ArrowLeft size={13} /> Back to Leads
        </Link>
        <div className="panel" style={{ padding: 30, color: "var(--danger)" }}>
          <div style={{ fontWeight: 800, fontSize: 16, marginBottom: 8 }}>Unable to load lead</div>
          <div style={{ fontSize: 12 }}>{error || "Lead not found."}</div>
          <button className="secondary-btn" style={{ marginTop: 16 }} onClick={loadLead}>
            Try Again
          </button>
        </div>
      </main>
    );
  }

  const score = lead.score ?? 0;

  return (
    <main className="page">
      {/* PAGE HEADER */}
      <div className="page-header">
        <div>
          <Link href="/leads" className="secondary-btn" style={{ height: 32, marginBottom: 12 }}>
            <ArrowLeft size={13} /> Back to Leads
          </Link>
          <div style={{ display: "flex", alignItems: "center", gap: 12, flexWrap: "wrap", marginTop: 6 }}>
            <div className="page-title">{lead.name}</div>
            {lead.qualified && <span className="badge badge-green">Qualified</span>}
            {lead.tier && <span className={`badge badge-${lead.tier.toLowerCase()}`}>{lead.tier}</span>}
          </div>
          <div className="page-description">
            Lead #{lead.id}
            {lead.category ? ` · ${lead.category}` : ""}
            {lead.city ? ` · ${lead.city}` : ""}
          </div>
        </div>

        <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
          {lead.demo_url && (
            <a href={lead.demo_url} target="_blank" rel="noreferrer" className="primary-btn">
              Open Demo Website <ExternalLink size={13} />
            </a>
          )}
          {lead.website && (
            <a href={lead.website} target="_blank" rel="noreferrer" className="secondary-btn">
              Open Website <ExternalLink size={13} />
            </a>
          )}
        </div>
      </div>

      {/* KPI METRIC CARDS */}
      <div className="kpi-grid" style={{ gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))" }}>
        <div className="kpi-card">
          <div className="kpi-top">
            <div>
              <div className="kpi-label">Lead Score</div>
              <div className="kpi-value">{score}/100</div>
            </div>
            <div className="kpi-icon"><Activity size={18} /></div>
          </div>
          <div className="kpi-foot"><span className="up">{scoreLabel}</span></div>
        </div>

        <div className="kpi-card">
          <div className="kpi-top">
            <div>
              <div className="kpi-label">SEO Health</div>
              <div className="kpi-value">{seoScore != null ? `${seoScore}/100` : "—"}</div>
            </div>
            <div className="kpi-icon"><Globe size={18} /></div>
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-top">
            <div>
              <div className="kpi-label">Website Speed</div>
              <div className="kpi-value">{speed != null ? `${speed.toFixed(2)}s` : "—"}</div>
            </div>
            <div className="kpi-icon"><Zap size={18} /></div>
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-top">
            <div>
              <div className="kpi-label">Google Rating</div>
              <div className="kpi-value">{lead.rating != null ? lead.rating.toFixed(1) : "—"}</div>
            </div>
            <div className="kpi-icon"><Star size={18} /></div>
          </div>
          {lead.reviews ? <div className="kpi-foot"><span className="muted">{lead.reviews} reviews</span></div> : null}
        </div>

        <div className="kpi-card">
          <div className="kpi-top">
            <div>
              <div className="kpi-label">Pipeline Status</div>
              <div className="kpi-value" style={{ fontSize: 15, marginTop: 10 }}>{lead.status || "—"}</div>
            </div>
            <div className="kpi-icon"><ShieldCheck size={18} /></div>
          </div>
        </div>
      </div>

      {/* DETAIL GRID */}
      <div className="detail-grid">
        {/* BUSINESS INFO */}
        <section className="panel" style={{ padding: 24 }}>
          <div className="detail-heading">Business Information</div>
          <div className="muted" style={{ fontSize: 11, marginBottom: 18 }}>
            Verified business details collected during discovery.
          </div>

          <div className="detail-grid-small">
            <div className="detail-field">
              <div className="detail-label">Business Name</div>
              <div className="detail-value">{lead.name}</div>
            </div>

            <div className="detail-field">
              <div className="detail-label">Category</div>
              <div className="detail-value">{lead.category || "—"}</div>
            </div>

            <div className="detail-field">
              <div className="detail-label">City</div>
              <div className="detail-value">{lead.city || "—"}</div>
            </div>

            <div className="detail-field">
              <div className="detail-label">Address</div>
              <div className="detail-value">{lead.address || "—"}</div>
            </div>

            <div className="detail-field">
              <div className="detail-label">Phone</div>
              <div className="detail-value" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span>{lead.phone || "—"}</span>
                {lead.phone && (
                  <button className="secondary-btn" style={{ height: 26, padding: "0 8px", fontSize: 10 }} onClick={() => copyText(lead.phone, "phone")}>
                    {copied === "phone" ? <Check size={11} /> : <Copy size={11} />}
                    {copied === "phone" ? "Copied" : "Copy"}
                  </button>
                )}
              </div>
            </div>

            <div className="detail-field">
              <div className="detail-label">Email</div>
              <div className="detail-value" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span>{lead.email || "—"}</span>
                {lead.email && (
                  <button className="secondary-btn" style={{ height: 26, padding: "0 8px", fontSize: 10 }} onClick={() => copyText(lead.email, "email")}>
                    {copied === "email" ? <Check size={11} /> : <Copy size={11} />}
                    {copied === "email" ? "Copied" : "Copy"}
                  </button>
                )}
              </div>
            </div>
          </div>

          <div className="detail-field" style={{ marginTop: 14 }}>
            <div className="detail-label">Website</div>
            <div className="detail-value">
              {lead.website ? (
                <a href={lead.website} target="_blank" rel="noreferrer" style={{ color: "var(--primary)", textDecoration: "underline" }}>
                  {lead.website}
                </a>
              ) : (
                <span className="badge badge-hot">No Website</span>
              )}
            </div>
          </div>

          <div className="detail-field" style={{ marginTop: 14 }}>
            <div className="detail-label">Website Verification Status</div>
            <div className="detail-value">
              <span className={`badge ${lead.website_status === "VALID_WEBSITE" ? "badge-green" : "badge-gray"}`}>
                {lead.website_status || "—"}
              </span>
            </div>
          </div>
        </section>

        {/* QUALIFICATION */}
        <section className="panel" style={{ padding: 24 }}>
          <div className="detail-heading">Qualification & Scoring</div>

          <div style={{ background: "#f8fafc", padding: 18, borderRadius: 12, marginBottom: 18, border: "1px solid var(--line)" }}>
            <div className="detail-label">Opportunity Rating</div>
            <div style={{ fontSize: 22, fontWeight: 800, margin: "6px 0", color: "var(--text)" }}>{scoreLabel}</div>
            <div className="score-track" style={{ width: "100%", height: 8, marginTop: 10 }}>
              <div className="score-fill" style={{ width: `${Math.min(score, 100)}%` }} />
            </div>
          </div>

          <div className="stat-line"><span>Qualified</span><span style={{ fontWeight: 700 }}>{lead.qualified ? "Yes" : "No"}</span></div>
          <div className="stat-line"><span>Lead Tier</span><span className={`badge badge-${(lead.tier || "cold").toLowerCase()}`}>{lead.tier || "COLD"}</span></div>
          <div className="stat-line"><span>Website Status</span><span style={{ fontWeight: 700 }}>{lead.website_status || "—"}</span></div>

          {lead.qualification_notes && (
            <div style={{ marginTop: 18, padding: 14, background: "#f8fafc", borderRadius: 10, border: "1px solid var(--line)" }}>
              <div className="detail-label">Qualification Notes</div>
              <div style={{ fontSize: 11, marginTop: 6, lineHeight: 1.6, color: "var(--text)" }}>{lead.qualification_notes}</div>
            </div>
          )}
        </section>
      </div>

      {/* SEO & WEBSITE ANALYSIS */}
      <section className="panel" style={{ marginTop: 24, padding: 24 }}>
        <div className="detail-heading">Website & SEO Analysis</div>
        <div className="muted" style={{ fontSize: 11, marginBottom: 18 }}>
          Technical audit signals and estimated commercial impact.
        </div>

        <div className="grid-3">
          <div className="detail-field">
            <div className="detail-label">SEO Health Score</div>
            <div className="detail-value" style={{ fontSize: 24, fontWeight: 800, color: "var(--primary)" }}>
              {seoScore != null ? `${seoScore}/100` : "—"}
            </div>
          </div>

          <div className="detail-field">
            <div className="detail-label">Page Load Speed</div>
            <div className="detail-value" style={{ fontSize: 24, fontWeight: 800 }}>
              {speed != null ? `${speed.toFixed(2)}s` : "—"}
            </div>
          </div>

          <div className="detail-field">
            <div className="detail-label">Estimated Revenue Opportunity</div>
            <div className="detail-value" style={{ fontSize: 18, fontWeight: 800, color: "var(--success)" }}>
              {lossRange || "—"}
            </div>
          </div>
        </div>

        {seoIssues.length > 0 && (
          <div style={{ marginTop: 20 }}>
            <div className="detail-label" style={{ marginBottom: 10 }}>Detected SEO Issues</div>
            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              {seoIssues.map((issue, idx) => (
                <div key={idx} style={{ padding: "10px 14px", background: "#f8fafc", borderRadius: 8, border: "1px solid var(--line)", fontSize: 11, display: "flex", gap: 8, alignItems: "center" }}>
                  <AlertTriangle size={13} style={{ color: "#f59e0b", flexShrink: 0 }} />
                  <span>{issue}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </section>

      {/* AI OUTREACH COPYWRITING */}
      <section className="panel" style={{ marginTop: 24, padding: 24 }}>
        <div className="detail-heading">AI Outreach Copywriting</div>
        <div className="muted" style={{ fontSize: 11, marginBottom: 18 }}>
          Personalized cold email & WhatsApp copy built for this business.
        </div>

        <div className="grid-2">
          <div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
              <div className="detail-label" style={{ display: "flex", gap: 6, alignItems: "center" }}>
                <Mail size={13} /> Cold Email Message
              </div>
              <div style={{ display: "flex", gap: 6 }}>
                {lead.email && lead.email_message && (
                  <a
                    href={`mailto:${lead.email}?subject=${encodeURIComponent(lead.email_subject || "Proposal for " + lead.name)}&body=${encodeURIComponent(lead.email_message)}`}
                    target="_blank"
                    rel="noreferrer"
                    className="primary-btn"
                    style={{ height: 26, padding: "0 10px", fontSize: 10, display: "inline-flex", alignItems: "center", gap: 4 }}
                  >
                    <Mail size={11} /> Send Email
                  </a>
                )}
                {lead.email_message && (
                  <button className="secondary-btn" style={{ height: 26, padding: "0 8px", fontSize: 10 }} onClick={() => copyText(lead.email_message, "email-msg")}>
                    {copied === "email-msg" ? <Check size={11} /> : <Copy size={11} />}
                    {copied === "email-msg" ? "Copied" : "Copy"}
                  </button>
                )}
              </div>
            </div>

            {lead.email_subject && (
              <div style={{ fontWeight: 700, fontSize: 12, marginBottom: 10, color: "var(--primary)" }}>
                Subject: {lead.email_subject}
              </div>
            )}

            <div className="message-box">
              {lead.email_message || lead.personalized_message || "No email message generated yet."}
            </div>
          </div>

          <div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
              <div className="detail-label" style={{ display: "flex", gap: 6, alignItems: "center" }}>
                <MessageSquare size={13} /> WhatsApp Message
              </div>
              <div style={{ display: "flex", gap: 6 }}>
                {lead.phone && lead.whatsapp_message && (
                  <a
                    href={`https://wa.me/${lead.phone.replace(/[^0-9]/g, '')}?text=${encodeURIComponent(lead.whatsapp_message)}`}
                    target="_blank"
                    rel="noreferrer"
                    className="primary-btn"
                    style={{ height: 26, padding: "0 10px", fontSize: 10, display: "inline-flex", alignItems: "center", gap: 4, background: "#22c55e", borderColor: "#16a34a" }}
                  >
                    <MessageSquare size={11} /> Send WhatsApp
                  </a>
                )}
                {lead.whatsapp_message && (
                  <button className="secondary-btn" style={{ height: 26, padding: "0 8px", fontSize: 10 }} onClick={() => copyText(lead.whatsapp_message, "wa-msg")}>
                    {copied === "wa-msg" ? <Check size={11} /> : <Copy size={11} />}
                    {copied === "wa-msg" ? "Copied" : "Copy"}
                  </button>
                )}
              </div>
            </div>

            <div className="message-box">
              {lead.whatsapp_message || "No WhatsApp message generated yet."}
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}