"""
LeadHunter AI Demo URL Generator

Creates clean personalized demo URLs.

Example:

https://example.com/preview/vantage-roofing-ltd-surrey-bc
"""

from __future__ import annotations

import logging
import os
import re
from typing import Any, Dict, List, Optional

import requests
from dotenv import load_dotenv

from ..db import Database


load_dotenv()

logger = logging.getLogger(
    "leadhunter.demo.url_generator"
)


# ---------------------------------------------------------------------------
# Slug
# ---------------------------------------------------------------------------

def slugify(value: Any) -> str:

    text = str(
        value or ""
    ).strip().lower()

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


def build_demo_slug(lead: Any) -> str:

    name = getattr(
        lead,
        "name",
        "",
    )

    city = getattr(
        lead,
        "city",
        "",
    )

    return slugify(
        f"{name}-{city}"
    )


# ---------------------------------------------------------------------------
# Base URL
# ---------------------------------------------------------------------------

def get_demo_base_url() -> str:
    base_url = os.getenv("DEMO_BASE_URL", "").strip().rstrip("/")
    if not base_url or "trycloudflare.com" in base_url or "ngrok" in base_url or "127.0.0.1" in base_url or "localhost" in base_url:
        return ""
    if base_url.endswith("/preview"):
        base_url = base_url[:-len("/preview")]
    return base_url.rstrip("/")


# ---------------------------------------------------------------------------
# Demo URL
# ---------------------------------------------------------------------------

def build_demo_url(
    lead: Any,
    base_url: Optional[str] = None,
) -> str:

    base = (
        base_url.rstrip("/")
        if base_url
        else get_demo_base_url()
    )

    slug = build_demo_slug(
        lead
    )

    return (
        f"{base}/preview/{slug}"
    )


def build_fallback_demo_url(
    lead: Any,
    base_url: Optional[str] = None,
) -> str:

    base = (
        base_url.rstrip("/")
        if base_url
        else get_demo_base_url()
    )

    lead_id = getattr(
        lead,
        "id",
        None,
    )

    return (
        f"{base}/preview?lead_id={lead_id}"
    )


# ---------------------------------------------------------------------------
# Text replacement
# ---------------------------------------------------------------------------

def replace_demo_url(
    text: Optional[str],
    demo_url: str,
) -> str:

    if not text:
        return ""

    return str(text).replace(
        "{{DEMO_URL}}",
        demo_url,
    )


# ---------------------------------------------------------------------------
# URL verification
# ---------------------------------------------------------------------------

def verify_demo_url(
    url: str,
    timeout: int = 10,
) -> bool:

    if not url:
        return False

    try:

        response = requests.get(
            url,
            timeout=timeout,
            allow_redirects=True,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(LeadHunter AI Demo Validator)"
                )
            },
        )

        return (
            200
            <= response.status_code
            < 400
        )

    except requests.RequestException as exc:

        logger.warning(
            "Demo URL verification failed: %s",
            exc,
        )

        return False


# ---------------------------------------------------------------------------
# Database update
# ---------------------------------------------------------------------------

def update_demo_fields(
    db: Database,
    lead_id: int,
    demo_url: str,
    demo_status: str = "READY",
) -> None:

    fields = {
        "demo_url": demo_url,
        "demo_status": demo_status,
    }

    db.update_lead(
        int(lead_id),
        fields,
    )


# ---------------------------------------------------------------------------
# Generate one URL
# ---------------------------------------------------------------------------

def generate_demo_url_for_lead(
    lead: Any,
    db: Optional[Database] = None,
    verify: bool = False,
) -> str:

    demo_url = build_demo_url(
        lead
    )

    lead_id = getattr(
        lead,
        "id",
        None,
    )

    demo_status = "READY"

    if verify:

        if not verify_demo_url(
            demo_url
        ):

            demo_status = "FAILED"

            demo_url = (
                build_fallback_demo_url(
                    lead
                )
            )

    if db is not None and lead_id:

        try:

            update_demo_fields(
                db=db,
                lead_id=int(lead_id),
                demo_url=demo_url,
                demo_status=demo_status,
            )

        except Exception as exc:

            logger.warning(
                "Could not update demo fields for lead %s: %s",
                lead_id,
                exc,
            )

    return demo_url


# ---------------------------------------------------------------------------
# Generate URLs for leads
# ---------------------------------------------------------------------------

def generate_lead_demo_urls(
    leads: Optional[Any] = None,
    db: Optional[Database] = None,
    verify: bool = False,
    city: Optional[str] = None,
    limit: int = 100,
) -> Any:

    own_db = False
    single_lead = False

    if db is None:

        db = Database()

        own_db = True

    try:

        if leads is None:

            leads = db.get_leads_by_statuses(
                statuses=[
                    "PERSONALIZED",
                    "DEMO_READY",
                    "QUALIFIED",
                ],
                city=city,
                limit=limit,
            )
        elif not isinstance(leads, (list, tuple, set)):
            single_lead = True
            leads = [leads]

        output = []

        for lead in leads:

            demo_url = (
                generate_demo_url_for_lead(
                    lead=lead,
                    db=db,
                    verify=verify,
                )
            )

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
                        "",
                    ),

                    "city": getattr(
                        lead,
                        "city",
                        "",
                    ),

                    "slug": build_demo_slug(
                        lead
                    ),

                    "demo_url": demo_url,

                    "status": "READY",
                }
            )

        db.conn.commit()

        if single_lead and output:
            item = output[0]
            return (item["slug"], item["demo_url"], item["demo_url"])

        return output

    finally:

        if own_db:

            db.close()


# ---------------------------------------------------------------------------
# Compatibility aliases
# ---------------------------------------------------------------------------

def generate_demo_urls(
    leads: Optional[List[Any]] = None,
    db: Optional[Database] = None,
    verify: bool = False,
    city: Optional[str] = None,
    limit: int = 100,
):

    return generate_lead_demo_urls(
        leads=leads,
        db=db,
        verify=verify,
        city=city,
        limit=limit,
    )


def process_and_generate_demo_urls(
    db: Optional[Database] = None,
    verify: bool = False,
    city: Optional[str] = None,
    limit: int = 100,
):

    return generate_lead_demo_urls(
        leads=None,
        db=db,
        verify=verify,
        city=city,
        limit=limit,
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():

    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(message)s"
        ),
    )

    results = (
        generate_lead_demo_urls(
            verify=False
        )
    )

    print(
        "\nLeadHunter AI — Demo URLs\n"
    )

    for result in results:

        print(
            f"{result['id']} | "
            f"{result['name']} | "
            f"{result['demo_url']}"
        )


if __name__ == "__main__":
    main()