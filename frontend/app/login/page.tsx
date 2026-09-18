"use client";

import { Suspense, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Lock, ShieldCheck, Eye, EyeOff, KeyRound } from "lucide-react";

function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const from = searchParams.get("from") || "/dashboard";

  const [passwordInput, setPasswordInput] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");
  const [loading, setLoading] = useState(false);

  const expectedPassword = process.env.NEXT_PUBLIC_DASHBOARD_PASSWORD || "admin123";

  function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setErrorMsg("");

    if (passwordInput.trim() === expectedPassword) {
      document.cookie = "leadhunter_auth_session=authenticated; path=/; max-age=86400; SameSite=Lax";
      sessionStorage.setItem("leadhunter_auth_token", "authenticated");
      router.push(from);
      router.refresh();
    } else {
      setLoading(false);
      setErrorMsg("Invalid password. Please try again.");
    }
  }

  return (
    <div
      style={{
        minHeight: "100vh",
        backgroundColor: "#0b1019",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "20px",
        fontFamily: "sans-serif",
        color: "#e2e8f0"
      }}
    >
      <div
        style={{
          maxWidth: "420px",
          width: "100%",
          backgroundColor: "#131b2a",
          border: "1px solid #1e293b",
          borderRadius: "16px",
          padding: "36px 32px",
          boxShadow: "0 25px 50px -12px rgba(0, 0, 0, 0.6)",
          textAlign: "center"
        }}
      >
        <div
          style={{
            width: "60px",
            height: "60px",
            borderRadius: "14px",
            backgroundColor: "rgba(59, 130, 246, 0.12)",
            border: "1px solid rgba(59, 130, 246, 0.25)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            margin: "0 auto 20px auto",
            color: "#3b82f6"
          }}
        >
          <ShieldCheck size={32} />
        </div>

        <h2 style={{ fontSize: "24px", fontWeight: 700, margin: "0 0 8px 0", color: "#f8fafc" }}>
          LeadHunter AI Admin
        </h2>
        <p style={{ fontSize: "14px", color: "#94a3b8", margin: "0 0 28px 0" }}>
          Enter your security password to unlock workspace
        </p>

        <form onSubmit={handleLogin} style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          <div style={{ position: "relative" }}>
            <input
              type={showPassword ? "text" : "password"}
              placeholder="Enter admin password..."
              value={passwordInput}
              onChange={(e) => setPasswordInput(e.target.value)}
              autoFocus
              style={{
                width: "100%",
                padding: "12px 42px 12px 14px",
                borderRadius: "8px",
                backgroundColor: "#0f172a",
                border: "1px solid #334155",
                color: "#f8fafc",
                fontSize: "15px",
                outline: "none",
                boxSizing: "border-box"
              }}
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              style={{
                position: "absolute",
                right: "12px",
                top: "50%",
                transform: "translateY(-50%)",
                background: "none",
                border: "none",
                color: "#64748b",
                cursor: "pointer",
                display: "flex",
                alignItems: "center"
              }}
            >
              {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
            </button>
          </div>

          {errorMsg && (
            <div
              style={{
                backgroundColor: "rgba(239, 68, 68, 0.12)",
                border: "1px solid rgba(239, 68, 68, 0.3)",
                color: "#f87171",
                fontSize: "13px",
                padding: "10px",
                borderRadius: "6px"
              }}
            >
              {errorMsg}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            style={{
              width: "100%",
              padding: "12px",
              borderRadius: "8px",
              backgroundColor: "#2563eb",
              color: "#ffffff",
              fontWeight: 600,
              fontSize: "15px",
              border: "none",
              cursor: loading ? "wait" : "pointer",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: "8px",
              opacity: loading ? 0.7 : 1
            }}
          >
            <KeyRound size={16} /> {loading ? "Verifying..." : "Unlock Dashboard"}
          </button>
        </form>

        <div
          style={{
            marginTop: "24px",
            fontSize: "12px",
            color: "#64748b",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: "6px"
          }}
        >
          <Lock size={12} /> Strict Edge Session Protection Active
        </div>
      </div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={<div style={{ minHeight: "100vh", backgroundColor: "#0b1019" }} />}>
      <LoginForm />
    </Suspense>
  );
}
