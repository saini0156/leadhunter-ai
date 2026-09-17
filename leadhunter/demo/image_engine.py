"""
LeadHunter AI — Intelligent Image Engine

Selects illustrative imagery based on the actual business category.

Important:
- Images are illustrative website assets.
- They are NOT presented as verified client projects.
- No fake business results are generated.
"""

from __future__ import annotations

from typing import Any, Dict, List


IMAGE_LIBRARY: Dict[str, Dict[str, Any]] = {

    "roofing": {
        "hero": (
            "https://images.unsplash.com/photo-1632759145351-1d592919f522"
            "?auto=format&fit=crop&w=1600&q=85"
        ),
        "gallery": [
            (
                "https://images.unsplash.com/photo-1632759145351-1d592919f522"
                "?auto=format&fit=crop&w=1000&q=80"
            ),
            (
                "https://images.unsplash.com/photo-1621905252507-b35492cc74b4"
                "?auto=format&fit=crop&w=1000&q=80"
            ),
            (
                "https://images.unsplash.com/photo-1503387762-592deb58ef4e"
                "?auto=format&fit=crop&w=1000&q=80"
            ),
            (
                "https://images.unsplash.com/photo-1504307651254-35680f356dfd"
                "?auto=format&fit=crop&w=1000&q=80"
            ),
            (
                "https://images.unsplash.com/photo-1541888946425-d81bb19240f5"
                "?auto=format&fit=crop&w=1000&q=80"
            ),
        ],
        "visual_label": "Professional roofing and exterior construction",
        "alt": [
            "Professional roofing work",
            "Residential roof construction",
            "Roofing and exterior building work",
            "Professional construction project",
            "Exterior property improvement",
        ],
    },

    "plumbing": {
        "hero": (
            "https://images.unsplash.com/photo-1607472586893-edb57bdc0e39"
            "?auto=format&fit=crop&w=1600&q=85"
        ),
        "gallery": [
            (
                "https://images.unsplash.com/photo-1607472586893-edb57bdc0e39"
                "?auto=format&fit=crop&w=1000&q=80"
            ),
            (
                "https://images.unsplash.com/photo-1585704032915-c3400ca199e7"
                "?auto=format&fit=crop&w=1000&q=80"
            ),
            (
                "https://images.unsplash.com/photo-1504148455328-c376907d081c"
                "?auto=format&fit=crop&w=1000&q=80"
            ),
            (
                "https://images.unsplash.com/photo-1581244277943-fe4a9c777189"
                "?auto=format&fit=crop&w=1000&q=80"
            ),
        ],
        "visual_label": "Professional plumbing and home service work",
        "alt": [
            "Professional plumbing service",
            "Residential plumbing repair",
            "Plumbing tools and equipment",
            "Professional home service technician",
        ],
    },

    "cleaning": {
        "hero": (
            "https://images.unsplash.com/photo-1581578731548-c64695cc6952"
            "?auto=format&fit=crop&w=1600&q=85"
        ),
        "gallery": [
            (
                "https://images.unsplash.com/photo-1581578731548-c64695cc6952"
                "?auto=format&fit=crop&w=1000&q=80"
            ),
            (
                "https://images.unsplash.com/photo-1527515637462-cff94eecc1ac"
                "?auto=format&fit=crop&w=1000&q=80"
            ),
            (
                "https://images.unsplash.com/photo-1585421514738-01798e348b17"
                "?auto=format&fit=crop&w=1000&q=80"
            ),
            (
                "https://images.unsplash.com/photo-1558618666-fcd25c85cd64"
                "?auto=format&fit=crop&w=1000&q=80"
            ),
        ],
        "visual_label": "Professional cleaning and property care",
        "alt": [
            "Professional cleaning service",
            "Residential cleaning",
            "Professional cleaning equipment",
            "Detailed property cleaning",
        ],
    },

    "landscaping": {
        "hero": (
            "https://images.unsplash.com/photo-1558904541-efa843a96f01"
            "?auto=format&fit=crop&w=1600&q=85"
        ),
        "gallery": [
            (
                "https://images.unsplash.com/photo-1558904541-efa843a96f01"
                "?auto=format&fit=crop&w=1000&q=80"
            ),
            (
                "https://images.unsplash.com/photo-1585320806297-9794b3e4eeae"
                "?auto=format&fit=crop&w=1000&q=80"
            ),
            (
                "https://images.unsplash.com/photo-1598902108854-10e335adac99"
                "?auto=format&fit=crop&w=1000&q=80"
            ),
            (
                "https://images.unsplash.com/photo-1416879595882-3373a0480b5b"
                "?auto=format&fit=crop&w=1000&q=80"
            ),
        ],
        "visual_label": "Professional landscaping and outdoor spaces",
        "alt": [
            "Professional landscaping",
            "Residential garden landscaping",
            "Outdoor landscape design",
            "Garden maintenance",
        ],
    },

    "electrical": {
        "hero": (
            "https://images.unsplash.com/photo-1621905252507-b35492cc74b4"
            "?auto=format&fit=crop&w=1600&q=85"
        ),
        "gallery": [
            (
                "https://images.unsplash.com/photo-1621905252507-b35492cc74b4"
                "?auto=format&fit=crop&w=1000&q=80"
            ),
            (
                "https://images.unsplash.com/photo-1621905251918-48416bd8575a"
                "?auto=format&fit=crop&w=1000&q=80"
            ),
            (
                "https://images.unsplash.com/photo-1555963966-b7ae5406b6e5"
                "?auto=format&fit=crop&w=1000&q=80"
            ),
            (
                "https://images.unsplash.com/photo-1592833159155-c62df1b65634"
                "?auto=format&fit=crop&w=1000&q=80"
            ),
        ],
        "visual_label": "Professional electrical installation and service",
        "alt": [
            "Professional electrical service",
            "Electrical installation work",
            "Electrical technician working",
            "Modern electrical equipment",
        ],
    },

    "hvac": {
        "hero": (
            "https://images.unsplash.com/photo-1631545806609-5f3c5b1f4f56"
            "?auto=format&fit=crop&w=1600&q=85"
        ),
        "gallery": [
            (
                "https://images.unsplash.com/photo-1631545806609-5f3c5b1f4f56"
                "?auto=format&fit=crop&w=1000&q=80"
            ),
            (
                "https://images.unsplash.com/photo-1581094794329-c8112a89af12"
                "?auto=format&fit=crop&w=1000&q=80"
            ),
            (
                "https://images.unsplash.com/photo-1621905251189-08b45d6a269e"
                "?auto=format&fit=crop&w=1000&q=80"
            ),
        ],
        "visual_label": "Heating, cooling and indoor comfort services",
        "alt": [
            "HVAC service",
            "Professional HVAC technician",
            "Heating and cooling equipment",
        ],
    },

    "construction": {
        "hero": (
            "https://images.unsplash.com/photo-1503387762-592deb58ef4e"
            "?auto=format&fit=crop&w=1600&q=85"
        ),
        "gallery": [
            (
                "https://images.unsplash.com/photo-1503387762-592deb58ef4e"
                "?auto=format&fit=crop&w=1000&q=80"
            ),
            (
                "https://images.unsplash.com/photo-1504307651254-35680f356dfd"
                "?auto=format&fit=crop&w=1000&q=80"
            ),
            (
                "https://images.unsplash.com/photo-1541888946425-d81bb19240f5"
                "?auto=format&fit=crop&w=1000&q=80"
            ),
            (
                "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab"
                "?auto=format&fit=crop&w=1000&q=80"
            ),
        ],
        "visual_label": "Professional construction and building services",
        "alt": [
            "Construction project",
            "Professional building work",
            "Construction site",
            "Modern commercial building",
        ],
    },

    "real_estate": {
        "hero": (
            "https://images.unsplash.com/photo-1600585154340-be6161a56a0c"
            "?auto=format&fit=crop&w=1600&q=85"
        ),
        "gallery": [
            (
                "https://images.unsplash.com/photo-1600585154340-be6161a56a0c"
                "?auto=format&fit=crop&w=1000&q=80"
            ),
            (
                "https://images.unsplash.com/photo-1600607687920-4e2a09cf159d"
                "?auto=format&fit=crop&w=1000&q=80"
            ),
            (
                "https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3"
                "?auto=format&fit=crop&w=1000&q=80"
            ),
        ],
        "visual_label": "Modern property and real estate presentation",
        "alt": [
            "Modern residential property",
            "Luxury home exterior",
            "Modern property interior",
        ],
    },

    "auto": {
        "hero": (
            "https://images.unsplash.com/photo-1487754180451-c456f719a1fc"
            "?auto=format&fit=crop&w=1600&q=85"
        ),
        "gallery": [
            (
                "https://images.unsplash.com/photo-1487754180451-c456f719a1fc"
                "?auto=format&fit=crop&w=1000&q=80"
            ),
            (
                "https://images.unsplash.com/photo-1619642751034-765dfdf7c58e"
                "?auto=format&fit=crop&w=1000&q=80"
            ),
            (
                "https://images.unsplash.com/photo-1632823469850-1f77f3c6a495"
                "?auto=format&fit=crop&w=1000&q=80"
            ),
        ],
        "visual_label": "Professional automotive service and maintenance",
        "alt": [
            "Professional auto service",
            "Automotive workshop",
            "Vehicle maintenance",
        ],
    },

    "dental": {
        "hero": (
            "https://images.unsplash.com/photo-1606811971618-4486d14f3f99"
            "?auto=format&fit=crop&w=1600&q=85"
        ),
        "gallery": [
            (
                "https://images.unsplash.com/photo-1606811971618-4486d14f3f99"
                "?auto=format&fit=crop&w=1000&q=80"
            ),
            (
                "https://images.unsplash.com/photo-1588776814546-1ffcf47267a5"
                "?auto=format&fit=crop&w=1000&q=80"
            ),
            (
                "https://images.unsplash.com/photo-1550831107-1553da8c8464"
                "?auto=format&fit=crop&w=1000&q=80"
            ),
        ],
        "visual_label": "Modern dental care and patient experience",
        "alt": [
            "Modern dental clinic",
            "Dental consultation",
            "Professional dental care",
        ],
    },

    "legal": {
        "hero": (
            "https://images.unsplash.com/photo-1589829545856-d10d557cf95f"
            "?auto=format&fit=crop&w=1600&q=85"
        ),
        "gallery": [
            (
                "https://images.unsplash.com/photo-1589829545856-d10d557cf95f"
                "?auto=format&fit=crop&w=1000&q=80"
            ),
            (
                "https://images.unsplash.com/photo-1450101499163-c8848c66ca85"
                "?auto=format&fit=crop&w=1000&q=80"
            ),
            (
                "https://images.unsplash.com/photo-1505664194779-8beaceb93744"
                "?auto=format&fit=crop&w=1000&q=80"
            ),
        ],
        "visual_label": "Professional legal and advisory services",
        "alt": [
            "Professional legal consultation",
            "Legal documents and consultation",
            "Professional law office",
        ],
    },

    "business": {
        "hero": (
            "https://images.unsplash.com/photo-1497366216548-37526070297c"
            "?auto=format&fit=crop&w=1600&q=85"
        ),
        "gallery": [
            (
                "https://images.unsplash.com/photo-1497366216548-37526070297c"
                "?auto=format&fit=crop&w=1000&q=80"
            ),
            (
                "https://images.unsplash.com/photo-1497366811353-6870744d04b2"
                "?auto=format&fit=crop&w=1000&q=80"
            ),
            (
                "https://images.unsplash.com/photo-1524758631624-e2822e304c36"
                "?auto=format&fit=crop&w=1000&q=80"
            ),
        ],
        "visual_label": "Modern professional business environment",
        "alt": [
            "Modern professional office",
            "Business consultation",
            "Professional workspace",
        ],
    },
}


CATEGORY_KEYWORDS: Dict[str, List[str]] = {

    "roofing": [
        "roof",
        "roofing",
        "roofer",
        "shingle",
        "flat roof",
        "roof repair",
    ],

    "plumbing": [
        "plumb",
        "plumber",
        "plumbing",
        "drain",
        "water heater",
        "pipe",
    ],

    "cleaning": [
        "clean",
        "cleaning",
        "janitorial",
        "maid",
        "housekeeping",
    ],

    "landscaping": [
        "landscape",
        "landscaping",
        "lawn",
        "garden",
        "gardener",
        "tree service",
        "yard",
    ],

    "electrical": [
        "electric",
        "electrical",
        "electrician",
        "wiring",
        "lighting",
    ],

    "hvac": [
        "hvac",
        "heating",
        "cooling",
        "air conditioning",
        "air conditioner",
        "furnace",
    ],

    "construction": [
        "construction",
        "builder",
        "building",
        "contractor",
        "renovation",
        "remodel",
    ],

    "real_estate": [
        "real estate",
        "realtor",
        "property",
        "estate agent",
        "realty",
    ],

    "auto": [
        "auto",
        "automotive",
        "car",
        "vehicle",
        "mechanic",
        "garage",
        "motorcycle",
    ],

    "dental": [
        "dentist",
        "dental",
        "orthodont",
        "teeth",
        "oral",
    ],

    "legal": [
        "lawyer",
        "legal",
        "law firm",
        "attorney",
        "solicitor",
        "barrister",
    ],
}


def detect_image_category(
    category: str = "",
    business_name: str = "",
) -> str:

    text = f"{category} {business_name}".lower()

    ordered_categories = [
        "roofing",
        "plumbing",
        "cleaning",
        "landscaping",
        "electrical",
        "hvac",
        "construction",
        "real_estate",
        "dental",
        "legal",
        "auto",
    ]

    for image_category in ordered_categories:

        for keyword in CATEGORY_KEYWORDS.get(
            image_category,
            [],
        ):

            if keyword in text:
                return image_category

    return "business"


def _select_gallery(
    library: Dict[str, Any],
    profile: Dict[str, Any],
) -> List[Dict[str, str]]:

    gallery = library.get("gallery", [])
    alt_list = library.get("alt", [])

    services = profile.get("services")

    service_text = ""

    if isinstance(services, list):
        service_text = " ".join(
            str(item)
            for item in services
        ).lower()

    result = []

    # Slightly different ordering based on business/service signals.
    if "repair" in service_text:
        indexes = list(range(len(gallery)))
    elif "replacement" in service_text:
        indexes = list(reversed(range(len(gallery))))
    else:
        indexes = list(range(len(gallery)))

    for index in indexes:

        if index >= len(gallery):
            continue

        alt_text = (
            alt_list[index]
            if index < len(alt_list)
            else library.get(
                "visual_label",
                "Professional service",
            )
        )

        result.append({
            "url": gallery[index],
            "alt": alt_text,
        })

    return result[:5]


def build_image_profile(
    business_name: str = "",
    category: str = "",
    city: str = "",
    business_profile: Dict[str, Any] | None = None,
) -> Dict[str, Any]:

    profile = business_profile or {}

    # Prefer profile values if supplied.
    business_name = (
        str(
            profile.get(
                "business_name",
                business_name,
            )
        ).strip()
        or business_name
    )

    category = (
        str(
            profile.get(
                "category",
                category,
            )
        ).strip()
        or category
    )

    city = (
        str(
            profile.get(
                "city",
                city,
            )
        ).strip()
        or city
    )

    image_category = detect_image_category(
        category=category,
        business_name=business_name,
    )

    library = IMAGE_LIBRARY.get(
        image_category,
        IMAGE_LIBRARY["business"],
    )

    hero_alt = (
        library.get("alt", ["Professional service image"])[0]
    )

    gallery = _select_gallery(
        library,
        profile,
    )

    # Image role helps preview.html use the same assets
    # differently depending on the section.
    return {

        "category": image_category,

        "hero": {
            "url": library["hero"],
            "alt": hero_alt,
            "role": "hero",
        },

        "gallery": gallery,

        "visual_label": library.get(
            "visual_label",
            "Professional service",
        ),

        "city": city,

        "business_name": business_name,

        "is_client_project": False,

        "image_disclaimer": (
            "Illustrative imagery shown for website presentation. "
            "Replace with verified business photography when available."
        ),

        "usage": {
            "hero": "primary_service_visual",
            "services": "service_context",
            "gallery": "illustrative_gallery",
        },
    }