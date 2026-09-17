"use client";

import { Menu, Bell, Search } from "lucide-react";

const titles: Record<string, string> = {
  "/dashboard": "Dashboard",
  "/leads": "Leads",
  "/discover": "Discover Leads",
  "/qualified": "Qualified Leads",
  "/demos": "Demo Websites",
  "/enquiries": "Enquiries",
  "/outreach": "Outreach",
  "/followups": "Follow-ups",
  "/analytics": "Analytics",
  "/settings": "Settings"
};

export default function Topbar({
  pathname,
  onMenu
}: {
  pathname: string;
  onMenu: () => void;
}) {
  const title =
    titles[pathname] ||
    (pathname.startsWith("/leads/") ? "Lead Details" : "LeadHunter AI");

  return (
    <header className="topbar">
      <div className="topbar-left">
        <button className="mobile-menu" onClick={onMenu}><Menu size={17} /></button>
        <div>
          <div className="topbar-title">{title}</div>
          <div className="topbar-subtitle">LeadHunter AI workspace</div>
        </div>
      </div>

      <div className="top-actions">
        <button className="search-btn"><Search size={14} /> Search <span style={{ marginLeft: "auto", color: "#9aa7ba" }}>/</span></button>
        <button className="icon-btn"><Bell size={15} /><span className="notification-dot" /></button>
        <div className="avatar">NS</div>
      </div>
    </header>
  );
}
