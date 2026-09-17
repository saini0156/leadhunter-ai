from typing import Dict, Any

def format_location(city: str) -> dict:
    """
    Convert raw location data into clean website display text.

    Examples:
        surrey, ca
        -> Surrey, BC
        -> Surrey, British Columbia, Canada

        Surrey
        -> Surrey
    """

    raw = (city or "").strip()

    if not raw:
        return {
            "display_city": "",
            "display_location": "",
            "short_location": "",
        }

    parts = [p.strip() for p in raw.split(",") if p.strip()]

    city_name = parts[0].title() if parts else ""

    # Common Canadian province/state abbreviations
    region_map = {
        "bc": "BC",
        "ab": "AB",
        "on": "ON",
        "qc": "QC",
        "mb": "MB",
        "sk": "SK",
        "ns": "NS",
        "nb": "NB",
        "nl": "NL",
        "pe": "PE",
        "ca": "BC",  # Many scraped Surrey records incorrectly use "ca"
    }

    region = ""
    country = ""

    if len(parts) >= 2:
        region_raw = parts[1].lower()

        if region_raw in region_map:
            region = region_map[region_raw]

    if len(parts) >= 3:
        country = parts[2].title()

    # Surrey + CA from our lead data should display as Surrey, BC
    if city_name.lower() == "surrey" and region.lower() == "bc":
        country = "Canada"

    if city_name.lower() == "surrey" and not region:
        region = "BC"
        country = "Canada"

    if region:
        display_city = f"{city_name}, {region}"
    else:
        display_city = city_name

    if country:
        display_location = f"{city_name}, {region}, {country}"
    else:
        display_location = display_city

    return {
        "display_city": display_city,
        "display_location": display_location,
        "short_location": city_name,
    }
def build_business_profile(
    business_name: str,
    category: str,
    city: str,
    address: str = "",
    phone: str = "",
    website: str = "",
    rating: float = 0,
    reviews: int = 0,
) -> Dict[str, Any]:
    """
    Build a structured business profile.

    This file decides WHAT the demo website should contain.
    The HTML/template decides HOW it looks.
    """

    category_text = (category or "").lower()
    location = format_location(city)

    # =====================================================
    # BASE PROFILE
    # =====================================================

    profile = {
        "business_name": business_name or "Local Business",
        "category": category or "Business",
        "city": city or "",
        "address": address or "",
        "phone": phone or "",
        "website": website or "",
        "rating": rating or 0,
        "reviews": reviews or 0,

        # Business intelligence
        "industry": "local_service",
        "business_type": "professional service",
        "target_customers": [],
        "services": [],

        # Website strategy
        "website_goal": "Generate more local enquiries",
        "primary_cta": "Get a Quote",

        # Design strategy
        "design_style": "clean_professional",
        "hero_style": "split",

        # Website structure
        "sections": [
            "hero",
            "services",
            "why_choose_us",
            "service_area",
            "contact",
        ],
    }

    # =====================================================
    # ROOFING
    # =====================================================

    if any(
        word in category_text
        for word in ["roof", "roofer", "roofing"]
    ):
        profile.update({
            "industry": "home_services",
            "business_type": "roofing company",

            "target_customers": [
                "homeowners",
                "property owners",
                "commercial property managers",
            ],

            "services": [
                "Roof Repair",
                "Roof Replacement",
                "Roof Inspection",
                "Emergency Roofing",
            ],

            "website_goal": (
                "Generate roofing enquiries "
                "and quote requests"
            ),

            "primary_cta": "Get a Free Roofing Quote",

            "design_style": "bold_construction",
            "hero_style": "visual_split",

            "sections": [
                "hero",
                "services",
                "why_choose_us",
                "roofing_process",
                "service_area",
                "project_gallery",
                "faq",
                "quote_form",
                "contact",
            ],
        })

    # =====================================================
    # PLUMBING
    # =====================================================

    elif any(
        word in category_text
        for word in ["plumb", "plumber"]
    ):
        profile.update({
            "industry": "home_services",
            "business_type": "plumbing company",

            "target_customers": [
                "homeowners",
                "landlords",
                "business owners",
            ],

            "services": [
                "Emergency Plumbing",
                "Leak Repair",
                "Drain Cleaning",
                "Water Heater Service",
            ],

            "website_goal": (
                "Generate calls and "
                "plumbing service enquiries"
            ),

            "primary_cta": "Call a Plumber",

            "design_style": "clean_professional",
            "hero_style": "service_split",

            "sections": [
                "hero",
                "emergency_cta",
                "services",
                "why_choose_us",
                "service_area",
                "faq",
                "quote_form",
                "contact",
            ],
        })

    # =====================================================
    # CLEANING
    # =====================================================

    elif any(
        word in category_text
        for word in ["clean", "cleaning", "janitorial"]
    ):
        profile.update({
            "industry": "home_services",
            "business_type": "cleaning company",

            "target_customers": [
                "homeowners",
                "offices",
                "property managers",
                "landlords",
            ],

            "services": [
                "Residential Cleaning",
                "Deep Cleaning",
                "Move-In / Move-Out Cleaning",
                "Commercial Cleaning",
            ],

            "website_goal": (
                "Generate cleaning "
                "service enquiries"
            ),

            "primary_cta": "Get a Cleaning Quote",

            "design_style": "modern_minimal",
            "hero_style": "clean_split",

            "sections": [
                "hero",
                "services",
                "how_it_works",
                "why_choose_us",
                "service_area",
                "faq",
                "quote_form",
                "contact",
            ],
        })

    # =====================================================
    # LANDSCAPING
    # =====================================================

    elif any(
        word in category_text
        for word in [
            "landscap",
            "lawn",
            "garden",
            "gardener",
            "tree service",
        ]
    ):
        profile.update({
            "industry": "home_services",
            "business_type": "landscaping company",

            "target_customers": [
                "homeowners",
                "property managers",
                "commercial property owners",
            ],

            "services": [
                "Lawn Care",
                "Garden Design",
                "Landscape Maintenance",
                "Tree & Hedge Services",
            ],

            "website_goal": (
                "Generate landscaping "
                "and lawn-care enquiries"
            ),

            "primary_cta": "Get a Landscaping Quote",

            "design_style": "natural_modern",
            "hero_style": "image_split",

            "sections": [
                "hero",
                "services",
                "project_gallery",
                "how_it_works",
                "why_choose_us",
                "service_area",
                "faq",
                "quote_form",
                "contact",
            ],
        })

    # =====================================================
    # ELECTRICIAN
    # =====================================================

    elif any(
        word in category_text
        for word in [
            "electric",
            "electrical",
            "electrician",
        ]
    ):
        profile.update({
            "industry": "home_services",
            "business_type": "electrical contractor",

            "target_customers": [
                "homeowners",
                "business owners",
                "property managers",
            ],

            "services": [
                "Electrical Repairs",
                "Lighting Installation",
                "Electrical Inspections",
                "Emergency Electrical Service",
            ],

            "website_goal": (
                "Generate electrical "
                "service calls and enquiries"
            ),

            "primary_cta": "Request Electrical Service",

            "design_style": "technical_modern",
            "hero_style": "bold_split",

            "sections": [
                "hero",
                "emergency_cta",
                "services",
                "why_choose_us",
                "service_area",
                "faq",
                "quote_form",
                "contact",
            ],
        })

    # =====================================================
    # HVAC
    # =====================================================

    elif any(
        word in category_text
        for word in [
            "hvac",
            "heating",
            "air conditioning",
            "air conditioner",
            "ac contractor",
        ]
    ):
        profile.update({
            "industry": "home_services",
            "business_type": "HVAC company",

            "target_customers": [
                "homeowners",
                "landlords",
                "commercial property owners",
            ],

            "services": [
                "AC Repair",
                "Heating Repair",
                "HVAC Installation",
                "HVAC Maintenance",
            ],

            "website_goal": (
                "Generate HVAC "
                "service calls and enquiries"
            ),

            "primary_cta": "Book HVAC Service",

            "design_style": "modern_comfort",
            "hero_style": "service_split",

            "sections": [
                "hero",
                "emergency_cta",
                "services",
                "why_choose_us",
                "service_area",
                "faq",
                "quote_form",
                "contact",
            ],
        })

    # =====================================================
    # CONSTRUCTION
    # =====================================================

    elif any(
        word in category_text
        for word in [
            "construction",
            "builder",
            "building contractor",
            "general contractor",
        ]
    ):
        profile.update({
            "industry": "construction",
            "business_type": "construction company",

            "target_customers": [
                "homeowners",
                "property developers",
                "commercial property owners",
            ],

            "services": [
                "New Construction",
                "Home Renovation",
                "Extensions & Additions",
                "Commercial Construction",
            ],

            "website_goal": (
                "Generate construction "
                "project enquiries"
            ),

            "primary_cta": "Discuss Your Project",

            "design_style": "premium_construction",
            "hero_style": "cinematic",

            "sections": [
                "hero",
                "services",
                "projects",
                "process",
                "why_choose_us",
                "service_area",
                "faq",
                "project_form",
                "contact",
            ],
        })

    # =====================================================
    # REAL ESTATE
    # =====================================================

    elif any(
        word in category_text
        for word in [
            "real estate",
            "realtor",
            "property",
            "estate agent",
        ]
    ):
        profile.update({
            "industry": "real_estate",
            "business_type": "real estate agency",

            "target_customers": [
                "home buyers",
                "home sellers",
                "property investors",
                "landlords",
            ],

            "services": [
                "Property Buying",
                "Property Selling",
                "Property Valuation",
                "Investment Guidance",
            ],

            "website_goal": (
                "Generate property "
                "buyer and seller enquiries"
            ),

            "primary_cta": "Explore Properties",

            "design_style": "premium_real_estate",
            "hero_style": "luxury_split",

            "sections": [
                "hero",
                "featured_properties",
                "services",
                "why_choose_us",
                "areas",
                "testimonials",
                "faq",
                "contact",
            ],
        })

    # =====================================================
    # AUTO / MECHANIC
    # =====================================================

    elif any(
        word in category_text
        for word in [
            "auto",
            "automotive",
            "mechanic",
            "car repair",
            "car service",
            "garage",
        ]
    ):
        profile.update({
            "industry": "automotive",
            "business_type": "auto repair shop",

            "target_customers": [
                "car owners",
                "vehicle owners",
                "local businesses with vehicles",
            ],

            "services": [
                "Car Diagnostics",
                "Brake Service",
                "Oil & Filter Service",
                "Vehicle Repairs",
            ],

            "website_goal": (
                "Generate vehicle "
                "service bookings"
            ),

            "primary_cta": "Book a Service",

            "design_style": "automotive_modern",
            "hero_style": "dark_split",

            "sections": [
                "hero",
                "services",
                "why_choose_us",
                "service_process",
                "faq",
                "booking",
                "contact",
            ],
        })

    # =====================================================
    # DENTAL
    # =====================================================

    elif any(
        word in category_text
        for word in [
            "dentist",
            "dental",
            "orthodont",
        ]
    ):
        profile.update({
            "industry": "healthcare",
            "business_type": "dental practice",

            "target_customers": [
                "families",
                "adults",
                "children",
                "local patients",
            ],

            "services": [
                "General Dentistry",
                "Teeth Cleaning",
                "Cosmetic Dentistry",
                "Emergency Dental Care",
            ],

            "website_goal": (
                "Generate patient "
                "enquiries and appointments"
            ),

            "primary_cta": "Book an Appointment",

            "design_style": "calm_healthcare",
            "hero_style": "clean_split",

            "sections": [
                "hero",
                "services",
                "why_choose_us",
                "patient_information",
                "faq",
                "appointment",
                "contact",
            ],
        })

    # =====================================================
    # LEGAL
    # =====================================================

    elif any(
        word in category_text
        for word in [
            "lawyer",
            "law firm",
            "attorney",
            "legal",
            "solicitor",
        ]
    ):
        profile.update({
            "industry": "professional_services",
            "business_type": "law firm",

            "target_customers": [
                "individual clients",
                "families",
                "business owners",
            ],

            "services": [
                "Legal Consultation",
                "Business Law",
                "Property Law",
                "Civil Matters",
            ],

            "website_goal": (
                "Generate qualified "
                "legal enquiries"
            ),

            "primary_cta": "Request a Consultation",

            "design_style": "premium_professional",
            "hero_style": "authority_split",

            "sections": [
                "hero",
                "practice_areas",
                "why_choose_us",
                "process",
                "faq",
                "consultation",
                "contact",
            ],
        })

    # =====================================================
    # FALLBACK
    # =====================================================

    else:
        profile.update({
            "industry": "local_business",
            "business_type": (
                category
                if category
                else "local business"
            ),

            "target_customers": [
                "local customers",
                "nearby businesses",
            ],

            "services": [
                "Professional Services",
                "Customer Support",
                "Local Services",
            ],

            "website_goal": (
                "Generate more local "
                "customers and enquiries"
            ),

            "primary_cta": "Contact Us",

            "design_style": "clean_professional",
            "hero_style": "split",

            "sections": [
                "hero",
                "services",
                "why_choose_us",
                "service_area",
                "faq",
                "contact",
            ],
        })

    # =====================================================
    # RETURN PROFILE
    # =====================================================
    profile.update({
        "display_city": location["display_city"],
        "display_location": location["display_location"],
        "short_location": location["short_location"],
    })

    return profile
    