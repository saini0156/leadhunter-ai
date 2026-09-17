"use client";

import Link from "next/link";
import {
  Download,
  Plus,
  Search,
  RefreshCw,
  SlidersHorizontal,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";

type Lead = {
  id: number;
  name: string;
  category: string;
  city: string;
  address?: string | null;
  phone?: string | null;
  email?: string | null;
  website?: string | null;
  website_verified?: boolean;
  website_status?: string | null;
  rating?: number | null;
  reviews?: number | null;
  status?: string | null;
  score?: number | null;
  tier?: string | null;
  qualified?: boolean;
  demo_url?: string | null;
  demo_status?: string | null;
};

export default function LeadsPage() {
  const apiBase =
    process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8500";

  const [leads, setLeads] = useState<Lead[]>([]);
  const [query, setQuery] = useState("");
  const [tier, setTier] = useState("All");
  const [website, setWebsite] = useState("All");
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");

  async function loadLeads(showRefresh = false) {
    try {
      if (showRefresh) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }

      setError("");

      const response = await fetch(`${apiBase}/api/leads?limit=100`, {
        cache: "no-store",
      });

      if (!response.ok) {
        throw new Error(`API returned ${response.status}`);
      }

      const data = await response.json();

      setLeads(data.leads || []);
    } catch (err) {
      console.error(err);
      setError(
        "Unable to load leads. Make sure the FastAPI server is running on port 8500."
      );
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }

  useEffect(() => {
    loadLeads();
  }, []);

  const filtered = useMemo(() => {
    return leads.filter((lead) => {
      const q = query.toLowerCase().trim();

      const matchesSearch =
        !q ||
        `${lead.name} ${lead.city} ${lead.category} ${lead.phone || ""} ${
          lead.email || ""
        }`
          .toLowerCase()
          .includes(q);

      const leadTier = (lead.tier || "COLD").toUpperCase();

      const matchesTier =
        tier === "All" || leadTier === tier.toUpperCase();

      const websiteStatus = lead.website_status || "Unknown";

      const matchesWebsite =
        website === "All" ||
        (website === "No Website" &&
          websiteStatus.toLowerCase().includes("no website")) ||
        (website === "Website Found" &&
          !websiteStatus.toLowerCase().includes("no website"));

      return matchesSearch && matchesTier && matchesWebsite;
    });
  }, [leads, query, tier, website]);

  const totalLeads = leads.length;

  const hotLeads = leads.filter(
    (lead) => (lead.tier || "").toUpperCase() === "HOT"
  ).length;

  const warmLeads = leads.filter(
    (lead) => (lead.tier || "").toUpperCase() === "WARM"
  ).length;

  const noWebsite = leads.filter((lead) =>
    (lead.website_status || "").toLowerCase().includes("no website")
  ).length;

  function exportCSV() {
    if (!filtered.length) return;

    const headers = [
      "ID",
      "Business",
      "Category",
      "City",
      "Address",
      "Phone",
      "Email",
      "Website",
      "Website Status",
      "Status",
      "Score",
      "Tier",
      "Qualified",
    ];

    const rows = filtered.map((lead) => [
      lead.id,
      lead.name,
      lead.category,
      lead.city,
      lead.address || "",
      lead.phone || "",
      lead.email || "",
      lead.website || "",
      lead.website_status || "",
      lead.status || "",
      lead.score ?? 0,
      lead.tier || "",
      lead.qualified ? "Yes" : "No",
    ]);

    const csv = [
      headers,
      ...rows,
    ]
      .map((row) =>
        row
          .map((value) => `"${String(value).replace(/"/g, '""')}"`)
          .join(",")
      )
      .join("\n");

    const blob = new Blob([csv], {
      type: "text/csv;charset=utf-8;",
    });

    const url = URL.createObjectURL(blob);

    const link = document.createElement("a");
    link.href = url;
    link.download = "leadhunter-leads.csv";
    link.click();

    URL.revokeObjectURL(url);
  }

  function tierBadgeClass(value: string) {
    switch (value.toUpperCase()) {
      case "HOT":
        return "badge badge-hot";
      case "WARM":
        return "badge badge-warm";
      case "COLD":
        return "badge badge-cold";
      default:
        return "badge badge-gray";
    }
  }

  return (
    <main className="page">
      <div className="page-header">
        <div>
          <div className="page-title">Leads</div>

          <div className="page-description">
            Manage, qualify and review your discovered business leads.
          </div>
        </div>

        <Link href="/discover" className="primary-btn">
          <Plus size={15} />
          Discover Leads
        </Link>
      </div>

      {/* KPI CARDS */}
      <div className="kpi-grid">
        <div className="kpi-card">
          <div className="kpi-label">Total Leads</div>
          <div className="kpi-value">{totalLeads}</div>
          <div className="muted" style={{ fontSize: 10, marginTop: 6 }}>
            Discovered prospects
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-label">Hot Leads</div>
          <div className="kpi-value">{hotLeads}</div>
          <div className="muted" style={{ fontSize: 10, marginTop: 6 }}>
            High-priority opportunities
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-label">Warm Leads</div>
          <div className="kpi-value">{warmLeads}</div>
          <div className="muted" style={{ fontSize: 10, marginTop: 6 }}>
            Potential opportunities
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-label">No Website</div>
          <div className="kpi-value">{noWebsite}</div>
          <div className="muted" style={{ fontSize: 10, marginTop: 6 }}>
            Website opportunity
          </div>
        </div>
      </div>

      {/* MAIN TABLE */}
      <section className="panel">
        {/* TOOLBAR */}
        <div className="table-toolbar">
          <div
            style={{
              position: "relative",
              width: "100%",
              maxWidth: 380,
            }}
          >
            <Search
              size={14}
              style={{
                position: "absolute",
                left: 12,
                top: 12,
                color: "#94a3b8",
              }}
            />

            <input
              className="input search-input"
              style={{ paddingLeft: 35 }}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search business, city or category..."
            />
          </div>

          <div className="filter-row">
            {["All", "HOT", "WARM", "COLD"].map((item) => (
              <button
                key={item}
                className={`filter-btn ${
                  tier === item ? "active" : ""
                }`}
                onClick={() => setTier(item)}
              >
                {item}
              </button>
            ))}

            <select
              className="select"
              value={website}
              onChange={(e) => setWebsite(e.target.value)}
            >
              <option>All</option>
              <option>No Website</option>
              <option>Website Found</option>
            </select>

            <button
              className="secondary-btn"
              style={{ height: 34 }}
              onClick={() => loadLeads(true)}
              disabled={refreshing}
            >
              <RefreshCw
                size={13}
                className={refreshing ? "animate-spin" : ""}
              />

              {refreshing ? "Refreshing" : "Refresh"}
            </button>

            <button
              className="secondary-btn"
              style={{ height: 34 }}
            >
              <SlidersHorizontal size={13} />
              Filters
            </button>
          </div>
        </div>

        {/* TABLE INFO */}
        <div
          style={{
            padding: "10px 16px",
            borderBottom: "1px solid var(--line)",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <span className="muted" style={{ fontSize: 10 }}>
            Showing{" "}
            <b style={{ color: "#475569" }}>
              {filtered.length}
            </b>{" "}
            leads
          </span>

          <button
            className="secondary-btn"
            style={{ height: 31 }}
            onClick={exportCSV}
          >
            <Download size={12} />
            Export CSV
          </button>
        </div>

        {/* LOADING */}
        {loading && (
          <div
            style={{
              padding: 50,
              textAlign: "center",
              color: "#64748b",
              fontSize: 13,
            }}
          >
            Loading leads from LeadHunter database...
          </div>
        )}

        {/* ERROR */}
        {!loading && error && (
          <div
            style={{
              padding: 50,
              textAlign: "center",
              color: "#dc2626",
              fontSize: 13,
            }}
          >
            {error}

            <div style={{ marginTop: 14 }}>
              <button
                className="secondary-btn"
                onClick={() => loadLeads()}
              >
                Try Again
              </button>
            </div>
          </div>
        )}

        {/* EMPTY */}
        {!loading && !error && filtered.length === 0 && (
          <div
            style={{
              padding: 50,
              textAlign: "center",
              color: "#64748b",
              fontSize: 13,
            }}
          >
            No leads found.

            {leads.length > 0 && (
              <div style={{ marginTop: 6, fontSize: 11 }}>
                Try changing your search or filters.
              </div>
            )}
          </div>
        )}

        {/* TABLE */}
        {!loading && !error && filtered.length > 0 && (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Business</th>
                  <th>Category</th>
                  <th>Location</th>
                  <th>Website</th>
                  <th>Qualification</th>
                  <th>Score</th>
                  <th>Tier</th>
                  <th />
                </tr>
              </thead>

              <tbody>
                {filtered.map((lead) => {
                  const leadTier = (
                    lead.tier || "COLD"
                  ).toUpperCase();

                  const score = Math.max(
                    0,
                    Math.min(100, Number(lead.score || 0))
                  );

                  const hasNoWebsite = (
                    lead.website_status || ""
                  )
                    .toLowerCase()
                    .includes("no website");

                  return (
                    <tr key={lead.id}>
                      {/* BUSINESS */}
                      <td>
                        <div className="business-cell">
                          <div className="business-avatar">
                            {lead.name?.charAt(0)?.toUpperCase() || "L"}
                          </div>

                          <div>
                            <div className="business-name">
                              {lead.name}
                            </div>

                            <div className="business-meta">
                              Lead #{lead.id}
                            </div>
                          </div>
                        </div>
                      </td>

                      {/* CATEGORY */}
                      <td className="cell-text">
                        {lead.category || "—"}
                      </td>

                      {/* LOCATION */}
                      <td>
                        <div className="cell-text">
                          {lead.city || "—"}
                        </div>

                        <div className="business-meta">
                          {lead.reviews || 0} reviews
                        </div>
                      </td>

                      {/* WEBSITE */}
                      <td>
                        <span
                          className={`badge ${
                            hasNoWebsite
                              ? "badge-hot"
                              : "badge-gray"
                          }`}
                        >
                          {lead.website_status ||
                            (lead.website
                              ? "Website Found"
                              : "Unknown")}
                        </span>
                      </td>

                      {/* QUALIFICATION */}
                      <td>
                        <span
                          className={`badge ${
                            lead.qualified
                              ? "badge-green"
                              : "badge-gray"
                          }`}
                        >
                          {lead.qualified
                            ? "Qualified"
                            : lead.status || "Discovered"}
                        </span>
                      </td>

                      {/* SCORE */}
                      <td>
                        <div className="score">
                          <div className="score-track">
                            <div
                              className="score-fill"
                              style={{
                                width: `${score}%`,
                              }}
                            />
                          </div>

                          <span className="score-value">
                            {score}
                          </span>
                        </div>
                      </td>

                      {/* TIER */}
                      <td>
                        <span className={tierBadgeClass(leadTier)}>
                          {leadTier}
                        </span>
                      </td>

                      {/* VIEW */}
                      <td>
                        <Link
                          href={`/leads/${lead.id}`}
                          className="secondary-btn"
                          style={{
                            height: 31,
                            padding: "0 10px",
                          }}
                        >
                          View
                        </Link>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </main>
  );
}