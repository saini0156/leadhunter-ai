"""Universal Niche & Layout Archetype Engine for LeadHunter AI.

Granular industry taxonomy ensuring:
- Cafes get artisan coffee, croissants, cheesecakes (NO tandoori/roti).
- Restaurants get authentic fine dining, sizzlers & curries.
- Dentists get invisible aligners, smile design & painless implants.
- Motorcycles get two-wheeler service, engine tuning & spares.
- Real estate gets luxury villas, apartments & site visits.
- Sports gets synthetic turfs, leagues & cricket academies.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional


NICHE_DEFINITIONS: Dict[str, Dict[str, Any]] = {
    # ☕ 1. CAFES, BAKERIES & COFFEE HOUSES
    "cafe": {
        "layout_style": "cinematic_center",
        "keywords": ["cafe", "coffee", "bakery", "bake", "espresso", "tea", "roaster", "croissant", "bistro", "pastry", "waffle", "crepe", "dessert", "brew", "cappuccino", "waycup"],
        "icon": "fa-mug-hot",
        "badge": "Artisan Specialty Cafe & Roastery",
        "theme": "amber",
        "accent_hex": "#d97706",
        "gradient": "from-amber-600 via-amber-700 to-stone-900",
        "glow": "bg-amber-600/20",
        "hero_title": "Handcrafted Artisan Coffee, Fresh Bakes & Warm Moments at {name}",
        "hero_desc": "Single-origin pour-over brews, freshly baked butter croissants, artisan sourdough melts, and decadent handcrafted desserts in {city}.",
        "hero_img": "https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?auto=format&fit=crop&w=1200&q=80",
        "cta_booking": "Reserve Cozy Table / Pre-Order",
        "cta_chat": "WhatsApp Cafe Barista",
        "service_title": "Signature Specialty Brews, Fresh Bakes & Desserts",
        "services": [
            {
                "title": "Artisan Pour-Over & Specialty Brews",
                "desc": "Single-origin Arabica beans, velvety flat whites, iced matcha, and 18-hour cold brew extractions.",
                "badge": "☕ Specialty Coffee",
                "img": "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?auto=format&fit=crop&w=600&q=80"
            },
            {
                "title": "Freshly Baked Butter Croissants & Melts",
                "desc": "Flaky golden French croissants, sourdough grilled paninis, and artisan gourmet breakfast toasts.",
                "badge": "🥐 Fresh from Oven",
                "img": "https://images.unsplash.com/photo-1555507036-ab1f4038808a?auto=format&fit=crop&w=600&q=80"
            },
            {
                "title": "Signature Cheesecakes & Handcrafted Desserts",
                "desc": "New York baked blueberry cheesecake, Belgian dark chocolate brownies, and layered tiramisu jars.",
                "badge": "🍰 Pastry Chef Special",
                "img": "https://images.unsplash.com/photo-1533134242443-d4fd215305ad?auto=format&fit=crop&w=600&q=80"
            }
        ],
        "booking_heading": "Reserve Your Cozy Table in Advance",
        "booking_field_label": "Seating Preference",
        "booking_options": ["Cozy Table for 2 (Coffee Date)", "Group Table for 4 (Friends)", "Work & Coffee Table (High-Speed Wi-Fi)", "Bakery Pre-Order Pickup"],
        "metric_1": "25,000+ Coffees Served",
        "metric_2": "100% Arabica Beans",
        "metric_label": "Coffee Lovers"
    },

    # 🦷 2. DENTAL CLINICS & SMILE DESIGNERS
    "dental": {
        "layout_style": "split_modern",
        "keywords": ["dentist", "dental", "orthodontist", "smile", "teeth", "invisalign", "implant", "braces", "cavity", "tooth"],
        "icon": "fa-tooth",
        "badge": "Advanced Smile & Dental Studio",
        "theme": "cyan",
        "accent_hex": "#06b6d4",
        "gradient": "from-cyan-600 via-teal-600 to-cyan-700",
        "glow": "bg-cyan-600/20",
        "hero_title": "Design Your Perfect, Radiant Smile with {name}",
        "hero_desc": "State-of-the-art painless dental implants, Invisalign clear aligners, laser teeth whitening, and compassionate family dentistry in {city}.",
        "hero_img": "https://images.unsplash.com/photo-1606811841689-23dfddce3e95?auto=format&fit=crop&w=1200&q=80",
        "cta_booking": "Book Dental Consultation",
        "cta_chat": "WhatsApp Clinic",
        "service_title": "Advanced Painless Dental & Aesthetic Treatments",
        "services": [
            {
                "title": "Invisalign & Clear Aligners",
                "desc": "Discreet, removable custom clear aligners for perfect teeth straightening without metal braces.",
                "badge": "✨ Smile Design",
                "img": "https://images.unsplash.com/photo-1588776814546-1ffcf47267a5?auto=format&fit=crop&w=600&q=80"
            },
            {
                "title": "Single-Sitting Laser Root Canal & Crowns",
                "desc": "High-precision painless microscopic endodontics and computerized zirconia ceramic crowns.",
                "badge": "🦷 Painless Tech",
                "img": "https://images.unsplash.com/photo-1629909613654-28e377c37b09?auto=format&fit=crop&w=600&q=80"
            },
            {
                "title": "Laser Teeth Whitening & Cosmetic Veneers",
                "desc": "Instant shade brightening and ultra-thin porcelain veneers for Hollywood-grade smile transformations.",
                "badge": "⭐ 1-Hour Brightening",
                "img": "https://images.unsplash.com/photo-1579684385127-1ef15d508118?auto=format&fit=crop&w=600&q=80"
            }
        ],
        "booking_heading": "Schedule Your Dental Checkup / Smile Consult",
        "booking_field_label": "Treatment Required",
        "booking_options": ["General Dental Checkup & Cleaning", "Invisalign / Braces Consultation", "Painless Root Canal / Implant", "Cosmetic Smile Whitening"],
        "metric_1": "10,000+ Smiles Designed",
        "metric_2": "100% Sterile Tech",
        "metric_label": "Happy Patients"
    },

    # 🏍️ 3. MOTORCYCLES & TWO-WHEELER REPAIR / SHOPS
    "motorcycle": {
        "layout_style": "split_modern",
        "keywords": ["motorcycle", "bike", "two wheeler", "scooter", "royal enfield", "yamaha", "honda 2 wheeler", "hero", "bajaj", "superbike", "bullet"],
        "icon": "fa-motorcycle",
        "badge": "Two-Wheeler & Superbike Specialist",
        "theme": "orange",
        "accent_hex": "#ea580c",
        "gradient": "from-orange-600 via-zinc-800 to-stone-900",
        "glow": "bg-orange-600/20",
        "hero_title": "Master Two-Wheeler Tuning & Precision Bike Service at {name}",
        "hero_desc": "Certified technicians, computerized carburetor/FI scanning, genuine OEM bike spares, and performance tuning in {city}.",
        "hero_img": "https://images.unsplash.com/photo-1558981403-c5f9899a28bc?auto=format&fit=crop&w=1200&q=80",
        "cta_booking": "Book Bike Service Slot",
        "cta_chat": "WhatsApp Workshop",
        "service_title": "Comprehensive Two-Wheeler Care & Performance Upgrades",
        "services": [
            {
                "title": "Periodic Service & Computerized FI Tuning",
                "desc": "Complete 35-point safety check, synthetic engine oil flush, spark plug replacement, and throttle body clean.",
                "badge": "🏍️ Full Service",
                "img": "https://images.unsplash.com/photo-1568772585407-9361f9bf3a87?auto=format&fit=crop&w=600&q=80"
            },
            {
                "title": "Brake Overhaul & Suspension Tuning",
                "desc": "Disc brake bleeding, high-performance brake pads, fork oil overhaul, and rear monoshock adjustments.",
                "badge": "⚙️ Precision Tech",
                "img": "https://images.unsplash.com/photo-1486006920555-c77dce18193b?auto=format&fit=crop&w=600&q=80"
            },
            {
                "title": "Genuine Spares, Chain & Tyre Replacement",
                "desc": "O-ring chain lubrication, tubeless radial tyre fitting with dynamic balancing, and genuine OEM parts.",
                "badge": "🛡️ 100% Genuine OEM",
                "img": "https://images.unsplash.com/photo-1601362840469-51e4d8d58785?auto=format&fit=crop&w=600&q=80"
            }
        ],
        "booking_heading": "Schedule Your Two-Wheeler Service",
        "booking_field_label": "Service Type",
        "booking_options": ["Standard Periodic Maintenance", "Engine & Electrical Troubleshooting", "Brake / Suspension Overhaul", "General Checkup & Quote"],
        "metric_1": "12,000+ Bikes Serviced",
        "metric_2": "100% Genuine Spares",
        "metric_label": "Satisfied Riders"
    },

    # 🏆 4. SPORTS & TURFS
    "sports": {
        "layout_style": "cinematic_center",
        "keywords": ["sport", "turf", "cricket", "football", "badminton", "academy", "tennis", "swimming", "skating", "martial arts", "box cricket", "futsal", "athletic"],
        "icon": "fa-trophy",
        "badge": "Premier Sports Arena",
        "theme": "amber",
        "accent_hex": "#f59e0b",
        "gradient": "from-amber-500 via-orange-600 to-amber-600",
        "glow": "bg-amber-500/20",
        "hero_title": "Elevate Your Game & Master Your Skills at {name}",
        "hero_desc": "World-class synthetic turfs, certified coaching academies, competitive leagues, and floodlit night matches right in {city}.",
        "hero_img": "https://images.unsplash.com/photo-1574629810360-7efbbe195018?auto=format&fit=crop&w=1200&q=80",
        "cta_booking": "Book Turf / Free Trial Slot",
        "cta_chat": "WhatsApp Arena Desk",
        "service_title": "World-Class Sports Arenas & Training Academies",
        "services": [
            {
                "title": "Pro Synthetic Turf & Arena Booking",
                "desc": "FIFA & ICC standard shock-absorbent synthetic turf with high-lumen floodlights for box cricket and football.",
                "badge": "🏆 Match Ready",
                "img": "https://images.unsplash.com/photo-1529900245534-47fbfb57835a?auto=format&fit=crop&w=600&q=80"
            },
            {
                "title": "Youth & Pro Coaching Academy",
                "desc": "Certified NIS master coaches delivering tactical drills, agility conditioning, and competitive tournament prep.",
                "badge": "⭐ Certified Mentors",
                "img": "https://images.unsplash.com/photo-1517649763962-0c623266ddc0?auto=format&fit=crop&w=600&q=80"
            },
            {
                "title": "Corporate Leagues & Tournaments",
                "desc": "End-to-end tournament management with digital scoring, spectator seating, custom trophies, and refreshments.",
                "badge": "⚡ Tournaments",
                "img": "https://images.unsplash.com/photo-1511886929837-354d827aae26?auto=format&fit=crop&w=600&q=80"
            }
        ],
        "booking_heading": "Book Your Turf Slot or Academy Trial",
        "booking_field_label": "Select Sport / Turf Type",
        "booking_options": ["Box Cricket Turf (60 Mins)", "Football / Futsal Turf (60 Mins)", "Academy Free Trial Session", "Corporate Tournament Booking"],
        "metric_1": "5,000+ Matches",
        "metric_2": "100% Pro Turf",
        "metric_label": "Athletes & Players"
    },

    # 🏋️ 5. GYMS & FITNESS
    "fitness": {
        "layout_style": "cinematic_center",
        "keywords": ["gym", "fitness", "workout", "crossfit", "yoga", "bodybuilding", "trainer", "pilates", "aerobics", "zumba"],
        "icon": "fa-dumbbell",
        "badge": "Elite Training Facility",
        "theme": "red",
        "accent_hex": "#ef4444",
        "gradient": "from-red-600 via-orange-600 to-red-600",
        "glow": "bg-red-600/20",
        "hero_title": "Transform Your Physique & Build Unstoppable Strength at {name}",
        "hero_desc": "State-of-the-art imported biomechanics equipment, certified elite trainers, and custom macro nutrition in {city}.",
        "hero_img": "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?auto=format&fit=crop&w=1200&q=80",
        "cta_booking": "Claim Free 1-Day VIP Pass",
        "cta_chat": "WhatsApp Trainer",
        "service_title": "Results-Driven Fitness Programs & Memberships",
        "services": [
            {
                "title": "Hypertrophy & Heavy Iron Zone",
                "desc": "Olympic power racks, calibrated plates, and ergonomic pin-loaded resistance machinery.",
                "badge": "💪 Heavy Iron",
                "img": "https://images.unsplash.com/photo-1581009146145-b5ef050c2e1e?auto=format&fit=crop&w=600&q=80"
            },
            {
                "title": "HIIT, Crossfit & Functional Cardio",
                "desc": "Curved motorless treadmills, assault bikes, rowing machines, and agility zones to melt body fat.",
                "badge": "🔥 Fat Shred",
                "img": "https://images.unsplash.com/photo-1518611012118-696072aa579a?auto=format&fit=crop&w=600&q=80"
            },
            {
                "title": "1-on-1 Personal Training & Custom Diet",
                "desc": "InBody body composition scans, customized macro-based diet plans, and weekly accountability.",
                "badge": "🥗 Nutrition & PT",
                "img": "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?auto=format&fit=crop&w=600&q=80"
            }
        ],
        "booking_heading": "Claim Your Free 1-Day VIP Workout Pass",
        "booking_field_label": "Primary Fitness Goal",
        "booking_options": ["Muscle Building & Strength", "Fat Loss & Conditioning", "Personal Training Consultation", "General Fitness Pass"],
        "metric_1": "100+ Pro Machines",
        "metric_2": "100% Certified PTs",
        "metric_label": "Active Members"
    },

    # 🍽️ 6. RESTAURANTS & TRADITIONAL DINING (Sizzlers, Curries, Dhabas)
    "dining": {
        "layout_style": "cinematic_center",
        "keywords": ["restaurant", "dining", "dhaba", "kitchen", "biryani", "tandoori", "thali", "curry", "food", "lounge", "bar", "pub"],
        "icon": "fa-utensils",
        "badge": "Artisanal Gourmet Dining",
        "theme": "orange",
        "accent_hex": "#f97316",
        "gradient": "from-orange-600 via-amber-500 to-orange-600",
        "glow": "bg-orange-600/20",
        "hero_title": "Taste Authentic Handcrafted Flavors & Delicacies at {name}",
        "hero_desc": "Handcrafted gourmet dining prepared with authentic recipes, farm-fresh local ingredients, and world-class hospitality in {city}.",
        "hero_img": "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&w=1200&q=80",
        "cta_booking": "Reserve Your Dining Table",
        "cta_chat": "WhatsApp Quick Order",
        "service_title": "Signature Dishes & Culinary Specialties",
        "services": [
            {
                "title": "Tandoori Sizzler Platter",
                "desc": "Charcoal grilled delicacies infused with aromatic smoked spices, bell peppers & mint chutney.",
                "badge": "🔥 Bestseller",
                "img": "https://images.unsplash.com/photo-1546833999-b9f581a1996d?auto=format&fit=crop&w=600&q=80"
            },
            {
                "title": "Slow-Cooked Royal Dal",
                "desc": "Simmered over slow flame for 14 hours with pure butter, cream & whole ground spices.",
                "badge": "⭐ Chef Special",
                "img": "https://images.unsplash.com/photo-1585937421612-70a008356fbe?auto=format&fit=crop&w=600&q=80"
            },
            {
                "title": "Signature Botanical Mocktails",
                "desc": "Crushed berries, fresh garden mint, zesty lime and sparkling botanical soda.",
                "badge": "🍹 Refreshing",
                "img": "https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?auto=format&fit=crop&w=600&q=80"
            }
        ],
        "booking_heading": "Reserve Your Table in Advance",
        "booking_field_label": "Guest Party Size",
        "booking_options": ["2 Guests (Couple)", "4 Guests (Family)", "6 Guests (Celebration)", "8+ Guests (Party)"],
        "metric_1": "50,000+ Meals",
        "metric_2": "100% Fresh Food",
        "metric_label": "Happy Foodies"
    },

    # 💇 7. BEAUTY, SALONS & SPAS
    "beauty": {
        "layout_style": "bento_luxury",
        "keywords": ["salon", "spa", "beauty", "hair", "makeup", "parlour", "skin", "nails", "massage", "bridal"],
        "icon": "fa-wand-magic-sparkles",
        "badge": "Couture Beauty & Spa",
        "theme": "pink",
        "accent_hex": "#ec4899",
        "gradient": "from-pink-600 via-rose-500 to-pink-600",
        "glow": "bg-pink-600/20",
        "hero_title": "Experience Luxury Hair, Skin & Bridal Aesthetics at {name}",
        "hero_desc": "Transformative couture hair styling, organic revitalizing spa rituals, advanced skincare, and bespoke bridal makeovers in {city}.",
        "hero_img": "https://images.unsplash.com/photo-1560066984-138dadb4c035?auto=format&fit=crop&w=1000&q=80",
        "cta_booking": "Book Salon Appointment",
        "cta_chat": "WhatsApp Stylist",
        "service_title": "Signature Salon & Rejuvenating Spa Treatments",
        "services": [
            {
                "title": "Couture Hair Styling & Keratin Care",
                "desc": "Precision haircuts, global highlights, botox hair therapy, and luxury nourishing hair spa rituals.",
                "badge": "✂️ Hair Studio",
                "img": "https://images.unsplash.com/photo-1562322140-8baeececf3df?auto=format&fit=crop&w=600&q=80"
            },
            {
                "title": "Advanced Skin Treatments & Facials",
                "desc": "Hydra-facials, organic peels, anti-aging therapies, and deep pore cleansing by expert aestheticians.",
                "badge": "✨ Glow Care",
                "img": "https://images.unsplash.com/photo-1570172619644-dfd03ed5d881?auto=format&fit=crop&w=600&q=80"
            },
            {
                "title": "HD Bridal & Event Makeovers",
                "desc": "Long-lasting Airbrush & HD makeup, pre-bridal packages, saree draping, and flawless event glam.",
                "badge": "💄 Bridal Glam",
                "img": "https://images.unsplash.com/photo-1487412720507-e7ab37603c6f?auto=format&fit=crop&w=600&q=80"
            }
        ],
        "booking_heading": "Reserve Your Appointment with Master Stylists",
        "booking_field_label": "Service Desired",
        "booking_options": ["Haircut & Styling Session", "Luxury Facial / Skincare", "Bridal / Party Makeup", "Full Spa Rejuvenation"],
        "metric_1": "15,000+ Makeovers",
        "metric_2": "100% Organic Care",
        "metric_label": "Happy Clients"
    },

    # 🏢 8. REAL ESTATE & BUILDERS
    "realestate": {
        "layout_style": "split_modern",
        "keywords": ["real estate", "realestate", "estate", "property", "properties", "builder", "ghar", "realtor", "plot", "housing", "apartment", "villa", "flats", "construction", "developer"],
        "icon": "fa-house-chimney",
        "badge": "Verified Property Consultant",
        "theme": "emerald",
        "accent_hex": "#10b981",
        "gradient": "from-emerald-600 via-teal-600 to-emerald-600",
        "glow": "bg-emerald-600/20",
        "hero_title": "Find Your Dream Home & High-ROI Properties with {name}",
        "hero_desc": "Explore verified luxury apartments, commercial SCO plots, gated society villas, and high-growth investment land across {city} with 100% legal transparency.",
        "hero_img": "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&w=1000&q=80",
        "cta_booking": "Schedule Free Site Visit",
        "cta_chat": "WhatsApp Property Desk",
        "service_title": "Explore Verified Properties & Investment Projects",
        "services": [
            {
                "title": "Luxury 3 & 4 BHK Apartments",
                "desc": "Gated society with clubhouse, swimming pool, 100% power backup, and modern smart home automation.",
                "badge": "🏢 Residential",
                "img": "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?auto=format&fit=crop&w=600&q=80"
            },
            {
                "title": "Gated Society Villas & Plots",
                "desc": "Freehold residential plots and architect-designed independent luxury villas with immediate registry.",
                "badge": "🏡 Independent",
                "img": "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=600&q=80"
            },
            {
                "title": "Commercial SCO & Retail Hubs",
                "desc": "High-visibility retail shops, corporate offices, and investment properties guaranteed with strong rental yields.",
                "badge": "🏬 Commercial",
                "img": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=600&q=80"
            }
        ],
        "booking_heading": "Schedule Your VIP Site Visit",
        "booking_field_label": "Property Type Desired",
        "booking_options": ["Residential Apartment (3/4 BHK)", "Independent Villa / Gated Plot", "Commercial SCO / Retail Hub", "High-Yield Investment Property"],
        "metric_1": "500+ Properties",
        "metric_2": "100% Clear Titles",
        "metric_label": "Happy Buyers"
    },

    # 🩺 9. MEDICAL & CLINICS
    "medical": {
        "layout_style": "split_modern",
        "keywords": ["clinic", "doctor", "hospital", "ortho", "bone", "joint", "physio", "surgeon", "health", "care", "eye", "skin doctor", "pediatric", "diagnostic", "pathology"],
        "icon": "fa-user-doctor",
        "badge": "Healthcare Excellence",
        "theme": "sky",
        "accent_hex": "#0ea5e9",
        "gradient": "from-sky-600 via-blue-600 to-sky-600",
        "glow": "bg-sky-600/20",
        "hero_title": "Advanced Medical Excellence & Compassionate Care at {name}",
        "hero_desc": "Delivering world-class diagnostic accuracy, modern minimally-invasive treatments, and patient-first rehabilitation in {city}.",
        "hero_img": "https://images.unsplash.com/photo-1629909613654-28e377c37b09?auto=format&fit=crop&w=1000&q=80",
        "cta_booking": "Book Doctor Consultation",
        "cta_chat": "WhatsApp Clinic",
        "service_title": "Comprehensive Treatments & Specialized Clinical Care",
        "services": [
            {
                "title": "Specialist Consultation & Accurate Diagnostics",
                "desc": "Digital evaluations, thorough health history assessments, and customized treatment planning.",
                "badge": "🩺 Expert Diagnosis",
                "img": "https://images.unsplash.com/photo-1579684385127-1ef15d508118?auto=format&fit=crop&w=600&q=80"
            },
            {
                "title": "Minimally Invasive Procedures",
                "desc": "Latest therapeutic equipment ensuring minimal discomfort, faster recovery, and high clinical success.",
                "badge": "🔬 Modern Tech",
                "img": "https://images.unsplash.com/photo-1584515979956-d9f6e5d09982?auto=format&fit=crop&w=600&q=80"
            },
            {
                "title": "Preventive Care & Rehabilitation",
                "desc": "Long-term wellness monitoring, lifestyle guidance, and personalized follow-up care for all patients.",
                "badge": "🩹 Rapid Recovery",
                "img": "https://images.unsplash.com/photo-1576091160550-2173dba999ef?auto=format&fit=crop&w=600&q=80"
            }
        ],
        "booking_heading": "Schedule Your In-Clinic Consultation",
        "booking_field_label": "Consultation Type",
        "booking_options": ["Initial Specialist Consultation", "Follow-up Checkup", "Second Medical Opinion", "Routine Health Checkup"],
        "metric_1": "20,000+ Patients",
        "metric_2": "100% Sterile",
        "metric_label": "Happy Patients"
    },

    # 🚗 10. AUTOMOTIVE & CAR REPAIR
    "auto": {
        "layout_style": "split_modern",
        "keywords": ["car", "auto", "motor", "mechanic", "detailing", "garage", "wheel", "tyre", "service station", "honda", "hyundai", "toyota", "maruti", "repair"],
        "icon": "fa-car-side",
        "badge": "Automotive Excellence",
        "theme": "blue",
        "accent_hex": "#3b82f6",
        "gradient": "from-blue-600 via-indigo-600 to-blue-600",
        "glow": "bg-blue-600/20",
        "hero_title": "Precision Auto Care & High-Performance Detailing at {name}",
        "hero_desc": "Certified mechanics, computerized diagnostic scanning, ceramic coating, and genuine OEM parts in {city}.",
        "hero_img": "https://images.unsplash.com/photo-1617814076367-b759c7d7e738?auto=format&fit=crop&w=1000&q=80",
        "cta_booking": "Book Service / Inspection",
        "cta_chat": "Inquire on WhatsApp",
        "service_title": "Complete Automotive Care & Detailing Solutions",
        "services": [
            {
                "title": "Periodic Service & Computer Diagnostics",
                "desc": "50-point safety check, synthetic engine oil change, brake overhaul, and computerized ECU scanning.",
                "badge": "🔧 Full Service",
                "img": "https://images.unsplash.com/photo-1486006920555-c77dce18193b?auto=format&fit=crop&w=600&q=80"
            },
            {
                "title": "Ceramic Coating & Paint Protection (PPF)",
                "desc": "Ultra-gloss 9H ceramic shield and self-healing TPU paint protection films with multi-year warranties.",
                "badge": "✨ 9H Ceramic",
                "img": "https://images.unsplash.com/photo-1601362840469-51e4d8d58785?auto=format&fit=crop&w=600&q=80"
            },
            {
                "title": "Suspension, AC & Wheel Alignment",
                "desc": "3D laser wheel alignment, nitrogen inflation, automated AC refrigerant gas recharge, and suspension tuning.",
                "badge": "⚙️ Precision Tech",
                "img": "https://images.unsplash.com/photo-1580273916550-e323be2ae537?auto=format&fit=crop&w=600&q=80"
            }
        ],
        "booking_heading": "Schedule Your Vehicle Service or Detailing",
        "booking_field_label": "Service Required",
        "booking_options": ["Periodic Maintenance Service", "Ceramic Coating / Detailing", "AC & Mechanical Repair", "General Inspection & Quote"],
        "metric_1": "10,000+ Cars Serviced",
        "metric_2": "100% OEM Parts",
        "metric_label": "Satisfied Drivers"
    },

    # ⚖️ 11. LEGAL & CA
    "legal": {
        "layout_style": "bento_luxury",
        "keywords": ["lawyer", "advocate", "legal", "attorney", "ca ", "chartered accountant", "tax", "audit", "law firm", "consultancy", "notary"],
        "icon": "fa-scale-balanced",
        "badge": "Trusted Advisory Firm",
        "theme": "indigo",
        "accent_hex": "#6366f1",
        "gradient": "from-slate-700 via-indigo-900 to-slate-900",
        "glow": "bg-indigo-600/15",
        "hero_title": "Authoritative Legal Counsel & Strategic Solutions at {name}",
        "hero_desc": "Delivering discreet, authoritative legal counsel, corporate compliance, property title documentation, and tax strategy across {city}.",
        "hero_img": "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?auto=format&fit=crop&w=1000&q=80",
        "cta_booking": "Book Confidential Consultation",
        "cta_chat": "WhatsApp Advisory",
        "service_title": "Comprehensive Legal & Corporate Practice Areas",
        "services": [
            {
                "title": "Corporate Compliance & Contracts",
                "desc": "Business incorporation, contract drafting, vendor agreements, dispute resolution, and commercial litigation.",
                "badge": "⚖️ Corporate Law",
                "img": "https://images.unsplash.com/photo-1450133064473-71024230f91b?auto=format&fit=crop&w=600&q=80"
            },
            {
                "title": "Property Title Verification & Civil Law",
                "desc": "Due diligence, clear title searches, registry dispute arbitration, and real estate legal representation.",
                "badge": "📜 Property Law",
                "img": "https://images.unsplash.com/photo-1521791136064-7986c2920216?auto=format&fit=crop&w=600&q=80"
            },
            {
                "title": "Tax Advisory & Financial Audits",
                "desc": "Direct/indirect tax strategy, GST compliance, appellate tribunal representations, and wealth protection.",
                "badge": "📊 Tax & Audit",
                "img": "https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?auto=format&fit=crop&w=600&q=80"
            }
        ],
        "booking_heading": "Schedule a Confidential Legal Consultation",
        "booking_field_label": "Consultation Category",
        "booking_options": ["Corporate & Business Advisory", "Property & Real Estate Law", "Civil & Family Matters", "Taxation & Compliance"],
        "metric_1": "15+ Years Experience",
        "metric_2": "100% Confidential",
        "metric_label": "Cases Resolved"
    },

    # 🎓 12. EDUCATION & ACADEMIES
    "education": {
        "layout_style": "split_modern",
        "keywords": ["school", "college", "coaching", "classes", "tuition", "institute", "training", "education", "ielts", "study abroad", "upsc", "jee", "neet"],
        "icon": "fa-graduation-cap",
        "badge": "Academic Excellence",
        "theme": "teal",
        "accent_hex": "#14b8a6",
        "gradient": "from-teal-600 via-cyan-600 to-teal-600",
        "glow": "bg-teal-600/20",
        "hero_title": "Unlock Your Academic Potential & Dream Career with {name}",
        "hero_desc": "Proven mentorship, structured study material, test series, and interactive doubt resolution in {city}.",
        "hero_img": "https://images.unsplash.com/photo-1523240795612-9a054b0db644?auto=format&fit=crop&w=1000&q=80",
        "cta_booking": "Book Free Demo Class",
        "cta_chat": "WhatsApp Admissions",
        "service_title": "Comprehensive Academic Programs & Batches",
        "services": [
            {
                "title": "Foundation & Comprehensive Courses",
                "desc": "Concept clarity, daily practice papers, and individual attention from top-tier experienced faculty.",
                "badge": "🎓 Core Programs",
                "img": "https://images.unsplash.com/photo-1524178232363-1fb2b075b655?auto=format&fit=crop&w=600&q=80"
            },
            {
                "title": "All-India Test Series & Mock Exams",
                "desc": "Exam-pattern mock tests with AI-driven weak area analysis, rank benchmarking, and strategy sessions.",
                "badge": "📈 Test Series",
                "img": "https://images.unsplash.com/photo-1434030216411-0b793f4b4173?auto=format&fit=crop&w=600&q=80"
            },
            {
                "title": "1-on-1 Mentorship & Doubt Clearing",
                "desc": "Dedicated daily doubt-solving desks, small batch sizes, and progress tracking for every student.",
                "badge": "💡 1-on-1 Help",
                "img": "https://images.unsplash.com/photo-1577896851231-70ef18881754?auto=format&fit=crop&w=600&q=80"
            }
        ],
        "booking_heading": "Register for a Free Demo Class / Counseling",
        "booking_field_label": "Program of Interest",
        "booking_options": ["Regular Classroom Program", "Crash Course / Test Series", "Weekend Batch", "Free 1-on-1 Counseling"],
        "metric_1": "95%+ Selection Rate",
        "metric_2": "100% Mentorship",
        "metric_label": "Students Mentored"
    },

    # 💼 13. GENERAL BUSINESS & PROFESSIONAL SERVICES
    "business": {
        "layout_style": "bento_luxury",
        "keywords": [],
        "icon": "fa-briefcase",
        "badge": "Verified Premier Provider",
        "theme": "indigo",
        "accent_hex": "#6366f1",
        "gradient": "from-indigo-600 via-blue-600 to-indigo-600",
        "glow": "bg-indigo-600/20",
        "hero_title": "Premier Solutions, Exceptional Quality & Trust with {name}",
        "hero_desc": "Delivering reliable, transparent, and award-winning solutions tailored to exceed your expectations in {city}.",
        "hero_img": "https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&w=1000&q=80",
        "cta_booking": "Book Free Consultation",
        "cta_chat": "Chat on WhatsApp",
        "service_title": "Our Professional Services & Solutions",
        "services": [
            {
                "title": "Comprehensive Consulting & Planning",
                "desc": "Tailored guidance, transparent evaluations, and step-by-step strategy to achieve your specific goals.",
                "badge": "✨ Quality Assured",
                "img": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=600&q=80"
            },
            {
                "title": "End-to-End Service Execution",
                "desc": "Dedicated team support, high-standard materials, and guaranteed satisfaction on every project.",
                "badge": "⚡ Turnkey Solution",
                "img": "https://images.unsplash.com/photo-1557804506-669a67965ba0?auto=format&fit=crop&w=600&q=80"
            },
            {
                "title": "Long-Term Support & Assistance",
                "desc": "Continuous customer assistance, warranty guarantees, and dependable relationship management.",
                "badge": "🛡️ 100% Reliable",
                "img": "https://images.unsplash.com/photo-1522071820081-009f0129c71c?auto=format&fit=crop&w=600&q=80"
            }
        ],
        "booking_heading": "Schedule Your Free Consultation",
        "booking_field_label": "Requirement Type",
        "booking_options": ["Standard Service Consultation", "Custom Project Discussion", "Price Quote & Estimate", "Urgent Support Request"],
        "metric_1": "1,000+ Completed",
        "metric_2": "100% Guaranteed",
        "metric_label": "Satisfied Clients"
    }
}


def resolve_niche_data(category: Optional[str] = "", business_name: Optional[str] = "", city: Optional[str] = "") -> Dict[str, Any]:
    """Analyze category and business name, returning complete tailored niche content & design assets."""
    target_text = f"{(category or '').lower()} {(business_name or '').lower()}"
    city_name = city or "your city"
    b_name = business_name or "Official Business"

    matched_niche = "business"
    for niche_key, niche_info in NICHE_DEFINITIONS.items():
        if niche_key == "business":
            continue
        for kw in niche_info["keywords"]:
            if kw in target_text:
                matched_niche = niche_key
                break
        if matched_niche != "business":
            break

    niche = NICHE_DEFINITIONS[matched_niche].copy()
    niche["niche_key"] = matched_niche
    niche["hero_title"] = niche["hero_title"].format(name=b_name)
    niche["hero_desc"] = niche["hero_desc"].format(city=city_name)
    return niche
