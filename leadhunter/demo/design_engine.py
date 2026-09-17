"""
LeadHunter AI — Intelligent Design Engine

Converts business characteristics into a visual website system.

The engine intentionally separates:
    Business Profile = what the business is
    Design Profile   = how the website presents it
"""

from __future__ import annotations

from typing import Any, Dict


def _clean(value: Any, default: str = "") -> str:
    if value is None:
        return default

    value = str(value).strip()

    if not value or value.lower() in {
        "none",
        "null",
        "n/a",
        "na",
        "unknown",
    }:
        return default

    return value


def _number(value: Any, default: float = 0) -> float:
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def _detect_style(profile: Dict[str, Any]) -> str:

    explicit = _clean(profile.get("design_style"))

    if explicit:
        return explicit

    category = _clean(
        profile.get("category"),
        profile.get("industry"),
    ).lower()

    business_type = _clean(
        profile.get("business_type")
    ).lower()

    text = f"{category} {business_type}"

    if any(x in text for x in [
        "roof",
        "construction",
        "builder",
        "contractor",
    ]):
        return "bold_construction"

    if any(x in text for x in [
        "cleaning",
        "janitorial",
        "maid",
    ]):
        return "modern_minimal"

    if any(x in text for x in [
        "landscape",
        "lawn",
        "garden",
    ]):
        return "natural_modern"

    if any(x in text for x in [
        "electric",
        "electrician",
    ]):
        return "technical_modern"

    if any(x in text for x in [
        "hvac",
        "heating",
        "cooling",
    ]):
        return "modern_comfort"

    if any(x in text for x in [
        "real estate",
        "realtor",
        "property",
    ]):
        return "premium_real_estate"

    if any(x in text for x in [
        "dentist",
        "dental",
        "clinic",
    ]):
        return "calm_healthcare"

    if any(x in text for x in [
        "lawyer",
        "legal",
        "attorney",
    ]):
        return "premium_professional"

    if any(x in text for x in [
        "auto",
        "automotive",
        "mechanic",
    ]):
        return "automotive_modern"

    return "clean_professional"


def _base_design(style: str) -> Dict[str, Any]:

    design = {

        "style": style,

        "theme": "light",

        "primary_color": "#0F172A",

        "accent_color": "#2563EB",

        "background_color": "#F8FAFC",

        "text_color": "#0F172A",

        "muted_text_color": "#64748B",

        "border_radius": "14px",

        "button_style": "rounded",

        "card_style": "soft",

        "font_heading": "Inter",

        "font_body": "Inter",

        "hero_image_position": "right",

        "animation": "subtle",

        "section_spacing": "large",

        "hero_layout": "split",

        "service_layout": "service_cards",

        "section_layout": "balanced",

        "image_style": "rounded",

        "nav_style": "professional",

        "cta_style": "standard",

        "show_gallery": False,

        "show_process": True,

        "show_faq": True,

        # New composition controls.
        "hero_overlay": False,

        "hero_full_bleed": False,

        "hero_height": "normal",

        "show_trust_strip": True,

        "show_service_intro": True,

        "show_contact_card": True,

        "show_sticky_mobile_cta": True,

        "show_quote_panel": True,

        "show_business_signals": True,

        "card_hover": True,

        "section_dividers": False,

        "visual_density": "comfortable",

        "cta_position": "hero",

        "navigation_mode": "standard",
    }

    return design


def _apply_style(design: Dict[str, Any], style: str) -> None:

    styles = {

        "bold_construction": {
            "theme": "light",
            "primary_color": "#171717",
            "accent_color": "#F97316",
            "background_color": "#F5F5F4",
            "text_color": "#171717",
            "muted_text_color": "#57534E",
            "border_radius": "10px",
            "button_style": "strong",
            "card_style": "construction",
            "font_heading": "Montserrat",
            "font_body": "Inter",
            "hero_image_position": "right",
            "animation": "subtle",
            "section_spacing": "large",
            "hero_layout": "visual_split",
            "service_layout": "service_cards",
            "section_layout": "spacious",
            "image_style": "large_rounded",
            "nav_style": "strong",
            "cta_style": "high_contrast",
            "show_gallery": True,
            "hero_height": "large",
            "show_trust_strip": True,
            "show_quote_panel": True,
            "visual_density": "strong",
        },

        "clean_professional": {
            "theme": "light",
            "primary_color": "#0F172A",
            "accent_color": "#2563EB",
            "background_color": "#F8FAFC",
            "text_color": "#0F172A",
            "muted_text_color": "#64748B",
            "border_radius": "14px",
            "button_style": "rounded",
            "card_style": "soft",
            "font_heading": "Inter",
            "font_body": "Inter",
            "hero_layout": "split",
            "service_layout": "service_cards",
            "section_layout": "balanced",
            "image_style": "rounded",
            "nav_style": "professional",
        },

        "modern_minimal": {
            "theme": "light",
            "primary_color": "#18181B",
            "accent_color": "#10B981",
            "background_color": "#FAFAFA",
            "text_color": "#18181B",
            "muted_text_color": "#71717A",
            "border_radius": "20px",
            "button_style": "pill",
            "card_style": "minimal",
            "font_heading": "Plus Jakarta Sans",
            "font_body": "Inter",
            "hero_layout": "clean_split",
            "service_layout": "minimal_cards",
            "section_layout": "airy",
            "image_style": "soft",
            "nav_style": "minimal",
            "cta_style": "pill",
        },

        "natural_modern": {
            "theme": "light",
            "primary_color": "#1C1917",
            "accent_color": "#65A30D",
            "background_color": "#F7FEE7",
            "text_color": "#1C1917",
            "muted_text_color": "#57534E",
            "border_radius": "18px",
            "button_style": "rounded",
            "card_style": "organic",
            "font_heading": "DM Sans",
            "font_body": "Inter",
            "hero_layout": "image_split",
            "service_layout": "visual_cards",
            "section_layout": "organic",
            "image_style": "natural",
            "nav_style": "natural",
            "show_gallery": True,
        },

        "technical_modern": {
            "theme": "dark",
            "primary_color": "#F8FAFC",
            "accent_color": "#FACC15",
            "background_color": "#111827",
            "text_color": "#F8FAFC",
            "muted_text_color": "#CBD5E1",
            "border_radius": "10px",
            "button_style": "strong",
            "card_style": "technical",
            "font_heading": "Space Grotesk",
            "font_body": "Inter",
            "hero_layout": "bold_split",
            "service_layout": "technical_cards",
            "section_layout": "structured",
            "image_style": "sharp",
            "nav_style": "technical",
            "cta_style": "high_contrast",
        },

        "modern_comfort": {
            "theme": "light",
            "primary_color": "#0F172A",
            "accent_color": "#06B6D4",
            "background_color": "#F0FDFA",
            "text_color": "#0F172A",
            "muted_text_color": "#475569",
            "border_radius": "16px",
            "button_style": "rounded",
            "card_style": "soft",
            "font_heading": "Manrope",
            "font_body": "Inter",
            "hero_layout": "service_split",
            "service_layout": "service_cards",
            "section_layout": "comfortable",
            "image_style": "rounded",
            "nav_style": "professional",
        },

        "premium_construction": {
            "theme": "dark",
            "primary_color": "#F8FAFC",
            "accent_color": "#D4A017",
            "background_color": "#18181B",
            "text_color": "#F8FAFC",
            "muted_text_color": "#A1A1AA",
            "border_radius": "8px",
            "button_style": "sharp",
            "card_style": "premium",
            "font_heading": "Playfair Display",
            "font_body": "Inter",
            "hero_layout": "cinematic",
            "service_layout": "premium_cards",
            "section_layout": "editorial",
            "image_style": "cinematic",
            "nav_style": "luxury",
            "cta_style": "elegant",
            "show_gallery": True,
            "hero_full_bleed": True,
        },

        "premium_real_estate": {
            "theme": "light",
            "primary_color": "#1C1917",
            "accent_color": "#A16207",
            "background_color": "#FAFAF9",
            "text_color": "#1C1917",
            "muted_text_color": "#57534E",
            "border_radius": "4px",
            "button_style": "elegant",
            "card_style": "luxury",
            "font_heading": "Cormorant Garamond",
            "font_body": "Inter",
            "hero_layout": "luxury_split",
            "service_layout": "property_grid",
            "section_layout": "editorial",
            "image_style": "editorial",
            "nav_style": "premium",
            "cta_style": "elegant",
            "show_gallery": True,
            "show_process": False,
        },

        "automotive_modern": {
            "theme": "dark",
            "primary_color": "#F8FAFC",
            "accent_color": "#EF4444",
            "background_color": "#09090B",
            "text_color": "#F8FAFC",
            "muted_text_color": "#A1A1AA",
            "border_radius": "8px",
            "button_style": "strong",
            "card_style": "technical",
            "font_heading": "Oswald",
            "font_body": "Inter",
            "hero_layout": "dark_split",
            "service_layout": "technical_cards",
            "section_layout": "structured",
            "image_style": "sharp",
            "nav_style": "technical",
            "cta_style": "high_contrast",
            "show_gallery": True,
        },

        "calm_healthcare": {
            "theme": "light",
            "primary_color": "#164E63",
            "accent_color": "#0891B2",
            "background_color": "#F0FDFA",
            "text_color": "#164E63",
            "muted_text_color": "#64748B",
            "border_radius": "18px",
            "button_style": "rounded",
            "card_style": "soft",
            "font_heading": "Plus Jakarta Sans",
            "font_body": "Inter",
            "hero_layout": "clean_split",
            "service_layout": "health_cards",
            "section_layout": "calm",
            "image_style": "soft",
            "nav_style": "professional",
            "show_process": False,
        },

        "premium_professional": {
            "theme": "light",
            "primary_color": "#172033",
            "accent_color": "#B08D57",
            "background_color": "#F8F7F4",
            "text_color": "#172033",
            "muted_text_color": "#667085",
            "border_radius": "8px",
            "button_style": "elegant",
            "card_style": "premium",
            "font_heading": "DM Serif Display",
            "font_body": "Inter",
            "hero_layout": "authority_split",
            "service_layout": "practice_cards",
            "section_layout": "editorial",
            "image_style": "premium",
            "nav_style": "professional",
            "cta_style": "elegant",
        },
    }

    design.update(styles.get(style, styles["clean_professional"]))


def _apply_business_variation(
    design: Dict[str, Any],
    profile: Dict[str, Any],
) -> None:

    rating = _number(profile.get("rating"))
    reviews = _number(profile.get("reviews_count"))

    has_phone = bool(_clean(profile.get("phone")))
    has_address = bool(_clean(profile.get("address")))
    has_website = bool(_clean(profile.get("website")))

    # Stronger reputation data → expose trust strip.
    if rating > 0 or reviews > 0:
        design["show_trust_strip"] = True
        design["show_business_signals"] = True
    else:
        design["show_business_signals"] = False

    # Contact-rich lead → stronger contact conversion.
    if has_phone:
        design["show_contact_card"] = True
        design["show_sticky_mobile_cta"] = True

    # Address available → service-area/contact section gets more prominence.
    if has_address:
        design["show_contact_card"] = True

    # Businesses without a website are demo prospects,
    # so the CTA should be conversion-oriented.
    if not has_website:
        design["show_quote_panel"] = True
        design["cta_position"] = "hero_and_services"

    category = _clean(
        profile.get("category"),
        profile.get("industry"),
    ).lower()

    # Roofing-specific composition.
    if any(x in category for x in [
        "roof",
        "roofer",
    ]):

        design["show_quote_panel"] = True
        design["show_sticky_mobile_cta"] = True
        design["show_process"] = True
        design["show_faq"] = True

        # Rotate among roofing compositions based on lead signals.
        if reviews >= 100:
            design["hero_layout"] = "trust_split"
            design["cta_position"] = "hero_and_trust"
        elif rating >= 4.5:
            design["hero_layout"] = "reputation_split"
            design["cta_position"] = "hero_and_services"
        else:
            design["hero_layout"] = "visual_split"
            design["cta_position"] = "hero_and_quote"

    # Plumbing / emergency-service style.
    elif "plumb" in category:

        design["show_quote_panel"] = True
        design["show_sticky_mobile_cta"] = True
        design["cta_position"] = "hero_and_services"

    # Professional service businesses benefit from authority presentation.
    elif any(x in category for x in [
        "law",
        "legal",
        "attorney",
        "real estate",
    ]):

        design["show_quote_panel"] = False
        design["cta_position"] = "hero_and_contact"

    # Add visual variation even within the same industry.
    if reviews and reviews < 20:
        design["card_style"] = (
            "compact" if design["theme"] == "light"
            else "technical"
        )

    if reviews >= 100:
        design["section_spacing"] = "extra_large"


def build_design_profile(
    business_profile: Dict[str, Any]
) -> Dict[str, Any]:

    profile = business_profile or {}

    style = _detect_style(profile)

    design = _base_design(style)

    _apply_style(design, style)

    _apply_business_variation(
        design,
        profile,
    )

    # Preserve explicit profile overrides.
    explicit_hero_style = _clean(
        profile.get("hero_style")
    )

    if explicit_hero_style:
        design["hero_style"] = explicit_hero_style

    design["style"] = style

    return design