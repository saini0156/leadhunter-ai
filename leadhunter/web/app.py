"""LeadHunter AI — Web Control Dashboard Backend.

Full-stack FastAPI server managing lead operations, human approvals,
interactive pipeline execution, demo previews, and live telemetry.
"""

from __future__ import annotations

import csv
import io
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import Body, FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from ..approval.approval_queue import process_approval_queue
from ..config import Config, load_env_file, DEFAULT_CONFIG_PATH, DEFAULT_ENV_PATH
from ..db import Database
from ..demo.server import app as demo_sub_app
from ..demo.url_generator import process_and_generate_demo_urls
from ..discovery.serpapi_search import search_serpapi_google_maps
from ..followup.followup_engine import FollowupEngine
from ..log import get_logger, setup_logging
from ..models import Lead, LeadStatus, utcnow_iso
from ..outreach.email_sender import EmailSender, is_dry_run
from ..outreach.whatsapp_sender import WhatsAppSender
from ..processing.deduplicate import process_leads
from ..processing.lead_scorer import score_and_qualify_leads
from ..processing.website_checker import verify_leads_batch
from ..sheets_logger import SheetsLogger, sync_leads

log = get_logger("web_dashboard")

# Paths
BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
DEMO_TEMPLATES_DIR = BASE_DIR.parent / "demo" / "templates"

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="LeadHunter AI Web Control Dashboard", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Static Files
try:
    STATIC_DIR.mkdir(parents=True, exist_ok=True)
    (STATIC_DIR / "css").mkdir(parents=True, exist_ok=True)
    (STATIC_DIR / "js").mkdir(parents=True, exist_ok=True)
except OSError:
    pass
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Templates
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
demo_templates = Jinja2Templates(directory=str(DEMO_TEMPLATES_DIR))

# Global DB and Config access
_db_instance: Optional[Database] = None
_config_instance: Optional[Config] = None


DEFAULT_DATABASE_URL = "postgresql://postgres.hljpzgoduyzitiulmilm:SainiAnhad2224455@aws-0-ap-northeast-1.pooler.supabase.com:5432/postgres"

def get_db() -> Database:
    data_url = (os.getenv("DATABASE_URL") or DEFAULT_DATABASE_URL).strip()
    if not os.getenv("DATABASE_URL"):
        os.environ["DATABASE_URL"] = data_url

    if data_url.startswith(("postgresql://", "postgres://")):
        return Database("leadhunter.db")

    data_dir = os.path.join(os.getcwd(), "data")
    try:
        os.makedirs(data_dir, exist_ok=True)
        db_path = os.path.join(data_dir, "leadhunter.db")
        test_file = os.path.join(data_dir, ".writable_test")
        with open(test_file, "w") as f:
            f.write("1")
        os.remove(test_file)
    except Exception:
        db_path = "/tmp/leadhunter.db"

    return Database(db_path)


def get_cfg() -> Optional[Config]:
    global _config_instance
    if _config_instance is None:
        load_env_file(DEFAULT_ENV_PATH)
        try:
            _config_instance = Config.load()
        except Exception:
            _config_instance = None
    return _config_instance


# --------------------------------------------------------------------------
# Page Views & Demo Previews
# --------------------------------------------------------------------------

EXPECTED_PASSWORD = os.getenv("DASHBOARD_PASSWORD") or os.getenv("NEXT_PUBLIC_DASHBOARD_PASSWORD") or "admin123"

@app.get("/login", response_class=HTMLResponse)
def serve_login(request: Request):
    """Render admin security login page."""
    return templates.TemplateResponse(request=request, name="login.html", context={})


class LoginRequest(BaseModel):
    password: str


@app.post("/login")
def process_login(body: LoginRequest):
    """Validate admin password and set session cookie."""
    if body.password and body.password.strip() == EXPECTED_PASSWORD:
        resp = JSONResponse(content={"status": "ok", "message": "Authenticated successfully"})
        resp.set_cookie(key="leadhunter_auth_session", value="authenticated", max_age=86400, httponly=False, samesite="lax")
        return resp
    return JSONResponse(status_code=401, content={"status": "error", "message": "Invalid password. Please try again."})


@app.get("/logout")
def process_logout():
    """Clear session cookie and redirect to login."""
    from fastapi.responses import RedirectResponse
    resp = RedirectResponse(url="/login", status_code=302)
    resp.delete_cookie(key="leadhunter_auth_session")
    return resp


@app.get("/", response_class=HTMLResponse)
@app.get("/dashboard", response_class=HTMLResponse)
def serve_dashboard(request: Request):
    """Render main web control dashboard with session protection."""
    from fastapi.responses import RedirectResponse
    auth_cookie = request.cookies.get("leadhunter_auth_session")
    if not auth_cookie or auth_cookie != "authenticated":
        return RedirectResponse(url="/login?from=/dashboard", status_code=302)
    return templates.TemplateResponse(request=request, name="dashboard.html", context={})



@app.get("/preview", response_class=HTMLResponse)
@app.get("/preview/{slug:path}", response_class=HTMLResponse)
def serve_demo_preview(request: Request, slug: Optional[str] = None, lead_id: Optional[int] = None):
    """Serve live preview landing page for any lead slug or lead ID."""
    db = get_db()
    row = None

    # 1. Direct lead_id lookup
    if lead_id:
        row = db.conn.execute("SELECT * FROM leads WHERE id = ? LIMIT 1", (lead_id,)).fetchone()

    # 2. Check if slug is numeric ID
    if not row and slug and slug.isdigit():
        row = db.conn.execute("SELECT * FROM leads WHERE id = ? LIMIT 1", (int(slug),)).fetchone()

    # 3. Match demo_url contains slug
    if not row and slug:
        cur = db.conn.execute("SELECT * FROM leads WHERE demo_url LIKE ? LIMIT 1", (f"%{slug}%",))
        row = cur.fetchone()

    # 4. Match business name words
    if not row and slug:
        words = [w for w in re.sub(r'[^a-zA-Z0-9\s]', ' ', slug).split() if len(w) > 2]
        for w in words:
            cur = db.conn.execute("SELECT * FROM leads WHERE name LIKE ? LIMIT 1", (f"%{w}%",))
            row = cur.fetchone()
            if row:
                break

    # 5. Fallback to latest available lead in database
    if not row:
        cur = db.conn.execute("SELECT * FROM leads ORDER BY id DESC LIMIT 1")
        row = cur.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="No leads found in database")

    lead = Lead.from_row(dict(row))
    from ..demo.server import build_business_profile
    profile = build_business_profile(lead)
    from ..demo.niche_engine import resolve_niche_data
    combined_cat = f"{lead.category or ''} {slug or ''}"
    niche_info = resolve_niche_data(category=combined_cat, business_name=lead.name, city=lead.city)

    return demo_templates.TemplateResponse(
        request=request,
        name="preview.html",
        context={
            "lead": lead,
            "business_profile": profile,
            "business": profile,
            "profile": profile,
            "slug": slug or str(lead.id),
            "sender_name": "LeadHunter AI Studio",
            "n": niche_info,
        },
    )


# --------------------------------------------------------------------------
# REST API Endpoints
# --------------------------------------------------------------------------

@app.get("/api/stats")
def get_pipeline_stats(city: Optional[str] = None) -> Dict[str, Any]:
    """Return pipeline telemetry and stage metrics."""
    db = get_db()
    if city and city.strip() and city.lower() != "all":
        where_city = "WHERE LOWER(city) LIKE ?"
        and_city = "AND LOWER(city) LIKE ?"
        param = f"%{city.strip().lower()}%"
        params_w = (param,)
        params_a = (param,)
    else:
        where_city = ""
        and_city = ""
        params_w = ()
        params_a = ()

    def run_cnt(sql: str, p: tuple) -> int:
        cur = db.conn.execute(sql, p)
        row = cur.fetchone()
        return row[0] if row else 0

    total = run_cnt(f"SELECT COUNT(*) FROM leads {where_city}", params_w)
    discovered = run_cnt(f"SELECT COUNT(*) FROM leads WHERE status = 'DISCOVERED' {and_city}", params_a)
    hot = run_cnt(f"SELECT COUNT(*) FROM leads WHERE lead_tier = 'HOT' {and_city}", params_a)
    warm = run_cnt(f"SELECT COUNT(*) FROM leads WHERE lead_tier = 'WARM' {and_city}", params_a)
    demo_ready = run_cnt(f"SELECT COUNT(*) FROM leads WHERE demo_url IS NOT NULL AND demo_url != '' {and_city}", params_a)
    pending_approval = run_cnt("SELECT COUNT(*) FROM approvals WHERE approval_status = 'PENDING_APPROVAL'", ())
    sent = run_cnt(f"SELECT COUNT(*) FROM leads WHERE status = 'SENT' {and_city}", params_a)
    dry_run_sent = run_cnt(f"SELECT COUNT(*) FROM leads WHERE status = 'DRY_RUN_SENT' {and_city}", params_a)

    return {
        "status": "ok",
        "stats": {
            "total": total,
            "discovered": discovered,
            "hot": hot,
            "warm": warm,
            "demo_ready": demo_ready,
            "pending_approval": pending_approval,
            "sent": sent,
            "dry_run_sent": dry_run_sent,
        }
    }


@app.get("/api/leads")
def list_leads(
    city: Optional[str] = None,
    category: Optional[str] = None,
    tier: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = Query(500, ge=1, le=2000),
) -> Dict[str, Any]:
    """Query leads with case-insensitive multi-filter and search options."""
    db = get_db()
    conditions = []
    params = []

    if city and city.strip() and city.lower() != "all":
        conditions.append("LOWER(city) LIKE ?")
        params.append(f"%{city.strip().lower()}%")
    if category and category.strip() and category.lower() != "all":
        conditions.append("LOWER(category) LIKE ?")
        params.append(f"%{category.strip().lower()}%")
    if tier and tier.strip() and tier.lower() != "all":
        conditions.append("lead_tier = ?")
        params.append(tier.strip().upper())
    if status and status.strip() and status.lower() != "all":
        conditions.append("status = ?")
        params.append(status.strip().upper())
    if search and search.strip():
        q = f"%{search.strip().lower()}%"
        conditions.append("(LOWER(name) LIKE ? OR LOWER(phone) LIKE ? OR LOWER(address) LIKE ? OR LOWER(city) LIKE ? OR LOWER(category) LIKE ?)")
        params.extend([q, q, q, q, q])

    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
    query = f"SELECT * FROM leads {where_clause} ORDER BY id DESC LIMIT ?"
    params.append(limit)
    rows = db.conn.execute(query, tuple(params)).fetchall()

    leads = []
    for r in rows:
        lead_dict = dict(r)
        try:
            lead_dict["tags"] = json.loads(lead_dict.get("tags_json") or "{}")
        except Exception:
            lead_dict["tags"] = {}
        try:
            lead_dict["score_reasons"] = json.loads(lead_dict.get("score_reasons_json") or "[]")
        except Exception:
            lead_dict["score_reasons"] = []
        try:
            lead_dict["site_profile"] = json.loads(lead_dict.get("site_profile_json") or "{}")
        except Exception:
            lead_dict["site_profile"] = {}
        leads.append(lead_dict)

    return {"status": "ok", "count": len(leads), "leads": leads}


@app.get("/api/leads/{lead_id}")
def get_lead_detail(lead_id: int) -> Dict[str, Any]:
    """Fetch complete lead record and history."""
    db = get_db()
    row = db.conn.execute("SELECT * FROM leads WHERE id = ?", (lead_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Lead not found")

    lead_dict = dict(row)
    try:
        lead_dict["tags"] = json.loads(lead_dict.get("tags_json") or "{}")
        lead_dict["score_reasons"] = json.loads(lead_dict.get("score_reasons_json") or "[]")
        lead_dict["site_profile"] = json.loads(lead_dict.get("site_profile_json") or "{}")
    except Exception:
        pass

    return {"status": "ok", "lead": lead_dict}


class LeadUpdateRequest(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    city: Optional[str] = None
    category: Optional[str] = None
    website: Optional[str] = None
    website_status: Optional[str] = None
    lead_tier: Optional[str] = None
    score: Optional[float] = None
    status: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    personalized_message: Optional[str] = None
    whatsapp_message: Optional[str] = None
    email_message: Optional[str] = None


@app.put("/api/leads/{lead_id}")
def update_lead(lead_id: int, req: LeadUpdateRequest) -> Dict[str, Any]:
    """Update editable fields of a lead record."""
    db = get_db()
    row = db.conn.execute("SELECT * FROM leads WHERE id = ?", (lead_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Lead not found")

    payload = req.model_dump(exclude_unset=True)
    if not payload:
        return {"status": "ok", "message": "No changes provided"}

    updates = []
    params = []
    for col, val in payload.items():
        updates.append(f"{col} = ?")
        params.append(val)

    params.append(lead_id)
    sql = f"UPDATE leads SET {', '.join(updates)} WHERE id = ?"
    db.conn.execute(sql, tuple(params))
    db.conn.commit()

    return {"status": "ok", "message": f"Lead #{lead_id} updated successfully"}


@app.delete("/api/leads/{lead_id}")
def delete_lead(lead_id: int) -> Dict[str, Any]:
    """Permanently remove lead and associated approval queue entries."""
    db = get_db()
    row = db.conn.execute("SELECT * FROM leads WHERE id = ?", (lead_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Lead not found")

    db.conn.execute("DELETE FROM approvals WHERE lead_id = ?", (lead_id,))
    db.conn.execute("DELETE FROM leads WHERE id = ?", (lead_id,))
    db.conn.commit()
    return {"status": "ok", "message": f"Lead #{lead_id} deleted successfully"}


class BulkDeleteRequest(BaseModel):
    lead_ids: List[int]


@app.post("/api/leads/bulk-delete")
def bulk_delete_leads(req: BulkDeleteRequest) -> Dict[str, Any]:
    """Delete multiple selected leads at once."""
    if not req.lead_ids:
        return {"status": "ok", "message": "No leads selected", "deleted_count": 0}

    db = get_db()
    placeholders = ", ".join(["?"] * len(req.lead_ids))
    db.conn.execute(f"DELETE FROM approvals WHERE lead_id IN ({placeholders})", tuple(req.lead_ids))
    db.conn.execute(f"DELETE FROM leads WHERE id IN ({placeholders})", tuple(req.lead_ids))
    db.conn.commit()

    return {"status": "ok", "message": f"Successfully deleted {len(req.lead_ids)} leads", "deleted_count": len(req.lead_ids)}


@app.post("/api/leads/delete-all")
def delete_all_leads() -> Dict[str, Any]:
    """Permanently delete all leads and approvals across the database."""
    db = get_db()
    count_row = db.conn.execute("SELECT COUNT(*) FROM leads").fetchone()
    total = count_row[0] if count_row else 0

    db.conn.execute("DELETE FROM approvals")
    db.conn.execute("DELETE FROM leads")
    db.conn.commit()

    return {"status": "ok", "message": f"All {total} leads have been deleted.", "deleted_count": total}


class StageRequest(BaseModel):
    stage: str
    city: Optional[str] = "Vadodara"
    category: Optional[str] = "restaurants"
    country: Optional[str] = "Canada"
    service: Optional[str] = "Digital Marketing"
    limit: int = 10


@app.post("/api/pipeline/run-stage")
def execute_stage(req: StageRequest) -> Dict[str, Any]:
    """Execute a single or all pipeline stages on demand."""
    stage = req.stage.lower().strip()
    city = req.city or "Vadodara"
    category = req.category or "restaurants"
    country = req.country or "Canada"
    search_location = f"{city}, {country}" if country else city
    # Keep the same location string for every stage. Discovery stores this
    # full value in leads.city, so later stages must use it too.
    pipeline_city = search_location
    limit = req.limit
    db = get_db()
    cfg = get_cfg()

    try:
        if stage in ("discover", "discovery"):
            res_tuple = search_serpapi_google_maps(city=search_location, business_type=category, max_results=limit, db=db, config=cfg)
            raw_leads = res_tuple[0] if isinstance(res_tuple, tuple) else res_tuple
            proc_leads = process_leads(city=pipeline_city, db=db, config=cfg)
            count = len(raw_leads) if isinstance(raw_leads, list) else limit
            return {"status": "ok", "message": f"Successfully discovered {count} leads for {category} in {city}", "count": count}

        elif stage in ("verify", "verification"):
            v_res = verify_leads_batch(city=pipeline_city, limit=limit, db=db, config=cfg)
            v_count = len(v_res) if isinstance(v_res, list) else limit
            return {"status": "ok", "message": f"Website verification completed for {v_count} leads in {city}", "count": v_count}

        elif stage in ("score", "scoring", "qualify"):
            s_res = score_and_qualify_leads(city=pipeline_city, limit=limit, db=db, config=cfg, service=req.service or "")
            s_count = len(s_res) if isinstance(s_res, list) else limit
            return {"status": "ok", "message": f"Lead scoring completed for {s_count} leads in {city}", "count": s_count}

        elif stage in ("personalize", "personalizer", "ai"):
            from ..ai.personalizer import personalize_qualified_leads
            p_res = personalize_qualified_leads(city=pipeline_city, limit=limit, db=db, config=cfg, service=req.service or "")
            p_count = len(p_res) if isinstance(p_res, list) else limit
            return {"status": "ok", "message": f"AI personalization completed for {p_count} leads in {city}", "count": p_count}

        elif stage in ("demo", "demos", "url_generator"):
            d_res = process_and_generate_demo_urls(city=pipeline_city, limit=limit, db=db, config=cfg)
            d_count = len(d_res) if isinstance(d_res, list) else limit
            return {"status": "ok", "message": f"Demo URLs generated for {d_count} leads in {city}", "count": d_count}

        elif stage in ("approval", "queue_approvals"):
            a_res = process_approval_queue(city=pipeline_city, limit=limit, db=db, config=cfg)
            a_count = len(a_res) if isinstance(a_res, list) else limit
            return {"status": "ok", "message": f"Leads queued for human approval in {city}", "count": a_count}

        elif stage in ("outreach", "dispatch"):
            wa_sender = WhatsAppSender(config=cfg, db=db)
            wa_sender.process_approved_whatsapp(city=city, limit=limit)
            email_sender = EmailSender(config=cfg, db=db)
            email_sender.process_approved_emails(city=city, limit=limit)
            return {"status": "ok", "message": f"Outreach dispatch executed for {city}"}

        elif stage in ("followup", "followups"):
            engine = FollowupEngine(config=cfg, db=db)
            engine.check_and_stage_followups(city=city, limit=limit)
            return {"status": "ok", "message": f"Follow-up sequence executed for {city}"}

        elif stage in ("sync", "sheets"):
            sync_leads(city=pipeline_city, db=db, config=cfg)
            return {"status": "ok", "message": f"Synced with Google Sheets / Local CSV for {city}"}

        elif stage == "all":
            raw_leads = search_serpapi_google_maps(city=search_location, business_type=category, max_results=limit, db=db, config=cfg)
            process_leads(city=pipeline_city, db=db, config=cfg)
            verify_leads_batch(city=pipeline_city, limit=limit, db=db, config=cfg)
            score_and_qualify_leads(city=pipeline_city, limit=limit, db=db, config=cfg, service=req.service or "")
            from ..ai.personalizer import personalize_qualified_leads
            personalize_qualified_leads(city=pipeline_city, limit=limit, db=db, config=cfg, service=req.service or "")
            process_and_generate_demo_urls(city=pipeline_city, limit=limit, db=db, config=cfg)
            process_approval_queue(city=pipeline_city, limit=limit, db=db, config=cfg)
            sync_leads(city=pipeline_city, db=db, config=cfg)
            count = len(raw_leads) if isinstance(raw_leads, list) else limit
            return {"status": "ok", "message": f"Full pipeline executed! Processed {count} leads for {category} in {city}", "count": count}

        else:
            raise HTTPException(status_code=400, detail=f"Unknown pipeline stage: '{stage}'")

    except Exception as exc:
        log.error("Pipeline stage execution error [%s]: %s", stage, exc)
        return {"status": "error", "error": str(exc)}


@app.get("/api/approvals")
def get_pending_approvals(city: Optional[str] = None) -> Dict[str, Any]:
    """Retrieve all leads in human approval queue with case-insensitive city matching."""
    db = get_db()
    params = []
    if city and city.strip() and city.lower() != "all":
        city_clause = " AND LOWER(l.city) LIKE ?"
        params.append(f"%{city.strip().lower()}%")
    else:
        city_clause = ""
    query = (
        f"SELECT a.*, l.name, l.city, l.category, l.phone, l.email FROM approvals a "
        f"JOIN leads l ON a.lead_id = l.id "
        f"WHERE a.approval_status = 'PENDING_APPROVAL'{city_clause} ORDER BY a.lead_score DESC"
    )
    rows = db.conn.execute(query, tuple(params)).fetchall()
    return {"status": "ok", "leads": [dict(r) for r in rows]}


class ReviewDecisionRequest(BaseModel):
    decision: str  # 'APPROVE' or 'REJECT'
    notes: Optional[str] = ""


@app.post("/api/approvals/approve-all")
def approve_all_pending(city: Optional[str] = None) -> Dict[str, Any]:
    """Approve all leads currently pending in approval queue."""
    db = get_db()
    rows = db.conn.execute("SELECT lead_id FROM approvals WHERE approval_status = 'PENDING_APPROVAL'").fetchall()
    count = 0
    for r in rows:
        lid = int(r["lead_id"])
        submit_approval_decision(lid, ReviewDecisionRequest(decision="APPROVE"))
        count += 1
    return {"status": "ok", "count": count}


@app.post("/api/approvals/{lead_id}")
def submit_approval_decision(lead_id: int, req: ReviewDecisionRequest) -> Dict[str, Any]:
    """Update human approval decision for a specific lead."""
    db = get_db()
    now = utcnow_iso()
    decision = req.decision.upper().strip()

    if decision == "APPROVE":
        app_status = "APPROVED"
        lead_status = LeadStatus.APPROVED.value
    elif decision == "REJECT":
        app_status = "REJECTED"
        lead_status = LeadStatus.REJECTED.value
    else:
        raise HTTPException(status_code=400, detail="Invalid decision. Use APPROVE or REJECT.")

    # 1. Update approvals table
    db.conn.execute(
        "UPDATE approvals SET approval_status = ?, reviewed_at = ?, notes = ?, updated_at = ? WHERE lead_id = ?",
        (app_status, now, req.notes or "", now, lead_id),
    )

    # 2. Update leads table & transition
    lead = db.get_lead(lead_id)
    tags = lead.tags or {}
    tags["approval_status"] = app_status
    tags["reviewed_at"] = now

    db.update_lead(lead_id, {
        "tags_json": json.dumps(tags),
        "status": lead_status,
        "updated_at": now,
    })
    db.transition(
        lead_id=lead_id,
        to_status=lead_status,
        stage="web_approval",
        event=f"Lead marked {app_status} via Web Dashboard",
        level="INFO",
    )
    db.conn.commit()

    # Sync to sheets
    sheets = SheetsLogger(config=get_cfg(), db=db)
    sheets.sync_lead(db.get_lead(lead_id))

    # Auto-dispatch email outreach immediately on approval
    email_result = None
    if decision == "APPROVE":
        try:
            email_sender = EmailSender(config=get_cfg(), db=db)
            approved_lead = db.get_lead(lead_id)
            email_result = email_sender.send_email_to_lead(approved_lead)
        except Exception as exc:
            log.error("Auto email dispatch error on approval for lead #%d: %s", lead_id, exc)
            email_result = {"status": "ERROR", "error": str(exc)}

    return {"status": "ok", "lead_id": lead_id, "decision": app_status, "email_result": email_result}


@app.post("/api/config/dry-run")
def toggle_dry_run() -> Dict[str, Any]:
    """Toggle DRY_RUN safety mode live."""
    current = is_dry_run()
    new_val = not current
    os.environ["DRY_RUN"] = "true" if new_val else "false"
    return {"status": "ok", "dry_run": new_val}


@app.get("/api/logs")
def get_live_logs(limit: int = Query(40, ge=1, le=200)) -> Dict[str, Any]:
    """Stream recent system telemetry logs from database events & log files."""
    logs = []
    db = get_db()

    # 1. Fetch live events from DB lead_events table
    try:
        rows = db.conn.execute(
            "SELECT ts, level, stage, event FROM lead_events ORDER BY id DESC LIMIT ?",
            (limit,)
        ).fetchall()
        for r in reversed(rows):
            r_dict = dict(r) if hasattr(r, "keys") else {}
            ts = (r_dict.get("ts") or "")[:19]
            lvl = r_dict.get("level") or "INFO"
            stg = r_dict.get("stage") or "system"
            evt = r_dict.get("event") or ""
            logs.append(f"[{ts}] [{lvl}] [{stg}] {evt}")
    except Exception as exc:
        log.error("Error reading lead_events: %s", exc)

    # 2. Check log file locations
    possible_paths = [
        get_cfg().data_dir / "logs" / "leadhunter.log" if get_cfg() else None,
        Path("/tmp/leadhunter_data/logs/leadhunter.log"),
        Path("./data/logs/leadhunter.log"),
    ]

    for p in possible_paths:
        if p and p.exists():
            try:
                with open(p, "r", encoding="utf-8") as f:
                    file_lines = [line.strip() for line in f.readlines() if line.strip()]
                    if file_lines:
                        logs.extend(file_lines[-limit:])
                        break
            except Exception:
                pass

    if not logs:
        logs = [
            f"[{utcnow_iso()[:19]}] [INFO] [system] System Live • Pipeline Ready for Execution"
        ]

    return {"status": "ok", "logs": logs[-limit:]}


def _infer_lead_country(city: Optional[str], address: Optional[str]) -> str:
    """Best-effort country inference for legacy leads that have no country column."""
    text = f"{city or ''} {address or ''}".upper()
    canadian_markers = (
        "CANADA", " CN", ", ON", " ON ", ", BC", " BC ", ", AB", " AB ",
        ", MB", " MB ", ", SK", " SK ", ", NS", " NS ", ", NB", " NB ",
        ", NL", " NL ", ", PE", " PE ", ", QC", " QC ", ", NT", " NT ",
        ", YT", " YT ", ", NU", " NU ",
    )
    if any(marker in text for marker in canadian_markers) or text.strip().endswith(" CN"):
        return "Canada"
    if "INDIA" in text or any(x in text for x in (" GUJARAT", " PUNJAB", " HARYANA", " DELHI", " MAHARASHTRA", " RAJASTHAN", " KARNATAKA")):
        return "India"
    return "Other"


def _infer_outreach_problem_and_action(row_dict: dict) -> tuple[str, str]:
    """Infer human-readable outreach problem and recommended action for clean Excel exports."""
    email = (row_dict.get("email") or "").strip()
    phone = (row_dict.get("phone") or "").strip()
    status = (row_dict.get("status") or "").upper()
    outreach_status = (row_dict.get("outreach_status") or "").upper()
    outreach_channel = (row_dict.get("outreach_channel") or "").lower()
    last_error = (row_dict.get("last_error") or "").strip()
    web_status = (row_dict.get("website_status") or "").upper()

    if last_error:
        return f"Error: {last_error}", "Check system logs or API configuration"

    if status in ("REJECTED", "DO_NOT_CONTACT", "DISCARDED"):
        return "Opted Out / Rejected", "Do not contact (rejected by human reviewer)"

    if not email and not phone:
        return "Missing Contact Info (No Email or Phone)", "Find contact email/phone manually"

    if outreach_channel == "email" and not email:
        return "Missing Email Address", "Add email address to lead profile"

    if outreach_channel == "whatsapp" and not phone:
        return "Missing Phone Number", "Add phone number to lead profile"

    if status == "PENDING_APPROVAL":
        return "Awaiting Human Approval", "Review copy & approve in Dashboard Approval Queue"

    if status == "DRY_RUN_SENT" or outreach_status == "DRY_RUN_SENT":
        return "Dry Run Active (Simulated Delivery)", "Toggle DRY RUN to LIVE mode to dispatch real emails"

    if status == "FAILED" or outreach_status == "FAILED":
        return "Outreach Delivery Failed", "Retry outreach or check SMTP credentials"

    if status in ("SENT", "REPLIED", "CONVERTED") or outreach_status == "SENT":
        return "None (Successfully Delivered)", "Follow up / Close client deal"

    if web_status == "BROKEN_WEBSITE":
        return "Broken Website Discovered", "Pitch website repair / redesign demo"

    if web_status == "NO_WEBSITE":
        return "No Website Found", "Pitch new business website build"

    return "Not Contacted Yet", "Run pipeline stage to generate copy and dispatch"


@app.get("/api/export/csv")
def export_csv(
    city: Optional[str] = None,
    category: Optional[str] = None,
    tier: Optional[str] = None,
    status: Optional[str] = None,
    website_status: Optional[str] = None,
    country: Optional[str] = None,
    search: Optional[str] = None,
):
    """Export currently selected lead filters to CSV with Excel UTF-8 BOM compatibility and Outreach Problem Tracking."""
    db = get_db()
    conditions = []
    params = []

    def add_like(column: str, value: Optional[str]):
        if value and value.strip() and value.lower() != "all":
            conditions.append(f"LOWER({column}) LIKE ?")
            params.append(f"%{value.strip().lower()}%")

    add_like("city", city)
    add_like("category", category)
    if tier and tier.strip() and tier.lower() != "all":
        conditions.append("UPPER(COALESCE(lead_tier, '')) = ?")
        params.append(tier.strip().upper())
    if status and status.strip() and status.lower() != "all":
        conditions.append("UPPER(COALESCE(status, '')) = ?")
        params.append(status.strip().upper())
    if website_status and website_status.strip() and website_status.lower() != "all":
        conditions.append("UPPER(COALESCE(website_status, '')) = ?")
        params.append(website_status.strip().upper())
    if search and search.strip():
        q = f"%{search.strip().lower()}%"
        conditions.append("(LOWER(name) LIKE ? OR LOWER(phone) LIKE ? OR LOWER(address) LIKE ? OR LOWER(city) LIKE ? OR LOWER(category) LIKE ? OR CAST(id AS TEXT) LIKE ?)")
        params.extend([q, q, q, q, q, q])

    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
    rows = db.conn.execute(f"SELECT * FROM leads {where_clause} ORDER BY id ASC", tuple(params)).fetchall()

    # Filter country if requested
    if country and country.strip() and country.lower() != "all":
        wanted = country.strip().lower()
        rows = [r for r in rows if _infer_lead_country(r["city"], r["address"]).lower() == wanted]

    output = io.StringIO()
    # Add UTF-8 BOM so Excel opens UTF-8 characters properly
    output.write("\ufeff")

    # Define clean, human-readable fieldnames focused on essential sales details + full SEO audit & outreach problem detection
    export_fields = [
        "id", "name", "category", "city", "country", "phone", "email",
        "website", "website_status", "lead_tier", "score", "status",
        "seo_health_score", "load_time_sec", "speed_category", "ssl_status",
        "critical_problems", "seo_issues", "seo_opportunities", "est_monthly_revenue_loss",
        "outreach_channel", "outreach_status", "outreach_problem",
        "action_required", "demo_url", "created_at"
    ]
    writer = csv.DictWriter(output, fieldnames=export_fields, extrasaction="ignore")
    writer.writeheader()

    for r in rows:
        r_dict = dict(r)
        r_dict["country"] = _infer_lead_country(r_dict.get("city"), r_dict.get("address"))
        
        # Parse SEO Audit details from site_profile_json
        sp = {}
        if r_dict.get("site_profile_json"):
            try:
                sp = json.loads(r_dict["site_profile_json"])
            except Exception:
                pass
        seo = sp.get("seo_audit", {})
        
        health = seo.get("seo_health_score") if seo.get("seo_health_score") is not None else sp.get("seo_health_score")
        r_dict["seo_health_score"] = health if health is not None else "N/A"
        
        load_sec = seo.get("load_time_sec") or sp.get("load_time_sec")
        r_dict["load_time_sec"] = f"{load_sec}s" if load_sec is not None else "N/A"
        r_dict["speed_category"] = seo.get("speed_category") or sp.get("speed_category") or "N/A"
        r_dict["ssl_status"] = "HTTPS Enabled" if seo.get("has_ssl") is not False else "No SSL"
        
        crits = seo.get("critical_problems", [])
        r_dict["critical_problems"] = "; ".join(crits) if crits else "None"
        
        issues = seo.get("seo_issues", [])
        r_dict["seo_issues"] = "; ".join(issues) if issues else "None"
        
        opps = seo.get("seo_opportunities", [])
        r_dict["seo_opportunities"] = "; ".join(opps) if opps else "None"
        
        fin = seo.get("financial_impact", {})
        r_dict["est_monthly_revenue_loss"] = fin.get("formatted_loss_range") or "N/A"

        problem, action = _infer_outreach_problem_and_action(r_dict)
        r_dict["outreach_problem"] = problem
        r_dict["action_required"] = action
        writer.writerow(r_dict)

    output.seek(0)
    parts = ["leadhunter_export"]
    if country and country.lower() != "all": parts.append(country)
    if city and city.lower() != "all": parts.append(city)
    if tier and tier.lower() != "all": parts.append(tier)
    raw_name = "_".join(parts)
    safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', raw_name)
    filename = f"{safe_name}.csv"

    csv_data = output.getvalue().encode("utf-8")
    return Response(
        content=csv_data,
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Access-Control-Expose-Headers": "Content-Disposition",
        },
    )


def run_server(host: str = "0.0.0.0", port: int = 8000):
    """Launch uvicorn server programmatically."""
    import uvicorn
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_server()
