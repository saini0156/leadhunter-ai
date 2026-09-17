# LeadHunter AI — Complete Operations & Developer Manual

---

## 1. System Overview
LeadHunter AI is an autonomous end-to-end B2B client acquisition platform built for agencies and freelancers offering web development and digital marketing services to local businesses.

---

## 2. Directory Structure
```text
leadhunter-ai/
├── main.py                      # Master CLI Orchestrator & Entrypoint
├── config.yaml                  # System Configuration, Scoring Weights, & Limits
├── .env                         # API Credentials & SMTP Configuration (Git Ignored)
├── google_creds.json            # Google Cloud Service Account Credentials
├── requirements.txt             # Python Package Dependencies
├── LeadHunter_Pro.bat           # 1-Click Interactive Windows Batch Launcher
├── README.md                    # Project Readme & Overview
├── DOCUMENTATION.md             # Complete Operations Manual
│
├── leadhunter/                  # Main Application Package
│   ├── discovery/               # Google Maps Scraping via SerpAPI
│   │   └── serpapi_search.py
│   ├── processing/              # Data Cleansing & Qualification
│   │   ├── normalization.py     # Phone, Name, URL sanitization
│   │   ├── deduplicate.py       # Exact & fuzzy deduplication + quality scores
│   │   ├── website_checker.py   # HTTP status classifier (NO_WEBSITE, SOCIAL_ONLY, etc.)
│   │   └── lead_scorer.py       # HOT, WARM, LOW tier point scoring engine
│   ├── ai/                      # Copywriting & Messaging
│   │   └── personalizer.py      # Claude Sonnet prompt generator + template fallback
│   ├── demo/                    # Client Demo Websites
│   │   ├── url_generator.py     # Slug generator & URL verification
│   │   ├── server.py            # Local FastAPI demo server
│   │   └── templates/
│   │       └── preview.html     # Responsive client landing page template
│   ├── approval/                # Human Review Gate
│   │   ├── approval_queue.py    # Staging queue SQLite manager
│   │   └── approval_viewer.py   # Terminal human approval cards ([A]/[R]/[S])
│   ├── outreach/                # Dispatch Senders
│   │   ├── email_sender.py      # Gmail SMTP dispatcher with rate limiter
│   │   ├── whatsapp_sender.py   # Meta WhatsApp Cloud API dispatcher
│   │   └── rate_limiter.py      # 10 emails/hr & 20 WA/hr rolling limiter
│   ├── followup/                # Automated Re-engagement
│   │   └── followup_engine.py   # Day 3 & Day 7 follow-up scheduler + COLD marker
│   ├── web/                     # Web Control Center
│   │   ├── app.py               # FastAPI backend for dashboard
│   │   └── templates/
│   │       └── dashboard.html   # Real-time multi-city dashboard UI
│   ├── db.py                    # SQLite database layer with auto-migration
│   ├── config.py                # Environment loader & YAML config parser
│   ├── models.py                # Dataclasses (Lead, ApprovalRecord, RunSummary)
│   ├── sheets_logger.py         # Google Sheets 26-column synchronization
│   └── utils/
│       ├── log.py               # UTF-8 structured file + console logger
│       └── error_handler.py     # Error classification & exponential backoff
│
└── data/                        # Persistent Storage
    ├── leadhunter.db            # SQLite database file
    ├── logs/
    │   └── leadhunter.log       # Rolling log file
    └── export/
        └── leads_sync.csv       # Local offline backup of Google Sheets sync
```

---

## 3. How the Pipeline Works (11 Stages)

### Stage 1: Business Discovery
- Queries SerpAPI Google Maps endpoint for `"{category} in {city}"`.
- Extracts Business Name, Phone, Address, Website, Rating, and Review Count.
- Generates a deterministic SHA256 `lead_id` hash (`business_name + city + phone`) to prevent duplicates.

### Stage 2: Normalization & Deduplication
- Strips `+91`, spaces, and dashes from Indian phone numbers to yield clean 10-digit numbers.
- Lowercases URLs, strips `www.` and trailing slashes.
- Assigns a data quality score (0–100) based on signal availability.

### Stage 3: Website Verification
- Makes an asynchronous HTTP GET request with a 10-second timeout.
- Classifies each lead into:
  - `NO_WEBSITE`: No URL provided in Google Maps.
  - `BROKEN_WEBSITE`: URL returned HTTP 4xx, 5xx, SSL error, or DNS failure.
  - `SOCIAL_ONLY`: Business only has a Facebook, Instagram, or Justdial link.
  - `DIRECTORY_ONLY`: Business only listed on IndiaMart, Sulekha, or yellow pages.
  - `VALID_WEBSITE`: Business already has an active, working website.

### Stage 4: Lead Scoring & Qualification
- **Points Awarded**:
  - `NO_WEBSITE`: +40 pts
  - `BROKEN_WEBSITE`: +35 pts
  - `SOCIAL_ONLY`: +30 pts
  - Has Phone: +15 pts
  - High Rating (4.0+) with 20+ reviews: +15 pts
  - Target Category (restaurant, clinic, salon, gym): +10 pts
- **Tiers**:
  - `HOT` ($\ge 70$ points): Top priority prospects.
  - `WARM` ($45-69$ points): Qualified prospects.
  - `LOW` ($< 45$ points): Stored in database but excluded from outreach.

### Stage 5: AI Copywriting & Message Personalization
- Sends business profile to Claude 3.5 Sonnet to write personalized outreach copy:
  - **Cold Email**: Subject line ($\le 8$ words) + Body ($\le 120$ words).
  - **WhatsApp Message**: Friendly, casual pitch ($\le 80$ words) ending with a question.
- If Claude API key is not present, the system automatically uses built-in high-converting niche copy templates.

### Stage 6: Personalized Demo Website Generation
- Generates a unique landing page URL: `{DEMO_BASE_URL}/preview/{slug}`.
- Verifies that the demo server loads the page and populates the business name, address, and category.

### Stage 7: Google Sheets 26-Column CRM Sync
- Synchronizes all leads into your Google Sheets `Leads` tab.
- Updates existing rows by `Lead ID` without creating duplicate entries.
- Logs run performance metrics to the `Runs` tab.

### Stage 8: Human Approval Gate
- Displays leads on the Web Dashboard (`http://localhost:8500`) or in the terminal.
- Allows you to review email preview, WhatsApp pitch, and demo link before approving.
- **Safety Rule**: Leads marked `REJECTED` are permanently excluded from outreach.

### Stage 9: Outbound Dispatch
- Sends emails via Gmail SMTP using your 16-character App Password.
- Sends WhatsApp messages via Meta WhatsApp Cloud API.
- Implements safety limits: 10 emails/hr, 20 WA/hr, and 3-second inter-message delay.

### Stage 10: Follow-Up Lifecycle Engine
- Automatically checks for leads contacted 3 days ago (Follow-Up 1) and 7 days ago (Follow-Up 2).
- Automatically marks leads as `COLD` after 10 days without a reply.
- Halts follow-ups if a lead replies (`REPLIED`) or opts out (`DO_NOT_CONTACT`).

---

## 4. Key CLI Commands

| Task | Command |
| :--- | :--- |
| **Launch Web UI** | `python main.py --web --port 8500` |
| **Run Full Pipeline** | `python main.py --all --city "Chandigarh" --category "restaurants" --limit 5` |
| **Run Follow-Ups** | `python main.py --followups` |
| **Run Discovery Only** | `python main.py --discover --city "Mohali" --category "cafes" --limit 10` |
| **Run Website Checks** | `python main.py --verify` |
| **Run Scoring** | `python main.py --score` |
| **Run Demo Generation** | `python main.py --demos` |
| **Sync Google Sheets** | `python main.py --sync` |
| **Run Automated Tests** | `python -m unittest discover tests` |

---

## 5. Security & Safety Best Practices
- Never commit `.env` or `google_creds.json` to GitHub (both are in `.gitignore`).
- Keep `DRY_RUN=true` in `.env` until you have reviewed demo sites and are ready to contact businesses.
- Always use a dedicated 16-character Gmail App Password rather than your primary Google password.
