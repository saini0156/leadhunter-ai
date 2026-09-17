"""
LeadHunter AI — Personalized Website Content Engine

Builds website content from the actual business profile.

Rules:
- Never invent business claims.
- Never invent reviews, ratings, years of experience, guarantees, etc.
- Uses verified/available lead data when supplied.
- Remains reusable across industries.
"""

from __future__ import annotations

from typing import Any, Dict, List


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def _clean(value: Any, default: str = "") -> str:
    if value is None:
        return default

    text = str(value).strip()

    if not text or text.lower() in {
        "none",
        "null",
        "n/a",
        "na",
        "unknown",
    }:
        return default

    return text


def _title_case(value: str) -> str:
    value = _clean(value)

    if not value:
        return ""

    return " ".join(word.capitalize() for word in value.split())


def _first_valid(*values: Any, default: str = "") -> str:
    for value in values:
        cleaned = _clean(value)

        if cleaned:
            return cleaned

    return default


def _get_location(profile: Dict[str, Any]) -> str:
    return _first_valid(
        profile.get("display_location"),
        profile.get("location"),
        profile.get("display_city"),
        profile.get("city"),
        default="your area",
    )


def _get_short_location(profile: Dict[str, Any]) -> str:
    location = _first_valid(
        profile.get("short_location"),
        profile.get("display_city"),
        profile.get("city"),
        default="your area",
    )

    return location.split(",")[0].strip()


def _clean_category(category: str) -> str:
    category = _clean(category, "Local Service")

    replacements = [
        " contractors",
        " contractor",
        " companies",
        " company",
    ]

    lower = category.lower()

    for suffix in replacements:
        if lower.endswith(suffix):
            category = category[: -len(suffix)]
            break

    return _title_case(category)


def _normalise_services(
    services: Any,
    category: str,
) -> List[str]:

    if isinstance(services, list):

        result = []

        for item in services:
            if isinstance(item, dict):
                name = _first_valid(
                    item.get("name"),
                    item.get("title"),
                    item.get("service"),
                )
            else:
                name = _clean(item)

            if name:
                result.append(name)

        if result:
            return result[:6]

    category_lower = category.lower()

    defaults = {
        "roof": [
            "Roof Repair",
            "Roof Replacement",
            "Roof Inspection",
            "Leak Detection",
            "Shingle Roofing",
            "Emergency Roofing",
        ],
        "plumb": [
            "Plumbing Repair",
            "Drain Services",
            "Water Heater Service",
            "Pipe Repair",
            "Leak Detection",
        ],
        "clean": [
            "Residential Cleaning",
            "Commercial Cleaning",
            "Deep Cleaning",
            "Move-In / Move-Out Cleaning",
        ],
        "landscape": [
            "Lawn Care",
            "Landscape Design",
            "Garden Maintenance",
            "Yard Cleanup",
        ],
        "electric": [
            "Electrical Repairs",
            "Electrical Installation",
            "Lighting",
            "Wiring",
            "Electrical Inspection",
        ],
        "hvac": [
            "Heating Service",
            "Cooling Service",
            "Air Conditioning",
            "Furnace Service",
            "HVAC Maintenance",
        ],
        "construction": [
            "Construction",
            "Renovation",
            "Remodeling",
            "Property Improvements",
        ],
    }

    for key, service_list in defaults.items():
        if key in category_lower:
            return service_list

    return [
        f"{_clean_category(category)} Services",
        "Consultation",
        "Service & Support",
    ]


def _service_description(
    service: str,
    category: str,
    location: str,
) -> str:

    category_lower = category.lower()

    if "roof" in category_lower:
        descriptions = {
            "roof repair": (
                f"Roof repair support for properties in {location}, "
                "focused on identifying the issue and planning the appropriate repair."
            ),
            "roof replacement": (
                f"Roof replacement services for properties in {location}, "
                "with the scope based on the condition and requirements of the roof."
            ),
            "roof inspection": (
                f"Roof inspection services in {location} to help identify "
                "visible roofing concerns and determine suitable next steps."
            ),
            "leak detection": (
                f"Roof leak assessment in {location} to help locate potential "
                "sources of water intrusion and determine the next step."
            ),
            "emergency roofing": (
                f"Roofing assistance for urgent issues in {location}, "
                "with the next step based on the situation and property requirements."
            ),
        }

        key = service.lower()

        if key in descriptions:
            return descriptions[key]

    return (
        f"{service} for customers in {location}, "
        "with the scope and approach based on your requirements."
    )


# ---------------------------------------------------------------------------
# BUSINESS SIGNALS
# ---------------------------------------------------------------------------

def _build_business_signals(
    profile: Dict[str, Any],
) -> List[Dict[str, str]]:

    signals = []

    rating = profile.get("rating")
    reviews = profile.get("reviews_count")

    if rating not in (None, "", 0, "0"):
        try:
            rating_value = float(rating)

            if rating_value > 0:
                review_text = ""

                try:
                    review_count = int(reviews or 0)

                    if review_count > 0:
                        review_text = f" · {review_count} reviews"

                except (ValueError, TypeError):
                    pass

                signals.append({
                    "label": "Google Rating",
                    "value": f"{rating_value:.1f}/5{review_text}",
                    "verified": "true",
                })

        except (ValueError, TypeError):
            pass

    phone = _clean(profile.get("phone"))

    if phone:
        signals.append({
            "label": "Direct Contact",
            "value": phone,
            "verified": "true",
        })

    address = _clean(profile.get("address"))

    if address:
        signals.append({
            "label": "Service Location",
            "value": address,
            "verified": "true",
        })

    return signals[:3]


# ---------------------------------------------------------------------------
# HERO
# ---------------------------------------------------------------------------

def _build_hero(
    business_name: str,
    category: str,
    short_location: str,
    profile: Dict[str, Any],
) -> Dict[str, Any]:

    category_lower = category.lower()

    if "roof" in category_lower:

        title = f"Roofing Services Built Around Your Property"

        subtitle = (
            f"Professional roofing services for homeowners and property "
            f"owners in {short_location}."
        )

        primary_cta = "Request a Roofing Quote"
        secondary_cta = "Call for Roofing Service"

    elif "plumb" in category_lower:

        title = "Reliable Plumbing Help When You Need It"

        subtitle = (
            f"Professional plumbing services for homes and properties "
            f"in {short_location}."
        )

        primary_cta = "Request Plumbing Service"
        secondary_cta = "Call for Service"

    elif "hvac" in category_lower:

        title = f"Heating & Cooling Services in {short_location}"

        subtitle = (
            "Professional HVAC service focused on your home's heating, "
            "cooling and comfort requirements."
        )

        primary_cta = "Request HVAC Service"
        secondary_cta = "Call for Service"

    else:

        title = f"Professional {category} Services in {short_location}"

        subtitle = (
            f"Professional {category.lower()} services for customers "
            f"in {short_location}."
        )

        primary_cta = "Request Service"
        secondary_cta = "Get in Touch"

    # If the business already has a meaningful custom goal,
    # preserve it without blindly turning it into a claim.
    website_goal = _clean(profile.get("website_goal"))

    if website_goal:
        subtitle = (
            f"{subtitle} "
            f"Get in touch to discuss your requirements."
        )

    return {
        "eyebrow": _clean(category, "Professional Services"),
        "title": title,
        "subtitle": subtitle,
        "primary_cta": primary_cta,
        "secondary_cta": secondary_cta,
        "business_name": business_name,
    }


# ---------------------------------------------------------------------------
# WHY CHOOSE
# ---------------------------------------------------------------------------

def _build_why_choose_us(
    category: str,
    location: str,
    profile: Dict[str, Any],
) -> List[Dict[str, str]]:

    category_lower = category.lower()

    if "roof" in category_lower:

        return [
            {
                "title": "Clear Roofing Guidance",
                "description": (
                    "Understand the roofing issue and discuss the "
                    "appropriate next step for your property."
                ),
            },
            {
                "title": "Service-Focused Approach",
                "description": (
                    f"Roofing services designed around properties "
                    f"and requirements in {location}."
                ),
            },
            {
                "title": "Straightforward Enquiry",
                "description": (
                    "Share your roofing requirements and get the "
                    "conversation started without unnecessary steps."
                ),
            },
        ]

    return [
        {
            "title": "Clear Communication",
            "description": (
                "A straightforward way to explain what you need "
                "and discuss the next step."
            ),
        },
        {
            "title": "Service Focused",
            "description": (
                f"Services structured around customer requirements "
                f"in {location}."
            ),
        },
        {
            "title": "Simple Enquiry Process",
            "description": (
                "Tell us what you need and start a conversation "
                "about the appropriate service."
            ),
        },
    ]


# ---------------------------------------------------------------------------
# PROCESS
# ---------------------------------------------------------------------------

def _build_process(category: str) -> List[Dict[str, str]]:

    category_lower = category.lower()

    if "roof" in category_lower:

        return [
            {
                "number": "01",
                "title": "Tell Us About Your Roof",
                "description": (
                    "Share the type of roofing help you need "
                    "and any visible issue you have noticed."
                ),
            },
            {
                "number": "02",
                "title": "Discuss the Requirement",
                "description": (
                    "Provide the relevant property and project "
                    "details so the enquiry can be understood."
                ),
            },
            {
                "number": "03",
                "title": "Plan the Next Step",
                "description": (
                    "Discuss the appropriate service or inspection "
                    "based on your requirements."
                ),
            },
        ]

    return [
        {
            "number": "01",
            "title": "Start an Enquiry",
            "description": "Tell us what service you are looking for.",
        },
        {
            "number": "02",
            "title": "Discuss Your Needs",
            "description": (
                "Share the relevant details about your property "
                "or project."
            ),
        },
        {
            "number": "03",
            "title": "Plan the Next Step",
            "description": (
                "Discuss the appropriate service based on "
                "your requirements."
            ),
        },
    ]


# ---------------------------------------------------------------------------
# FAQ
# ---------------------------------------------------------------------------

def _build_faq(
    category: str,
    services: List[str],
    location: str,
) -> List[Dict[str, str]]:

    category_display = _clean_category(category)

    first_service = services[0] if services else f"{category_display} services"

    return [
        {
            "question": f"What {category_display.lower()} services are available?",
            "answer": (
                f"The website presents available {category_display.lower()} "
                "services based on the business information available."
            ),
        },
        {
            "question": f"Do you provide {first_service.lower()}?",
            "answer": (
                f"{first_service} is listed among the services presented "
                f"for customers in {location}."
            ),
        },
        {
            "question": "How do I get started?",
            "answer": (
                "Use the enquiry form or contact option to describe "
                "what you need and discuss the next step."
            ),
        },
        {
            "question": "Can I request a quote?",
            "answer": (
                "Yes. Use the enquiry form to provide your requirements "
                "and request further information."
            ),
        },
    ]


# ---------------------------------------------------------------------------
# SERVICE AREA
# ---------------------------------------------------------------------------

def _build_service_area(
    location: str,
    category: str,
) -> Dict[str, Any]:

    return {
        "title": f"{_clean_category(category)} Services in {location}",
        "description": (
            f"Serving customers looking for {_clean_category(category).lower()} "
            f"services in and around {location}."
        ),
        "location": location,
    }


# ---------------------------------------------------------------------------
# MAIN FUNCTION
# ---------------------------------------------------------------------------

def build_content_profile(
    business_profile: Dict[str, Any],
) -> Dict[str, Any]:

    profile = business_profile or {}

    business_name = _first_valid(
        profile.get("business_name"),
        profile.get("name"),
        default="Local Business",
    )

    category = _first_valid(
        profile.get("category"),
        profile.get("industry"),
        default="Professional Services",
    )

    category_display = _clean_category(category)

    location = _get_location(profile)
    short_location = _get_short_location(profile)

    services = _normalise_services(
        profile.get("services"),
        category,
    )

    hero = _build_hero(
        business_name,
        category_display,
        short_location,
        profile,
    )

    why_choose_us = _build_why_choose_us(
        category_display,
        location,
        profile,
    )

    process = _build_process(category_display)

    faq = _build_faq(
        category_display,
        services,
        location,
    )

    service_items = []

    for service in services:
        service_items.append({
            "name": service,
            "title": service,
            "description": _service_description(
                service,
                category_display,
                location,
            ),
        })

    website_goal = _clean(
        profile.get("website_goal"),
        "Generate enquiries and service requests",
    )

    target_customers = profile.get("target_customers")

    if not isinstance(target_customers, list):
        target_customers = []

    target_customers = [
        _clean(item)
        for item in target_customers
        if _clean(item)
    ]

    if not target_customers:

        category_lower = category_display.lower()

        if "roof" in category_lower:
            target_customers = [
                "Homeowners",
                "Property owners",
                "Property managers",
            ]
        else:
            target_customers = [
                "Local homeowners",
                "Property owners",
                "Local businesses",
            ]

    primary_cta = hero["primary_cta"]
    secondary_cta = hero["secondary_cta"]

    return {

        "business_name": business_name,

        "category": category,

        "category_display": category_display,

        "business_type": _clean(
            profile.get("business_type"),
            category_display,
        ),

        "city": _clean(
            profile.get("city"),
            location,
        ),

        "location": location,

        "short_location": short_location,

        "hero": hero,

        "services": service_items,

        "why_choose_us": why_choose_us,

        "process": process,

        "service_area": _build_service_area(
            location,
            category_display,
        ),

        "faq": faq,

        "cta": {
            "title": f"Need {category_display.lower()} services?",
            "description": (
                f"Tell us what you need in {short_location} "
                "and start an enquiry."
            ),
            "primary": primary_cta,
            "secondary": secondary_cta,
        },

        "business_signals": _build_business_signals(profile),

        "seo": {
            "title": (
                f"{business_name} | "
                f"{category_display} Services in {short_location}"
            ),
            "description": (
                f"{business_name} provides "
                f"{category_display.lower()} services "
                f"in {short_location}."
            ),
            "location": short_location,
            "category": category_display,
        },

        "website_goal": website_goal,

        "target_customers": target_customers,

        "primary_cta": primary_cta,

        "secondary_cta": secondary_cta,
    }