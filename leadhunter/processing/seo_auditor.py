"""Senior SEO Auditor Module for LeadHunter AI.

Performs technical SEO and web performance auditing on client websites:
- Measures Time-To-First-Byte (TTFB) and total page load duration (seconds)
- Classifies loading speed: FAST (<1.5s), MODERATE (1.5–3.0s), SLOW (3.0–5.0s), CRITICAL_SLOW (>5.0s)
- Audits <title>, <meta description>, <h1> headings, mobile viewport, SSL/HTTPS, OpenGraph, and Schema markup
- Computes a Senior SEO Health Score (0–100) and compiles structured issues and actionable recommendations
"""

from __future__ import annotations

import re
import time
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

_TITLE_REGEX = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)
_META_DESC_REGEX = re.compile(r'<meta\s+[^>]*name=["\']description["\'][^>]*content=["\'](.*?)["\']', re.IGNORECASE | re.DOTALL)
_META_DESC_ALT_REGEX = re.compile(r'<meta\s+[^>]*content=["\'](.*?)["\'][^>]*name=["\']description["\']', re.IGNORECASE | re.DOTALL)
_VIEWPORT_REGEX = re.compile(r'<meta\s+[^>]*name=["\']viewport["\']', re.IGNORECASE)
_H1_REGEX = re.compile(r"<h1[^>]*>(.*?)</h1>", re.IGNORECASE | re.DOTALL)
_OG_TITLE_REGEX = re.compile(r'<meta\s+[^>]*property=["\']og:title["\']', re.IGNORECASE)
_SCHEMA_JSON_REGEX = re.compile(r'<script\s+[^>]*type=["\']application/ld\+json["\']', re.IGNORECASE)
_NOINDEX_REGEX = re.compile(r'<meta\s+[^>]*name=["\']robots["\'][^>]*content=["\'][^"\']*noindex', re.IGNORECASE)
_CANONICAL_REGEX = re.compile(r'<link\s+[^>]*rel=["\']canonical["\'][^>]*href=["\'](.*?)["\']', re.IGNORECASE)
_IMG_TAGS = re.compile(r'<img\s+[^>]*>', re.IGNORECASE)
_HTML_TAGS = re.compile(r"<[^>]+>")
_WS = re.compile(r"\s+")


def clean_html_text(raw_html: str) -> str:
    """Clean HTML snippet to plain text."""
    if not raw_html:
        return ""
    text = _HTML_TAGS.sub(" ", raw_html)
    return _WS.sub(" ", text).strip()


def estimate_seo_financial_impact(
    load_time_sec: float,
    seo_health_score: int,
    critical_problems_count: int,
    issues_count: int,
) -> Dict[str, Any]:
    """Calculate estimated monthly revenue loss due to website performance and SEO deficits."""
    base_loss = 0
    # Speed conversion penalty
    if load_time_sec > 2.0:
        delay = load_time_sec - 2.0
        base_loss += int(delay * 350)
    
    # Health score deficit
    score_deficit = max(0, 100 - seo_health_score)
    base_loss += int(score_deficit * 25)

    # Critical & SEO issue penalty
    base_loss += (critical_problems_count * 500) + (issues_count * 150)

    est_min = max(450, (base_loss // 100) * 100)
    est_max = int(est_min * 2.2)
    drop_pct = round(min(65.0, max(5.0, (load_time_sec - 1.5) * 8.5 + score_deficit * 0.4)), 1)

    return {
        "estimated_lost_monthly_revenue_min": est_min,
        "estimated_lost_monthly_revenue_max": est_max,
        "formatted_loss_range": f"${est_min:,} – ${est_max:,} / month",
        "conversion_drop_percent": drop_pct,
    }


def audit_website_seo(
    url: str,
    html_content: str,
    response_time_sec: float,
    status_code: int = 200,
    headers: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """Perform a 4-tier Senior SEO Recruiter audit categorized by severity:
    - 🔴 Critical problems (down, 5xx, noindex, broken canonical, major mobile issues)
    - 🟠 SEO issues (missing title, meta desc, H1, canonical, schema, OpenGraph)
    - 🟡 SEO opportunities (long title, weak meta desc, missing alt text, thin content)
    - 🟢 Passed checks (HTTPS, valid viewport, good speed, proper title, proper H1)
    """
    critical_problems: List[str] = []   # 🔴
    seo_issues: List[str] = []          # 🟠
    seo_opportunities: List[str] = []   # 🟡
    passed_checks: List[str] = []       # 🟢
    recommendations: List[str] = []
    deductions = 0

    # 1. HTTP Status & Server Health Check (Critical 🔴)
    if status_code >= 500:
        deductions += 40
        critical_problems.append(f"Website server error (HTTP {status_code})")
        recommendations.append("Fix server 5xx errors and check host infrastructure.")
    elif status_code >= 400:
        deductions += 40
        critical_problems.append(f"Website unreachable or broken link (HTTP {status_code})")
        recommendations.append("Resolve 4xx URL routing and ensure homepage is publicly accessible.")
    elif status_code == 200:
        passed_checks.append("Server response status HTTP 200 OK")

    # 2. Speed & Latency Audit
    load_time = round(max(0.05, float(response_time_sec)), 2)
    if load_time < 1.5:
        speed_category = "FAST"
        speed_label = f"Fast ({load_time}s)"
        passed_checks.append(f"Good response time ({load_time}s)")
    elif load_time <= 3.0:
        speed_category = "MODERATE"
        speed_label = f"Moderate ({load_time}s)"
        passed_checks.append(f"Acceptable page load speed ({load_time}s)")
    elif load_time <= 5.0:
        speed_category = "SLOW"
        speed_label = f"Slow Page Speed ({load_time}s)"
        deductions += 15
        seo_issues.append(f"Slow page loading speed ({load_time}s — target is under 2.0s)")
        recommendations.append("Optimize site assets, compress images, and utilize caching to reduce load time under 2s.")
    else:
        speed_category = "CRITICAL_SLOW"
        speed_label = f"Critical Slowdown ({load_time}s)"
        deductions += 30
        critical_problems.append(f"Severe website slowdown ({load_time}s load time losing traffic)")
        recommendations.append("Critical page speed bottleneck: overhaul hosting, CDN, and script execution.")

    # 3. SSL / HTTPS Security Audit
    is_https = url.lower().startswith("https://")
    if not is_https:
        deductions += 15
        seo_issues.append("Website lacks SSL certificate (HTTP only)")
        recommendations.append("Install an SSL certificate to enable HTTPS security, essential for Google search rankings.")
    else:
        passed_checks.append("Correct HTTPS security enabled")

    # 4. Noindex Accidental Indexing Block (Critical 🔴)
    has_noindex = bool(_NOINDEX_REGEX.search(html_content))
    if has_noindex:
        deductions += 35
        critical_problems.append("Noindex tag accidentally enabled (<meta name='robots' content='noindex'> blocks Google indexing)")
        recommendations.append("Remove the 'noindex' robots meta tag immediately so Google can index the site.")
    else:
        passed_checks.append("Indexable by search engines (No noindex tag)")

    # 5. Mobile Viewport Audit
    has_viewport = bool(_VIEWPORT_REGEX.search(html_content))
    if not has_viewport:
        deductions += 25
        critical_problems.append("Missing Mobile Viewport meta tag (Major mobile responsiveness issue)")
        recommendations.append("Add <meta name='viewport' content='width=device-width, initial-scale=1.0'> for mobile responsiveness.")
    else:
        passed_checks.append("Valid mobile viewport configured")

    # 6. Title Tag Audit
    title_match = _TITLE_REGEX.search(html_content)
    title_text = clean_html_text(title_match.group(1)) if title_match else ""
    has_title = bool(title_text)
    title_len = len(title_text)

    if not has_title:
        deductions += 20
        seo_issues.append("Missing <title> tag on homepage")
        recommendations.append("Add a primary target keyword and location to the homepage title tag.")
    elif title_len < 20:
        deductions += 5
        seo_opportunities.append(f"Title tag is too short ({title_len} chars): '{title_text}'")
        recommendations.append("Expand title tag to 40-60 characters with core service keywords.")
    elif title_len > 70:
        deductions += 5
        seo_opportunities.append(f"Title tag exceeds recommended 60 characters ({title_len} chars)")
        recommendations.append("Shorten title tag to under 60 characters to prevent Google SERP truncation.")
    else:
        passed_checks.append(f"Proper Title tag length ({title_len} chars)")

    # 7. Meta Description Audit
    meta_desc_match = _META_DESC_REGEX.search(html_content) or _META_DESC_ALT_REGEX.search(html_content)
    meta_desc_text = clean_html_text(meta_desc_match.group(1)) if meta_desc_match else ""
    has_meta_desc = bool(meta_desc_text)
    meta_desc_len = len(meta_desc_text)

    if not has_meta_desc:
        deductions += 15
        seo_issues.append("Missing Meta Description tag")
        recommendations.append("Write a compelling 150-character meta description with a call-to-action to boost click-through rate.")
    elif meta_desc_len < 50:
        deductions += 5
        seo_opportunities.append(f"Weak/short meta description ({meta_desc_len} chars)")
        recommendations.append("Expand meta description to 120-160 characters for maximum search visibility.")
    else:
        passed_checks.append(f"Proper Meta Description tag ({meta_desc_len} chars)")

    # 8. Heading <h1> Tag Audit
    h1_matches = _H1_REGEX.findall(html_content)
    h1_count = len(h1_matches)
    h1_text = clean_html_text(h1_matches[0]) if h1_matches else ""
    has_h1 = h1_count > 0

    if not has_h1:
        deductions += 15
        seo_issues.append("Missing <h1> main heading tag")
        recommendations.append("Include one clear <h1> tag containing your primary service and city name.")
    elif h1_count > 2:
        deductions += 5
        seo_opportunities.append(f"Multiple <h1> tags detected ({h1_count} tags found)")
        recommendations.append("Use a single <h1> for the page title and <h2>/<h3> for subheadings.")
    else:
        passed_checks.append("Proper single <h1> heading tag")

    # 9. Canonical Tag Audit
    canonical_match = _CANONICAL_REGEX.search(html_content)
    has_canonical = bool(canonical_match)
    if not has_canonical:
        deductions += 5
        seo_issues.append("Missing Canonical link tag (<link rel='canonical'>)")
        recommendations.append("Add a self-referential canonical tag to prevent duplicate content issues.")
    else:
        passed_checks.append("Valid Canonical link tag present")

    # 10. Social OpenGraph & Schema Markup Audit
    has_og = bool(_OG_TITLE_REGEX.search(html_content))
    if not has_og:
        deductions += 5
        seo_issues.append("Missing OpenGraph social metadata")

    has_schema = bool(_SCHEMA_JSON_REGEX.search(html_content))
    if not has_schema:
        deductions += 5
        seo_issues.append("Missing Schema.org JSON-LD structured data")
        recommendations.append("Add LocalBusiness Schema markup to help Google Maps & search understand business hours and NAP.")
    else:
        passed_checks.append("LocalBusiness Schema.org markup detected")

    # 11. Image Alt Text & Thin Content Opportunities
    img_tags = _IMG_TAGS.findall(html_content)
    if img_tags:
        imgs_without_alt = [img for img in img_tags if 'alt=' not in img.lower() or 'alt=""' in img.lower() or "alt=''" in img.lower()]
        if imgs_without_alt:
            seo_opportunities.append(f"Missing alt text on {len(imgs_without_alt)} of {len(img_tags)} image(s)")
            recommendations.append("Add descriptive alt keywords to images to rank in Google Image Search.")

    plain_text = clean_html_text(html_content)
    word_count = len(plain_text.split())
    if word_count < 250:
        seo_opportunities.append(f"Thin homepage content ({word_count} words — recommended minimum 500+ words)")
        recommendations.append("Add detailed service descriptions, customer FAQs, and social proof to expand content depth.")

    # Calculate overall SEO health score
    raw_score = 100 - deductions
    seo_health_score = max(10, min(100, raw_score))

    # Combine all items for backward compatibility
    all_issues = critical_problems + seo_issues + seo_opportunities
    financial_impact = estimate_seo_financial_impact(
        load_time_sec=load_time,
        seo_health_score=seo_health_score,
        critical_problems_count=len(critical_problems),
        issues_count=len(seo_issues),
    )

    return {
        "url": url,
        "status_code": status_code,
        "load_time_sec": load_time,
        "speed_category": speed_category,
        "speed_label": speed_label,
        "seo_health_score": seo_health_score,
        "has_ssl": is_https,
        "has_title": has_title,
        "title": title_text,
        "title_length": title_len,
        "has_meta_description": has_meta_desc,
        "meta_description": meta_desc_text,
        "meta_description_length": meta_desc_len,
        "has_h1": has_h1,
        "h1_text": h1_text,
        "h1_count": h1_count,
        "has_mobile_viewport": has_viewport,
        "has_opengraph": has_og,
        "has_schema_markup": has_schema,
        "has_noindex": has_noindex,
        "has_canonical": has_canonical,
        "word_count": word_count,
        "critical_problems": critical_problems,   # 🔴
        "seo_issues": seo_issues,                 # 🟠
        "seo_opportunities": seo_opportunities,   # 🟡
        "passed_checks": passed_checks,           # 🟢
        "financial_impact": financial_impact,     # 💰 Financial Impact
        "issues_count": len(all_issues),
        "seo_issues": all_issues,
        "seo_recommendations": recommendations,
    }

