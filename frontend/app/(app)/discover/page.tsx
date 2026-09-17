"use client";

import { useState } from "react";
import { Sparkles, MapPin, Target, Play, Loader2 } from "lucide-react";

export default function DiscoverPage() {
  const [city, setCity] = useState("Surrey, BC, Canada");
  const [category, setCategory] = useState("Roofing Contractor");
  const [count, setCount] = useState("25");
  const [running, setRunning] = useState(false);
  const [message, setMessage] = useState("");

  const runDiscovery = async () => {
    setRunning(true);
    setMessage("");

    try {
      const apiBase =
        process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8500";

      const response = await fetch(`${apiBase}/api/discover`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          city,
          category,
          lead_count: Number(count),
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Discovery failed");
      }

      setMessage(
        data.message ||
          `Discovery completed. ${data.count || 0} leads found.`
      );
    } catch (error) {
      setMessage(
        error instanceof Error
          ? error.message
          : "Unable to run discovery pipeline."
      );
    } finally {
      setRunning(false);
    }
  };

  return (
    <main className="page">
      <div className="page-header">
        <div>
          <div className="page-title">Discover Leads</div>
          <div className="page-description">
            Configure and run the LeadHunter discovery pipeline.
          </div>
        </div>

        <span className="badge badge-green">Pipeline Ready</span>
      </div>

      <div className="hero-card">
        <div>
          <div className="hero-eyebrow">AI Lead Discovery</div>

          <div className="hero-heading">
            Find businesses with real website + SEO opportunities.
          </div>

          <div className="hero-text">
            Your existing discovery, verification, scoring and personalization
            pipeline can feed this interface. Start with a city, category and
            target count.
          </div>
        </div>

        <Sparkles size={42} style={{ opacity: 0.7 }} />
      </div>

      <div className="discovery-grid">
        <section className="panel discovery-form">
          <div className="detail-heading">Discovery Configuration</div>

          <div className="form-group">
            <label className="form-label">Target City</label>

            <div style={{ position: "relative" }}>
              <MapPin
                size={14}
                style={{
                  position: "absolute",
                  left: 11,
                  top: 12,
                  color: "#94a3b8",
                }}
              />

              <input
                className="input"
                style={{ paddingLeft: 34 }}
                value={city}
                onChange={(e) => setCity(e.target.value)}
                disabled={running}
              />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Business Category</label>

            <div style={{ position: "relative" }}>
              <Target
                size={14}
                style={{
                  position: "absolute",
                  left: 11,
                  top: 12,
                  color: "#94a3b8",
                }}
              />

              <input
                className="input"
                style={{ paddingLeft: 34 }}
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                disabled={running}
              />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Lead Count</label>

            <select
              className="select"
              style={{ width: "100%" }}
              value={count}
              onChange={(e) => setCount(e.target.value)}
              disabled={running}
            >
              {["10", "25", "50", "100"].map((x) => (
                <option key={x}>{x}</option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">Qualification Target</label>

            <select
              className="select"
              style={{ width: "100%" }}
              disabled={running}
            >
              <option>Website + SEO opportunities</option>
              <option>No website only</option>
              <option>All businesses</option>
            </select>
          </div>

          <button
            type="button"
            className="primary-btn"
            style={{
              width: "100%",
              marginTop: 5,
              cursor: running ? "not-allowed" : "pointer",
              opacity: running ? 0.7 : 1,
            }}
            onClick={runDiscovery}
            disabled={running}
          >
            {running ? (
              <>
                <Loader2 size={14} className="animate-spin" />
                Running Discovery...
              </>
            ) : (
              <>
                <Play size={14} />
                Run Discovery Pipeline
              </>
            )}
          </button>

          {message && (
            <div
              style={{
                marginTop: 14,
                padding: 12,
                borderRadius: 10,
                background: "#f8fafc",
                border: "1px solid #e2e8f0",
                fontSize: 12,
                color: "#475569",
                lineHeight: 1.5,
              }}
            >
              {message}
            </div>
          )}
        </section>

        <section className="panel target-preview">
          <div className="detail-heading">Current Target</div>

          <div style={{ marginBottom: 16 }}>
            <span className="target-chip">
              <MapPin size={11} />
              {city}
            </span>

            <span className="target-chip">
              <Target size={11} />
              {category}
            </span>

            <span className="target-chip">{count} leads</span>
          </div>

          <div className="stat-line">
            <span>Discovery</span>
            <span>SerpAPI / Maps</span>
          </div>

          <div className="stat-line">
            <span>Verification</span>
            <span>Website Check</span>
          </div>

          <div className="stat-line">
            <span>Scoring</span>
            <span>AI + Rules</span>
          </div>

          <div className="stat-line">
            <span>Personalization</span>
            <span>Groq</span>
          </div>

          <div className="stat-line">
            <span>Demo</span>
            <span>FastAPI Generator</span>
          </div>

          <div
            style={{
              marginTop: 18,
              padding: 13,
              borderRadius: 10,
              background: "#f8fafc",
              fontSize: 10,
              color: "#64748b",
              lineHeight: 1.6,
            }}
          >
            Configure your target and start the real LeadHunter discovery
            pipeline.
          </div>
        </section>
      </div>
    </main>
  );
}