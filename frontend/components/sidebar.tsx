"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard, Users, Search, BadgeCheck, PanelsTopLeft,
  Mail, Send, RefreshCcw, BarChart3, Settings, X
} from "lucide-react";

const groups = [
  {
    label: "MAIN",
    items: [
      ["Dashboard", "/dashboard", LayoutDashboard],
      ["Leads", "/leads", Users],
      ["Discover Leads", "/discover", Search]
    ]
  },
  {
    label: "WORKFLOW",
    items: [
      ["Qualified", "/qualified", BadgeCheck],
      ["Demos", "/demos", PanelsTopLeft],
      ["Enquiries", "/enquiries", Mail],
      ["Outreach", "/outreach", Send],
      ["Follow-ups", "/followups", RefreshCcw]
    ]
  },
  {
    label: "INSIGHTS",
    items: [["Analytics", "/analytics", BarChart3]]
  }
] as const;

export default function Sidebar({
  open,
  onClose
}: {
  open?: boolean;
  onClose?: () => void;
}) {
  const pathname = usePathname();

  return (
    <aside className={`sidebar ${open ? "open" : ""}`}>
      <div className="brand">
        <div className="brand-mark">L</div>
        <div className="brand-copy">
          <div className="brand-name">LeadHunter</div>
          <div className="brand-label">AI PLATFORM</div>
        </div>
        <button className="icon-btn" style={{ marginLeft: "auto", display: open ? "grid" : "none", background: "transparent", color: "#fff", borderColor: "transparent" }} onClick={onClose}>
          <X size={17} />
        </button>
      </div>

      <nav className="nav">
        {groups.map((group) => (
          <div className="nav-section" key={group.label}>
            <div className="nav-label">{group.label}</div>
            {group.items.map(([name, href, Icon]) => {
              const active = pathname === href || (href !== "/dashboard" && pathname.startsWith(href));
              return (
                <Link key={href} href={href} className={`nav-link ${active ? "active" : ""}`} onClick={onClose}>
                  <span className="nav-icon"><Icon size={15} strokeWidth={1.8} /></span>
                  <span>{name}</span>
                  {name === "Enquiries" && <span className="nav-count">3</span>}
                </Link>
              );
            })}
          </div>
        ))}
        <div className="nav-section">
          <div className="nav-label">SYSTEM</div>
          <Link href="/settings" className={`nav-link ${pathname.startsWith("/settings") ? "active" : ""}`} onClick={onClose}>
            <span className="nav-icon"><Settings size={15} strokeWidth={1.8} /></span>
            <span>Settings</span>
          </Link>
        </div>
      </nav>

      <div className="sidebar-bottom">
        <div className="user-card">
          <div className="user-mini">NS</div>
          <div>
            <div className="user-name">LeadHunter Admin</div>
            <div className="user-role">Admin</div>
          </div>
        </div>
      </div>
    </aside>
  );
}
