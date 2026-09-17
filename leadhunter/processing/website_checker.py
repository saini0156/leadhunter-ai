"""Website verification module for LeadHunter AI.

Inspects business websites for leads with status DISCOVERED or ENRICHED:
- Performs HTTP GET requests via httpx with 10s timeout, following redirects
- Classifies into: VALID_WEBSITE, BROKEN_WEBSITE, NO_WEBSITE, SOCIAL_ONLY,
  DIRECTORY_ONLY, DOMAIN_ONLY, UNKNOWN
- Performs secondary SerpAPI search for leads without a claimed website
- Checks page title and content to verify business match
- Never treats social or directory profiles as a website
- Updates lead records with website_status and transitions to VERIFIED
- Applies a polite delay between checks
"""

from __future__ import annotations

import difflib
import json
import os
import re
import ssl
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import urlparse

import httpx
import serpapi

from ..config import Config, load_env_file, DEFAULT_CONFIG_PATH, DEFAULT_ENV_PATH
from ..db import Database
from ..discovery.serpapi_search import get_serpapi_key, get_serpapi_keys_pool
from ..log import get_logger, setup_logging
from ..models import Lead, LeadStatus
from .normalize import extract_domain, normalize_name, normalize_website
from .seo_auditor import audit_website_seo

log = get_logger("website_checker")

# Website Status Classifications
STATUS_VALID_WEBSITE = "VALID_WEBSITE"
STATUS_BROKEN_WEBSITE = "BROKEN_WEBSITE"
STATUS_NO_WEBSITE = "NO_WEBSITE"
STATUS_SOCIAL_ONLY = "SOCIAL_ONLY"
STATUS_DIRECTORY_ONLY = "DIRECTORY_ONLY"
STATUS_DOMAIN_ONLY = "DOMAIN_ONLY"
STATUS_UNKNOWN = "UNKNOWN"

ALL_WEBSITE_STATUSES = {
    STATUS_VALID_WEBSITE,
    STATUS_BROKEN_WEBSITE,
    STATUS_NO_WEBSITE,
    STATUS_SOCIAL_ONLY,
    STATUS_DIRECTORY_ONLY,
    STATUS_DOMAIN_ONLY,
    STATUS_UNKNOWN,
}

SOCIAL_DOMAINS: Set[str] = {
    "facebook.com",
    "instagram.com",
    "fb.com",
    "twitter.com",
    "x.com",
    "linkedin.com",
    "youtube.com",
    "threads.net",
    "pinterest.com",
    "tiktok.com",
}

DIRECTORY_DOMAINS: Set[str] = {
    "justdial.com",
    "sulekha.com",
    "indiamart.com",
    "tradeindia.com",
    "zomato.com",
    "swiggy.com",
    "magicpin.in",
    "dineout.co.in",
    "tripadvisor.com",
    "tripadvisor.in",
    "eattreat.in",
    "yellowpages.com",
    "nearbuy.com",
    "eatsure.com",
    "google.com",
    "maps.google.com",
    "goo.gl",
    "linktr.ee",
}

PARKED_INDICATORS: List[str] = [
    "domain parked",
    "domain is for sale",
    "buy this domain",
    "under construction",
    "coming soon",
    "godaddy",
    "namecheap",
    "dan.com",
    "sedoparking",
    "hugedomains",
    "apache2 debian default page",
    "default web site page",
    "welcome to nginx",
    "this domain may be for sale",
]

_TITLE_TAG = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)
_HTML_TAGS = re.compile(r"<[^>]+>")
_WS = re.compile(r"\s+")
_EMAIL_REGEX = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")


def extract_emails_from_html(html: str) -> List[str]:
    """Extract valid business contact emails from raw website HTML."""
    if not html:
        return []
    matches = _EMAIL_REGEX.findall(html)
    found: List[str] = []
    ignore_list = {
        "example.com", "wixpress.com", "sentry.io", "schema.org", "domain.com",
        "googleapis.com", "gravatar.com", "format.com", "bootstrap.com",
        "fontawesome.com", "cloudflare.com", "godaddy.com", "namecheap.com",
        "w3.org", "wordpress.org", "jquery.com", "yoast.com"
    }
    for m in matches:
        m_low = m.lower().strip()
        if any(m_low.endswith(ext) for ext in (".png", ".jpg", ".jpeg", ".gif", ".svg", ".css", ".js", ".webp", ".woff")):
            continue
        parts = m_low.split("@")
        if len(parts) == 2 and parts[1] not in ignore_list and not any(parts[1].endswith("." + ig) for ig in ignore_list):
            if m_low not in found:
                found.append(m_low)
    return found

HTTP_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}


def classify_url_domain(url: Optional[str]) -> Optional[str]:
    """Check if URL belongs to a known social platform or directory."""
    if not url:
        return None
    domain = extract_domain(url)
    if not domain:
        return None

    # Check root and subdomains against social domains
    for s_dom in SOCIAL_DOMAINS:
        if domain == s_dom or domain.endswith("." + s_dom):
            return STATUS_SOCIAL_ONLY

    # Check root and subdomains against directory domains
    for d_dom in DIRECTORY_DOMAINS:
        if domain == d_dom or domain.endswith("." + d_dom):
            return STATUS_DIRECTORY_ONLY

    return None


def extract_page_title(html: str) -> str:
    """Extract and clean <title> text from HTML."""
    match = _TITLE_TAG.search(html)
    if match:
        raw_title = _HTML_TAGS.sub("", match.group(1))
        return _WS.sub(" ", raw_title).strip()
    return ""


def is_parked_domain(html: str, title: str) -> bool:
    """Detect if page is a domain parking / for-sale placeholder."""
    lowered_title = title.lower()
    lowered_html = html[:4000].lower()
    for ind in PARKED_INDICATORS:
        if ind in lowered_title or ind in lowered_html:
            return True
    return False


def page_matches_business_name(business_name: str, title: str, html: str) -> bool:
    """Verify if HTML title or content matches business name tokens."""
    norm_biz = normalize_name(business_name)
    biz_tokens = {t for t in norm_biz.split() if len(t) > 2}
    if not biz_tokens:
        return True

    norm_title = normalize_name(title)
    title_tokens = set(norm_title.split())

    # If title has significant token overlap with business name
    if biz_tokens & title_tokens:
        return True

    # Check title similarity
    if norm_biz and norm_title:
        similarity = difflib.SequenceMatcher(None, norm_biz, norm_title).ratio()
        if similarity >= 0.4:
            return True

    # Check body text (first 3000 chars)
    body_snippet = _HTML_TAGS.sub(" ", html[:3000]).lower()
    body_snippet_norm = normalize_name(body_snippet)
    matched_count = sum(1 for token in biz_tokens if token in body_snippet_norm)
    return matched_count >= max(1, len(biz_tokens) // 2)


def check_url_with_httpx(url: str, business_name: str) -> Tuple[str, Dict[str, Any]]:
    """Perform HTTP GET request and inspect site response with Senior SEO auditing.

    Returns:
        (website_status, site_profile_dict)
    """
    profile: Dict[str, Any] = {
        "url": url,
        "final_url": url,
        "status_code": None,
        "title": "",
        "error": None,
        "is_matching": False,
        "load_time_sec": None,
        "seo_audit": {},
    }

    # First check if domain is social or directory
    domain_type = classify_url_domain(url)
    if domain_type == STATUS_SOCIAL_ONLY:
        profile["classification"] = STATUS_SOCIAL_ONLY
        return STATUS_SOCIAL_ONLY, profile
    elif domain_type == STATUS_DIRECTORY_ONLY:
        profile["classification"] = STATUS_DIRECTORY_ONLY
        return STATUS_DIRECTORY_ONLY, profile

    # Ensure valid scheme
    target_url = url
    if not target_url.startswith(("http://", "https://")):
        target_url = "https://" + target_url

    start_time = time.time()
    try:
        with httpx.Client(
            timeout=12.0,
            follow_redirects=True,
            headers=HTTP_HEADERS,
            verify=False,  # Still check site even with self-signed SSL
        ) as client:
            resp = client.get(target_url)
            duration = time.time() - start_time
            profile["status_code"] = resp.status_code
            profile["final_url"] = str(resp.url)
            profile["load_time_sec"] = round(duration, 2)

            # Check final redirected URL domain as well
            redir_type = classify_url_domain(str(resp.url))
            if redir_type in (STATUS_SOCIAL_ONLY, STATUS_DIRECTORY_ONLY):
                profile["classification"] = redir_type
                return redir_type, profile

            if resp.status_code == 200:
                html = resp.text
                title = extract_page_title(html)
                profile["title"] = title
                extracted = extract_emails_from_html(html)
                profile["extracted_emails"] = extracted
                if extracted:
                    profile["extracted_email"] = extracted[0]

                # Senior SEO Recruiter audit
                seo_audit = audit_website_seo(
                    url=profile["final_url"],
                    html_content=html,
                    response_time_sec=duration,
                    status_code=resp.status_code,
                )
                profile["seo_audit"] = seo_audit
                profile["seo_health_score"] = seo_audit.get("seo_health_score", 70)
                profile["speed_category"] = seo_audit.get("speed_category", "MODERATE")
                profile["seo_issues"] = seo_audit.get("seo_issues", [])

                # Check for parked domain
                if is_parked_domain(html, title):
                    profile["classification"] = STATUS_DOMAIN_ONLY
                    return STATUS_DOMAIN_ONLY, profile

                # Business title/content check
                matches = page_matches_business_name(business_name, title, html)
                profile["is_matching"] = matches
                profile["classification"] = STATUS_VALID_WEBSITE
                return STATUS_VALID_WEBSITE, profile

            elif resp.status_code in (403, 401, 503):
                # Bot protection / Cloudflare blocking standard GET scraper
                profile["error"] = f"HTTP {resp.status_code} Protection/Access Challenge"
                profile["classification"] = STATUS_VALID_WEBSITE
                profile["seo_audit"] = {
                    "load_time_sec": round(duration, 2),
                    "speed_category": "MODERATE",
                    "seo_health_score": 60,
                    "seo_issues": [f"HTTP {resp.status_code} WAF / Bot Security challenge enabled"],
                }
                return STATUS_VALID_WEBSITE, profile

            else:
                profile["error"] = f"HTTP {resp.status_code}"
                profile["classification"] = STATUS_BROKEN_WEBSITE
                return STATUS_BROKEN_WEBSITE, profile

    except Exception as exc:
        duration = time.time() - start_time
        from ..utils.error_handler import log_error
        log_error(exc, context=f"Website Checker '{url}'")
        profile["error"] = f"HTTP request error: {exc}"
        profile["load_time_sec"] = round(duration, 2)

        # Fallback using requests if available
        try:
            import requests
            req_resp = requests.get(target_url, headers=HTTP_HEADERS, timeout=8, verify=False)
            if req_resp.status_code == 200:
                html = req_resp.text
                title = extract_page_title(html)
                profile["status_code"] = 200
                profile["title"] = title
                profile["final_url"] = req_resp.url
                seo_audit = audit_website_seo(req_resp.url, html, duration, 200)
                profile["seo_audit"] = seo_audit
                profile["seo_health_score"] = seo_audit.get("seo_health_score", 70)
                profile["classification"] = STATUS_VALID_WEBSITE
                return STATUS_VALID_WEBSITE, profile
        except Exception:
            pass

        # If domain exists and belongs to lead, preserve it as VALID_WEBSITE or BROKEN_WEBSITE (never drop to NO_WEBSITE)
        domain = extract_domain(url)
        if domain and len(domain) > 3:
            profile["classification"] = STATUS_VALID_WEBSITE
            profile["seo_audit"] = {
                "load_time_sec": round(duration, 2),
                "speed_category": "CRITICAL_SLOW",
                "seo_health_score": 45,
                "seo_issues": [f"Connection timeout/latency: {exc}"],
            }
            return STATUS_VALID_WEBSITE, profile

        profile["classification"] = STATUS_BROKEN_WEBSITE
        return STATUS_BROKEN_WEBSITE, profile


def _country_google_code(city: str) -> str:
    """Best-effort Google country code for localized business searches.

    IMPORTANT: the database currently stores the search city separately from
    the country. Never default an unknown city to India because that can send
    a UK/Canada/etc. business search to the wrong market.
    """
    c = (city or "").strip().lower()
    mapping = {
        # Canada
        "canada": "ca", "ontario": "ca", "british columbia": "ca", "alberta": "ca",
        "surrey": "ca", "brampton": "ca", "toronto": "ca", "mississauga": "ca",
        "vancouver": "ca", "calgary": "ca", "edmonton": "ca", "ottawa": "ca",
        # United Kingdom
        "uk": "gb", "united kingdom": "gb", "england": "gb", "scotland": "gb",
        "manchester": "gb", "birmingham": "gb", "leeds": "gb", "glasgow": "gb",
        "liverpool": "gb", "bristol": "gb", "sheffield": "gb", "nottingham": "gb",
        "london": "gb", "rochdale": "gb", "bolton": "gb",
        # Australia
        "australia": "au", "sydney": "au", "melbourne": "au", "brisbane": "au",
        # UAE
        "uae": "ae", "united arab emirates": "ae", "dubai": "ae", "sharjah": "ae",
        "ajman": "ae", "abu dhabi": "ae",
        # USA
        "usa": "us", "united states": "us",
        # India
        "india": "in", "vadodara": "in", "ahmedabad": "in", "delhi": "in",
        "mumbai": "in", "pune": "in", "bangalore": "in", "hyderabad": "in",
        # Other configured markets
        "saudi arabia": "sa", "qatar": "qa", "new zealand": "nz",
        "germany": "de", "france": "fr", "singapore": "sg",
        "netherlands": "nl", "ireland": "ie", "switzerland": "ch",
        "south africa": "za",
    }
    for marker, code in mapping.items():
        if c == marker or marker in c:
            return code
    # Safe neutral fallback: do not force an unknown market to India.
    return ""


def _candidate_website_score(business_name: str, city: str, result: Dict[str, Any], url: str) -> int:
    """Score a Google result before accepting it as the business's official site."""
    biz = normalize_name(business_name)
    city_norm = normalize_name(city)
    tokens = [t for t in biz.split() if len(t) > 2]
    title = normalize_name(str(result.get("title") or ""))
    snippet = normalize_name(str(result.get("snippet") or ""))
    displayed = normalize_name(str(result.get("displayed_link") or ""))
    domain = normalize_name(extract_domain(url) or "")
    haystack = " ".join([title, snippet, displayed, domain])

    score = 0
    matched = sum(1 for t in tokens if t in haystack)
    if tokens:
        ratio = matched / len(tokens)
        if ratio >= 0.75:
            score += 60
        elif ratio >= 0.5:
            score += 35
        elif ratio >= 0.25:
            score += 15
    if biz and biz in title:
        score += 25
    if city_norm and any(part and part in haystack for part in city_norm.split() if len(part) > 3):
        score += 10
    if domain and any(t in domain for t in tokens):
        score += 15
    return score


def search_official_website_via_serpapi(
    business_name: str,
    city: str,
    api_key: Optional[str] = None,
) -> Tuple[Optional[str], Optional[str]]:
    """Find and verify a likely official website; never accept the first generic result."""
    keys = [api_key] if api_key else get_serpapi_keys_pool()
    keys = [k for k in keys if k]
    if not keys:
        return None, None

    queries = [
        f'"{business_name}" "{city}" website',
        f'"{business_name}" "{city}" official website',
        f'"{business_name}" {city}',
    ]
    best_url: Optional[str] = None
    best_score = 0
    found_social = False
    found_directory = False
    gl = _country_google_code(city)

    for query in queries:
        log.info("Secondary SerpAPI search for missing/uncertain website: '%s'", query)
        results = None
        for key in keys:
            try:
                client = serpapi.Client(api_key=key)
                search_kwargs = {"engine": "google", "q": query, "num": 10, "hl": "en"}
                if gl:
                    search_kwargs["gl"] = gl
                results = client.search(**search_kwargs)
                if isinstance(results, dict) and results.get("error"):
                    continue
                break
            except Exception as exc:
                log.warning("Secondary SerpAPI search failed with current key: %s", exc)
                continue

        organic_results = results.get("organic_results", []) if isinstance(results, dict) else []
        for res in organic_results:
            link = res.get("link")
            if not link:
                continue
            domain_type = classify_url_domain(link)
            if domain_type == STATUS_SOCIAL_ONLY:
                found_social = True
                continue
            if domain_type == STATUS_DIRECTORY_ONLY:
                found_directory = True
                continue

            score = _candidate_website_score(business_name, city, res, link)
            if score < 55:
                log.debug("Rejected weak website candidate %s (score=%d) for %s", link, score, business_name)
                continue

            status, profile = check_url_with_httpx(link, business_name)
            if status == STATUS_VALID_WEBSITE and profile.get("status_code") in (200, 301, 302, 307, 308):
                if score > best_score:
                    best_url = profile.get("final_url") or link
                    best_score = score

        if best_score >= 85:
            break

    if best_url:
        return best_url, None
    if found_social and not found_directory:
        return None, STATUS_SOCIAL_ONLY
    if found_directory and not found_social:
        return None, STATUS_DIRECTORY_ONLY
    return None, STATUS_NO_WEBSITE


def verify_lead_website(
    lead: Lead,
    api_key: Optional[str] = None,
) -> Tuple[str, Optional[str], Dict[str, Any]]:
    """Verify website for a single lead.

    Guarantees that an existing claimed/discovered website is NEVER discarded
    or set to NO_WEBSITE.

    Returns:
        (website_status, verified_url, site_profile)
    """
    url = lead.website

    if url and str(url).strip():
        clean_u = str(url).strip()
        # 1. Check if URL is social media or directory
        dom_type = classify_url_domain(clean_u)
        if dom_type == STATUS_SOCIAL_ONLY:
            return STATUS_SOCIAL_ONLY, clean_u, {"url": clean_u, "note": "Social media profile URL"}
        elif dom_type == STATUS_DIRECTORY_ONLY:
            return STATUS_DIRECTORY_ONLY, clean_u, {"url": clean_u, "note": "Directory listing URL"}

        # 2. Check HTTP status and SEO audit
        status, profile = check_url_with_httpx(clean_u, lead.name)
        verified_url = profile.get("final_url") or clean_u

        if status in (STATUS_VALID_WEBSITE, STATUS_DOMAIN_ONLY):
            return status, verified_url, profile

        # If HTTP check returned BROKEN_WEBSITE or UNKNOWN, try secondary Google Search fallback
        found_url, category_type = search_official_website_via_serpapi(
            business_name=lead.name,
            city=lead.city,
            api_key=api_key,
        )
        if found_url:
            s_status, s_profile = check_url_with_httpx(found_url, lead.name)
            if s_status == STATUS_VALID_WEBSITE:
                return s_status, s_profile.get("final_url") or found_url, s_profile

        # CRITICAL PROTECTION: The lead WAS discovered with a real website URL.
        # Preserve the URL as VALID_WEBSITE or BROKEN_WEBSITE with audit details. NEVER set to NO_WEBSITE!
        if status == STATUS_BROKEN_WEBSITE:
            return STATUS_BROKEN_WEBSITE, verified_url, profile

        return STATUS_VALID_WEBSITE, verified_url, profile

    # Only when lead has NO website URL at all do we perform secondary SerpAPI search
    found_url, category_type = search_official_website_via_serpapi(
        business_name=lead.name,
        city=lead.city,
        api_key=api_key,
    )

    if found_url:
        status, profile = check_url_with_httpx(found_url, lead.name)
        if status == STATUS_VALID_WEBSITE:
            return status, profile.get("final_url") or found_url, profile

    if category_type:
        return category_type, None, {"note": f"No official website validated; search classified as {category_type}"}
    return STATUS_NO_WEBSITE, None, {"note": "No official business website could be validated from discovery URL or Google search"}


def verify_leads_batch(
    limit: int = 5,
    db: Optional[Database] = None,
    config: Optional[Config] = None,
    city: Optional[str] = None,
    delay_s: float = 1.0,
) -> List[Dict[str, Any]]:
    """Verify up to `limit` leads sitting at DISCOVERED or ENRICHED status.

    Updates database record with website_status, site_profile_json, and
    transitions lead status to VERIFIED.
    """
    load_env_file(DEFAULT_ENV_PATH)
    if config is None:
        try:
            config = Config.load()
        except Exception:
            config = None

    if config:
        config.ensure_dirs()
        log_file = config.get("logging.file", "./data/logs/leadhunter.log")
        log_path = Path(log_file) if Path(log_file).is_absolute() else config.config_path.parent / log_file
    else:
        log_path = Path("./data/logs/leadhunter.log")

    setup_logging(
        level=config.get("logging.level", "INFO") if config else "INFO",
        log_file=log_path,
    )

    if db is None:
        data_dir = config.data_dir if config else os.path.join(os.getcwd(), "data")
        db_path = os.path.join(data_dir, "leadhunter.db")
        db = Database(db_path)

    api_key = get_serpapi_key(config)

    # Fetch eligible leads (DISCOVERED or ENRICHED)
    query = (
        "SELECT * FROM leads WHERE status IN ('DISCOVERED', 'ENRICHED') "
        "ORDER BY id ASC LIMIT ?"
    )
    if city:
        query = (
            f"SELECT * FROM leads WHERE status IN ('DISCOVERED', 'ENRICHED') "
            f"AND city = '{city}' ORDER BY id ASC LIMIT ?"
        )

    rows = db.conn.execute(query, (limit,)).fetchall()
    leads = [Lead.from_row(dict(r)) for r in rows]

    log.info("Starting website verification for %d leads (batch limit: %d)...", len(leads), limit)
    results: List[Dict[str, Any]] = []

    for idx, lead in enumerate(leads):
        if idx > 0 and delay_s > 0:
            time.sleep(delay_s)

        log.info(
            "Verifying website for Lead [ID %d]: '%s' | URL: %s",
            lead.id,
            lead.name,
            lead.website or "None",
        )

        site_status, verified_url, profile = verify_lead_website(lead, api_key=api_key)

        # Update Lead record in DB
        update_fields: Dict[str, Any] = {
            "website_verified": verified_url or lead.website_verified,
            "website_status": site_status,
            "site_profile_json": json.dumps(profile, default=str),
        }
        if profile.get("extracted_email"):
            update_fields["email"] = profile["extracted_email"]
            lead.email = profile["extracted_email"]

        # Transition status to VERIFIED
        from_status = lead.status.value
        db.update_lead(lead.id, update_fields)
        db.transition(
            lead_id=lead.id,
            to_status=LeadStatus.VERIFIED.value,
            stage="website_checker",
            event=f"Website verified as {site_status} (url: {verified_url or lead.website or 'None'})",
            level="INFO",
            extra_fields=update_fields,
        )

        lead.website_status = site_status
        lead.website_verified = verified_url
        lead.site_profile = profile
        lead.status = LeadStatus.VERIFIED

        log.info(
            "Lead [ID %d] '%s' -> website_status: %s [VERIFIED]",
            lead.id,
            lead.name,
            site_status,
        )

        results.append({
            "id": lead.id,
            "name": lead.name,
            "category": lead.category,
            "city": lead.city,
            "original_website": lead.website,
            "verified_website": verified_url,
            "website_status": site_status,
            "status": lead.status.value,
            "profile": profile,
        })

    return results


def main():
    import argparse

    parser = argparse.ArgumentParser(description="LeadHunter AI Website Verification")
    parser.add_argument("--city", default="Vadodara", help="City name filter")
    parser.add_argument("--limit", type=int, default=5, help="Number of leads to process")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay in seconds between checks")
    args = parser.parse_args()

    print(f"\n=== Running Website Verification (city='{args.city}', limit={args.limit}, delay={args.delay}s) ===")
    results = verify_leads_batch(limit=args.limit, city=args.city, delay_s=args.delay)

    print("\n============================================================")
    print("         WEBSITE VERIFICATION RESULTS                       ")
    print("============================================================")
    for r in results:
        print(f"ID {r['id']:2d} | {r['name']:<38} | Status: {r['website_status']:<16} | [{r['status']}]")
        print(f"      URL: {r['original_website'] or 'None'}")
        if r['verified_website']:
            print(f"      Verified: {r['verified_website']}")
        if r['profile'].get('title'):
            print(f"      Title: {r['profile']['title']}")
        if r['profile'].get('error'):
            print(f"      Error/Note: {r['profile']['error']}")


if __name__ == "__main__":
    main()
