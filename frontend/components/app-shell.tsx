"use client";

import { useEffect, useState } from "react";
import { usePathname } from "next/navigation";
import { Lock, ShieldCheck, Eye, EyeOff, KeyRound } from "lucide-react";
import Sidebar from "./sidebar";
import Topbar from "./topbar";

export default function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);
  const [authenticated, setAuthenticated] = useState<boolean | null>(null);
  const [passwordInput, setPasswordInput] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  const expectedPassword = process.env.NEXT_PUBLIC_DASHBOARD_PASSWORD || "admin123";

  useEffect(() => {
    const authSaved = sessionStorage.getItem("leadhunter_auth_token");
    if (authSaved === "authenticated") {
      setAuthenticated(true);
    } else {
      setAuthenticated(false);
    }
  }, []);

  function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    if (passwordInput.trim() === expectedPassword) {
      sessionStorage.setItem("leadhunter_auth_token", "authenticated");
      setAuthenticated(true);
      setErrorMsg("");
    } else {
      setErrorMsg("Invalid password. Please try again.");
    }
  }

  function handleLogout() {
    document.cookie = "leadhunter_auth_session=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT";
    sessionStorage.removeItem("leadhunter_auth_token");
    localStorage.removeItem("leadhunter_auth_token");
    window.location.href = "/login";
  }

  if (authenticated === null) {
    return <div style={{ minHeight: "100vh", backgroundColor: "#0b1019" }} />;
  }

  if (!authenticated) {
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
            padding: "32px",
            boxShadow: "0 25px 50px -12px rgba(0, 0, 0, 0.5)",
            textAlign: "center"
          }}
        >
          <div
            style={{
              width: "56px",
              height: "56px",
              borderRadius: "12px",
              backgroundColor: "rgba(59, 130, 246, 0.1)",
              border: "1px solid rgba(59, 130, 246, 0.2)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              margin: "0 auto 20px auto",
              color: "#3b82f6"
            }}
          >
            <ShieldCheck size={28} />
          </div>

          <h2 style={{ fontSize: "22px", fontWeight: 700, margin: "0 0 8px 0", color: "#f8fafc" }}>
            LeadHunter AI Admin
          </h2>
          <p style={{ fontSize: "14px", color: "#94a3b8", margin: "0 0 24px 0" }}>
            Enter your security password to access the workspace
          </p>

          <form onSubmit={handleLogin} style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
            <div style={{ position: "relative" }}>
              <input
                type={showPassword ? "text" : "password"}
                placeholder="Enter password..."
                value={passwordInput}
                onChange={(e) => setPasswordInput(e.target.value)}
                autoFocus
                style={{
                  width: "100%",
                  padding: "12px 40px 12px 14px",
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
                  backgroundColor: "rgba(239, 68, 68, 0.1)",
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
              style={{
                width: "100%",
                padding: "12px",
                borderRadius: "8px",
                backgroundColor: "#2563eb",
                color: "#ffffff",
                fontWeight: 600,
                fontSize: "15px",
                border: "none",
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: "8px"
              }}
            >
              <KeyRound size={16} /> Unlock Dashboard
            </button>
          </form>

          <div style={{ marginTop: "24px", fontSize: "12px", color: "#64748b", display: "flex", alignItems: "center", justifyContent: "center", gap: "6px" }}>
            <Lock size={12} /> Encrypted Session Protection Active
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="app-shell">
      <Sidebar open={open} onClose={() => setOpen(false)} />
      <div className="main-shell">
        <Topbar pathname={pathname} onMenu={() => setOpen(true)} onLogout={handleLogout} />
        {children}
      </div>
    </div>
  );
}