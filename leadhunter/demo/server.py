"""
LeadHunter AI Demo Server
FastAPI backend for:
- Lead discovery
- Lead listing
- Lead details
- Personalized demo websites
- Enquiry capture
- Dashboard statistics

Run:
    python -m uvicorn leadhunter.demo.server:app --host 127.0.0.1 --port 8500
"""

from __future__ import annotations

import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from leadhunter.db import Database
from leadhunter.discovery.serpapi_search import search_serpapi_google_maps


# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------

load_dotenv()


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("leadhunter.demo.server")


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = BASE_DIR / "templates"


# ---------------------------------------------------------------------------
# FastAPI
# ---------------------------------------------------------------------------

app = FastAPI(
    title="LeadHunter AI Demo Server",
    version="1.3.0",
    description="LeadHunter AI lead-generation and personalized demo backend.",
)


# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------

templates = Jinja2Templates(
    directory=str(TEMPLATE_DIR)
)


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def safe_string(value: Any, default: str = "") -> str:
    """
    Convert arbitrary database values safely to text.
    """
    if value is None:
        return default

    if isinstance(value, str):
        return value.strip()

    return str(value).strip()


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def safe_int(value: Any, default: int = 0) -> int:
    try:
        if value is None or value == "":
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


# ---------------------------------------------------------------------------
# Slug helpers
# ---------------------------------------------------------------------------

def slugify_lead(value: Any) -> str:
    """
    Convert text into a clean URL slug.

    IMPORTANT:
    Never pass a Lead object directly here.
    """

    text = safe_string(value)

    text = text.lower()

    text = re.sub(
        r"[^a-z0-9]+",
        "-",
        text,
    )

    text = re.sub(
        r"-+",
        "-",
        text,
    )

    return text.strip("-")


def lead_slug(lead: Mapping[str, Any]) -> str:
    """
    Generate a clean business slug.

    Example:
        Vantage Roofing Ltd. + Surrey, BC
        ->
        vantage-roofing-ltd-surrey-bc
    """

    business_name = safe_string(
        lead.get("name"),
        "local-business",
    )

    city = safe_string(
        lead.get("city"),
        "",
    )

    combined = f"{business_name}-{city}"

    return slugify_lead(combined)


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

def get_db() -> Database:
    return Database()


def lead_to_dict(lead: Any) -> Dict[str, Any]:
    """
    Convert Lead model / sqlite row / mapping into a plain dictionary.

    This function deliberately avoids treating dictionaries as keys,
    preventing 'unhashable type: dict' problems.
    """

    if lead is None:
        return {}

    if isinstance(lead, Mapping):
        return dict(lead)

    if hasattr(lead, "__dict__"):
        return dict(vars(lead))

    try:
        return dict(lead)
    except Exception:
        return {}


def get_lead_by_id(lead_id: int):
    db = get_db()

    try:
        try:
            return db.get_lead(int(lead_id))
        except Exception:
            cur = db.conn.execute("SELECT * FROM leads WHERE id = ? LIMIT 1", (int(lead_id),))
            row = cur.fetchone()
            if row:
                from leadhunter.models import Lead
                return Lead.from_row(dict(row))
            return None
    except Exception:
        return None
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Lead lookup
# ---------------------------------------------------------------------------

def find_lead_by_slug(slug: str):
    """
    Find a lead using the clean business/city slug.
    """

    requested_slug = slugify_lead(
        safe_string(slug)
    )

    db = get_db()

    try:
        leads = db.get_leads_by_statuses(
            statuses=[
                "DISCOVERED",
                "VERIFIED",
                "QUALIFIED",
                "PERSONALIZED",
                "DEMO_READY",
                "APPROVED",
                "SENT",
                "PENDING_APPROVAL",
            ],
            limit=5000,
        )

        # 1. Exact match on name-city slug
        for lead in leads:
            name = safe_string(getattr(lead, "name", ""))
            city = safe_string(getattr(lead, "city", ""))
            candidate_slug = slugify_lead(f"{name}-{city}")
            if candidate_slug == requested_slug:
                return lead

        # 2. Match on demo_url substring or name slug
        for lead in leads:
            demo_url = safe_string(getattr(lead, "demo_url", ""))
            name = safe_string(getattr(lead, "name", ""))
            if requested_slug and (requested_slug in demo_url or requested_slug == slugify_lead(name)):
                return lead

        return None

    finally:
        db.close()


def find_lead_by_slug_or_id(identifier: str):
    identifier = safe_string(identifier)

    if identifier.isdigit():
        return get_lead_by_id(
            int(identifier)
        )

    return find_lead_by_slug(
        identifier
    )


# ---------------------------------------------------------------------------
# Business profile
# ---------------------------------------------------------------------------

def resolve_category_design(category: str, business_name: str, city: str) -> Dict[str, Any]:
    from leadhunter.demo.niche_engine import resolve_niche_data

    c_str = city or "Surrey, BC"
    target = f"{category or ''} {business_name or ''}"
    b_name = business_name or "Local Business"
    niche = resolve_niche_data(category=target, business_name=b_name, city=c_str)

    accent = niche.get("accent_hex", "#f97316")

    pills = []
    if niche.get("booking_options"):
        for opt in niche["booking_options"]:
            pills.append({"name": opt, "val": opt})
    elif niche.get("services"):
        for s in niche["services"]:
            stitle = s.get("title", "") if isinstance(s, dict) else str(s)
            pills.append({"name": stitle, "val": stitle})

    if not pills:
        pills = [
            {"name": "Standard Service", "val": "Standard Service"},
            {"name": "Full Service", "val": "Full Service"}
        ]

    services_list = []
    if niche.get("services"):
        for s in niche["services"]:
            if isinstance(s, dict):
                services_list.append(s.get("title", ""))
            else:
                services_list.append(str(s))
    else:
        services_list = ["Professional Consultation", "Expert Service Execution", "Guaranteed Workmanship"]

    badge = niche.get("badge", f"Premier Services in {c_str}")
    if c_str not in badge:
        badge = f"{badge} in {c_str}"

    headline = niche.get("hero_title", f"Top-Rated Services in {c_str}")

    return {
        "accent_color": accent,
        "accent_dark": accent,
        "hero_image": niche.get("hero_img", "https://images.unsplash.com/photo-1632759145351-1d592919f522?auto=format&fit=crop&w=1600&q=85"),
        "hero_badge": badge,
        "hero_headline": headline,
        "pills": pills,
        "services": services_list
    }


def build_business_profile(lead: Any) -> Dict[str, Any]:
    """
    Build a safe normalized business profile for preview.html.

    All template fields are guaranteed to exist.
    """

    data = lead_to_dict(lead)

    name = safe_string(
        data.get("name"),
        "Local Business",
    )

    category = safe_string(
        data.get("category"),
        "Contractor",
    )

    city = safe_string(
        data.get("city"),
        "Surrey, BC",
    )

    address = safe_string(
        data.get("address"),
        "",
    )

    phone = safe_string(
        data.get("phone"),
        "",
    )

    email = safe_string(
        data.get("email"),
        "",
    )

    website = safe_string(
        data.get("website"),
        "",
    )

    website_status = safe_string(
        data.get("website_status"),
        "",
    )

    rating = safe_float(
        data.get("rating"),
        0,
    )

    reviews = safe_int(
        data.get("reviews_count"),
        0,
    )

    score = safe_float(
        data.get("score"),
        0,
    )

    tier = safe_string(
        data.get("lead_tier"),
        "COLD",
    ).upper()

    qualified = bool(
        data.get("qualified")
    )

    business_type = "local business"
    category_lower = category.lower()

    if any(k in category_lower for k in ["dent", "teeth", "smile", "ortho"]):
        business_type = "dental clinic"
    elif any(k in category_lower for k in ["plumb"]):
        business_type = "plumbing company"
    elif any(k in category_lower for k in ["hvac", "heat", "air", "cool"]):
        business_type = "HVAC company"
    elif any(k in category_lower for k in ["clean", "janitor", "maid"]):
        business_type = "cleaning company"
    elif any(k in category_lower for k in ["landscap", "lawn", "garden"]):
        business_type = "landscaping company"
    elif any(k in category_lower for k in ["cafe", "coffee", "bakery", "bake"]):
        business_type = "cafe & bakery"
    elif any(k in category_lower for k in ["restaur", "din", "food", "kitchen", "biryani"]):
        business_type = "restaurant"
    elif any(k in category_lower for k in ["salon", "spa", "beauty", "hair", "makeup"]):
        business_type = "salon & spa"
    elif any(k in category_lower for k in ["auto", "car", "mechanic", "garage", "detailing"]):
        business_type = "auto repair shop"
    elif any(k in category_lower for k in ["motorcycle", "bike", "two wheeler"]):
        business_type = "motorcycle shop"
    elif any(k in category_lower for k in ["real estate", "realtor", "property"]):
        business_type = "real estate agency"
    elif any(k in category_lower for k in ["electric"]):
        business_type = "electrician"
    elif any(k in category_lower for k in ["roof"]):
        business_type = "roofing company"
    elif any(k in category_lower for k in ["law", "legal", "advocate", "attorney", "ca"]):
        business_type = "law firm"
    elif any(k in category_lower for k in ["gym", "fitness", "workout"]):
        business_type = "fitness center"
    elif any(k in category_lower for k in ["doctor", "clinic", "medical", "hospital", "health"]):
        business_type = "medical clinic"
    elif any(k in category_lower for k in ["school", "coaching", "academy", "tuition"]):
        business_type = "educational academy"
    elif any(k in category_lower for k in ["sport", "turf", "cricket"]):
        business_type = "sports arena"
    elif category:
        business_type = category

    cat_design = resolve_category_design(category, name, city)
    services = cat_design["services"]
    service_area = city or "Local Area"

    return {
        "id": data.get("id"),
        "name": name,
        "business_name": name,
        "business_type": business_type,
        "category": category,
        "city": city,
        "address": address,
        "phone": phone,
        "email": email,
        "website": website,
        "website_status": website_status,
        "rating": rating,
        "reviews": reviews,
        "reviews_count": reviews,
        "score": score,
        "lead_tier": tier,
        "tier": tier,
        "qualified": qualified,
        "services": services,
        "service_area": service_area,
        "accent_color": cat_design["accent_color"],
        "accent_dark": cat_design["accent_dark"],
        "hero_image": cat_design["hero_image"],
        "hero_badge": cat_design["hero_badge"],
        "hero_headline": cat_design["hero_headline"],
        "pills": cat_design["pills"],
        "cta": f"Get a Free {business_type.title()} Quote",
    }

    return {
        "id": data.get("id"),

        "name": name,

        "business_name": name,

        "business_type": business_type,

        "category": category,

        "city": city,

        "address": address,

        "phone": phone,

        "email": email,

        "website": website,

        "website_status": website_status,

        "website_verified": bool(
            data.get("website_verified")
        ),

        "rating": rating,

        "reviews": reviews,

        "reviews_count": reviews,

        "score": score,

        "lead_tier": tier,

        "tier": tier,

        "qualified": qualified,

        "qualification_notes": safe_string(
            data.get("qualification_notes")
        ),

        "services": services,

        "service_area": service_area,

        "target_customers": [
            "Homeowners",
            "Property Owners",
            "Property Managers",
            "Commercial Customers",
        ],

        "goal": (
            f"Generate more {business_type} "
            f"enquiries and quote requests in {city}."
        ),

        "cta": (
            "Get a Free Roofing Quote"
            if "roof" in category_lower
            else f"Get a Free {business_type.title()} Quote"
        ),

        "email_subject": safe_string(
            data.get("email_subject")
        ),

        "email_message": safe_string(
            data.get("email_message")
        ),

        "whatsapp_message": safe_string(
            data.get("whatsapp_message")
        ),

        "personalized_message": safe_string(
            data.get("personalized_message")
        ),

        "demo_url": safe_string(
            data.get("demo_url")
        ),

        "demo_status": safe_string(
            data.get("demo_status")
        ),

        "seo_health": safe_float(
            data.get("seo_health_score"),
            60,
        ),

        "site_profile": data.get(
            "site_profile"
        ) or {},

        "seo": data.get(
            "seo"
        ) or {},

        "sections": [
            "Hero",
            "Services",
            "Why Choose Us",
            "Our Process",
            "Service Area",
            "Gallery",
            "FAQ",
            "Quote Form",
            "Contact",
        ],
    }


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------

class DiscoverRequest(BaseModel):
    city: str = Field(
        ...,
        min_length=2,
        max_length=120,
    )

    category: str = Field(
        ...,
        min_length=2,
        max_length=120,
    )

    lead_count: int = Field(
        default=25,
        ge=1,
        le=100,
    )


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    database_status = "UNKNOWN"

    db = None

    try:
        db = get_db()

        db.conn.execute(
            "SELECT 1"
        ).fetchone()

        database_status = "CONNECTED"

    except Exception as exc:
        database_status = f"ERROR: {exc}"

    finally:
        if db is not None:
            db.close()

    return {
        "status": "ok",
        "service": "leadhunter-demo-server",
        "database": database_status,
    }


# ---------------------------------------------------------------------------
# Root
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
def root():
    return """
    <!doctype html>
    <html>
    <head>
        <title>LeadHunter AI</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: #09090b;
                color: white;
                padding: 60px;
            }

            .box {
                max-width: 800px;
                margin: auto;
                padding: 40px;
                border: 1px solid #27272a;
                border-radius: 20px;
                background: #111113;
            }

            h1 {
                margin-bottom: 10px;
            }

            a {
                color: #f97316;
            }
        </style>
    </head>

    <body>
        <div class="box">
            <h1>LeadHunter AI</h1>

            <p>
                Lead generation and personalized website demo server.
            </p>

            <p>
                API:
                <a href="/health">Health</a>
            </p>

            <p>
                Use the Next.js frontend on port 3000.
            </p>
        </div>
    </body>
    </html>
    """


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------

@app.post("/api/discover")
def discover_leads(
    payload: DiscoverRequest,
):

    try:

        logger.info(
            "Discovery started | city=%s | category=%s | count=%s",
            payload.city,
            payload.category,
            payload.lead_count,
        )

        results, leads = search_serpapi_google_maps(
            city=payload.city,
            business_type=payload.category,
            max_results=payload.lead_count,
        )

        output = []

        for lead in leads:

            output.append(
                {
                    "id": getattr(
                        lead,
                        "id",
                        None,
                    ),

                    "name": getattr(
                        lead,
                        "name",
                        None,
                    ),

                    "city": getattr(
                        lead,
                        "city",
                        None,
                    ),

                    "category": getattr(
                        lead,
                        "category",
                        None,
                    ),

                    "website": getattr(
                        lead,
                        "website",
                        None,
                    ),

                    "phone": getattr(
                        lead,
                        "phone",
                        None,
                    ),

                    "status": getattr(
                        lead,
                        "status",
                        None,
                    ),
                }
            )

        logger.info(
            "Discovery completed | found=%s",
            len(leads),
        )

        return {
            "status": "success",

            "message": (
                f"Discovery completed. "
                f"{len(leads)} leads found."
            ),

            "count": len(leads),

            "results": results,

            "leads": output,
        }

    except Exception as exc:

        logger.exception(
            "Discovery failed"
        )

        raise HTTPException(
            status_code=500,
            detail=f"Discovery failed: {exc}",
        )


# ---------------------------------------------------------------------------
# Leads
# ---------------------------------------------------------------------------

@app.get("/api/leads")
def list_leads(
    status: Optional[str] = None,
    limit: int = 100,
):

    limit = max(
        1,
        min(
            int(limit),
            500,
        ),
    )

    db = None

    try:

        db = get_db()

        if status:

            lead_rows = db.get_leads_by_status(
                status=status,
                limit=limit,
            )

        else:

            lead_rows = db.get_leads_by_statuses(
                statuses=[
                    "DISCOVERED",
                    "VERIFIED",
                    "QUALIFIED",
                    "PERSONALIZED",
                    "DEMO_READY",
                    "APPROVED",
                    "SENT",
                    "PENDING_APPROVAL",
                ],
                limit=limit,
            )

        output = []

        for lead in lead_rows:

            output.append(
                {
                    "id": getattr(
                        lead,
                        "id",
                        None,
                    ),

                    "name": getattr(
                        lead,
                        "name",
                        None,
                    ),

                    "category": getattr(
                        lead,
                        "category",
                        None,
                    ),

                    "city": getattr(
                        lead,
                        "city",
                        None,
                    ),

                    "address": getattr(
                        lead,
                        "address",
                        None,
                    ),

                    "phone": getattr(
                        lead,
                        "phone",
                        None,
                    ),

                    "email": getattr(
                        lead,
                        "email",
                        None,
                    ),

                    "website": getattr(
                        lead,
                        "website",
                        None,
                    ),

                    "website_verified": getattr(
                        lead,
                        "website_verified",
                        False,
                    ),

                    "website_status": getattr(
                        lead,
                        "website_status",
                        None,
                    ),

                    "rating": getattr(
                        lead,
                        "rating",
                        0,
                    ),

                    "reviews": getattr(
                        lead,
                        "reviews_count",
                        0,
                    ),

                    "status": getattr(
                        lead,
                        "status",
                        None,
                    ),

                    "score": getattr(
                        lead,
                        "score",
                        0,
                    ) or 0,

                    "tier": getattr(
                        lead,
                        "lead_tier",
                        "COLD",
                    ) or "COLD",

                    "qualified": bool(
                        getattr(
                            lead,
                            "qualified",
                            False,
                        )
                    ),

                    "demo_url": getattr(
                        lead,
                        "demo_url",
                        None,
                    ),
                }
            )

        return {
            "status": "success",
            "count": len(output),
            "leads": output,
        }

    except Exception as exc:

        logger.exception(
            "Unable to load leads"
        )

        raise HTTPException(
            status_code=500,
            detail=f"Unable to load leads: {exc}",
        )

    finally:

        if db is not None:
            db.close()


# ---------------------------------------------------------------------------
# Lead detail
# ---------------------------------------------------------------------------

@app.get("/api/leads/{lead_id}")
def lead_detail(
    lead_id: int,
):

    db = None

    try:

        db = get_db()

        lead = db.get_lead(
            int(lead_id)
        )

        if lead is None:

            raise HTTPException(
                status_code=404,
                detail="Lead not found",
            )

        data = lead_to_dict(
            lead
        )

        profile = build_business_profile(
            lead
        )

        return {
            "status": "success",

            "lead": data,

            "business_profile": profile,

            "business": profile,
        }

    except HTTPException:
        raise

    except Exception as exc:

        logger.exception(
            "Unable to load lead %s",
            lead_id,
        )

        raise HTTPException(
            status_code=500,
            detail=f"Unable to load lead: {exc}",
        )

    finally:

        if db is not None:
            db.close()


# ---------------------------------------------------------------------------
# Preview by query
# ---------------------------------------------------------------------------

@app.get(
    "/preview",
    response_class=HTMLResponse,
)
def render_preview_query(
    request: Request,
    lead_id: Optional[int] = None,
):

    if lead_id is None:

        raise HTTPException(
            status_code=400,
            detail="lead_id is required",
        )

    try:

        lead = get_lead_by_id(
            int(lead_id)
        )

        if lead is None:

            raise HTTPException(
                status_code=404,
                detail="Lead not found",
            )

        profile = build_business_profile(
            lead
        )

        data = lead_to_dict(
            lead
        )

        # IMPORTANT:
        # preview.html expects business_profile.
        # We provide ALL aliases to keep template compatibility.

        context = {
            "request": request,

            "lead": lead,

            "lead_data": data,

            "business": profile,

            "business_profile": profile,

            "profile": profile,

            "demo": profile,
        }

        return templates.TemplateResponse(
            request=request,
            name="preview.html",
            context=context,
        )

    except HTTPException:
        raise

    except Exception as exc:

        logger.exception(
            "Preview query failed"
        )

        raise HTTPException(
            status_code=500,
            detail=f"Preview error: {type(exc).__name__}: {exc}",
        )


# ---------------------------------------------------------------------------
# Preview by clean slug
# ---------------------------------------------------------------------------

@app.get(
    "/preview/{slug}",
    response_class=HTMLResponse,
)
def preview(
    request: Request,
    slug: str,
):

    try:

        lead = find_lead_by_slug_or_id(
            slug
        )

        if lead is None:

            raise HTTPException(
                status_code=404,
                detail="Lead not found",
            )

        profile = build_business_profile(
            lead
        )

        if not isinstance(
            profile,
            dict,
        ):
            raise HTTPException(
                status_code=500,
                detail="Invalid business profile",
            )

        data = lead_to_dict(
            lead
        )

        context = {
            "request": request,

            "lead": lead,

            "lead_data": data,

            "business": profile,

            "business_profile": profile,

            "profile": profile,

            "demo": profile,
        }

        return templates.TemplateResponse(
            request=request,
            name="preview.html",
            context=context,
        )

    except HTTPException:
        raise

    except Exception as exc:

        logger.exception(
            "Preview failed for slug=%s",
            slug,
        )

        raise HTTPException(
            status_code=500,
            detail=f"Preview error: {type(exc).__name__}: {exc}",
        )


# ---------------------------------------------------------------------------
# Enquiry
# ---------------------------------------------------------------------------

@app.post("/api/enquiry")
def create_enquiry(
    lead_id: int = Form(...),
    name: str = Form(...),
    phone: str = Form(""),
    email: str = Form(""),
    service: str = Form(""),
    message: str = Form(""),
    website: str = Form(""),
):

    name = safe_string(name)
    phone = safe_string(phone)
    email = safe_string(email)
    service = safe_string(service)
    message = safe_string(message)
    website = safe_string(website)

    if not name:

        raise HTTPException(
            status_code=400,
            detail="Name is required",
        )

    if website:

        raise HTTPException(
            status_code=400,
            detail="Invalid enquiry",
        )

    if email:

        email_pattern = (
            r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
        )

        if not re.match(
            email_pattern,
            email,
        ):

            raise HTTPException(
                status_code=400,
                detail="Invalid email address",
            )

    db = None

    try:

        db = get_db()

        enquiry_data = {
            "lead_id": int(lead_id),
            "name": name,
            "phone": phone,
            "email": email,
            "service": service,
            "message": message,
        }

        if hasattr(
            db,
            "create_enquiry",
        ):

            result = db.create_enquiry(
                **enquiry_data
            )

        elif hasattr(
            db,
            "insert_enquiry",
        ):

            result = db.insert_enquiry(
                enquiry_data
            )

        else:

            raise RuntimeError(
                "Database enquiry method is unavailable."
            )

        return {
            "status": "success",
            "message": (
                "Thanks! Your enquiry has been received."
            ),
            "enquiry": result,
        }

    except HTTPException:
        raise

    except Exception as exc:

        logger.exception(
            "Enquiry creation failed"
        )

        raise HTTPException(
            status_code=500,
            detail=f"Unable to create enquiry: {exc}",
        )

    finally:

        if db is not None:
            db.close()


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

@app.get("/api/dashboard/summary")
def dashboard_summary():

    db = None

    try:

        db = get_db()

        def count_status(status: str) -> int:

            try:

                rows = db.get_leads_by_status(
                    status=status,
                    limit=100000,
                )

                return len(rows)

            except Exception:

                return 0

        discovered = count_status(
            "DISCOVERED"
        )

        verified = count_status(
            "VERIFIED"
        )

        qualified = count_status(
            "QUALIFIED"
        )

        personalized = count_status(
            "PERSONALIZED"
        )

        demo_ready = count_status(
            "DEMO_READY"
        )

        approved = count_status(
            "APPROVED"
        )

        sent = count_status(
            "SENT"
        )

        try:

            total_rows = db.get_leads_by_statuses(
                statuses=[
                    "DISCOVERED",
                    "VERIFIED",
                    "QUALIFIED",
                    "PERSONALIZED",
                    "DEMO_READY",
                    "APPROVED",
                    "SENT",
                    "PENDING_APPROVAL",
                ],
                limit=100000,
            )

            total = len(total_rows)

        except Exception:

            total = (
                discovered
                + verified
                + qualified
                + personalized
                + demo_ready
                + approved
                + sent
            )

        return {
            "status": "success",

            "total_leads": total,

            "qualified_leads": qualified,

            "demo_websites": demo_ready,

            "approved_leads": approved,

            "sent_leads": sent,

            "pipeline": {
                "discovered": discovered,
                "verified": verified,
                "qualified": qualified,
                "personalized": personalized,
                "demo_ready": demo_ready,
                "approved": approved,
                "sent": sent,
            },

            "system": {
                "api": "online",
                "database": "connected",
            },
        }

    except Exception as exc:

        logger.exception(
            "Dashboard summary failed"
        )

        raise HTTPException(
            status_code=500,
            detail=f"Dashboard error: {exc}",
        )

    finally:

        if db is not None:
            db.close()


# ---------------------------------------------------------------------------
# Development entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "leadhunter.demo.server:app",
        host="127.0.0.1",
        port=8500,
        reload=False,
    )