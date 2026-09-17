import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#64748B"))
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(54, 40, letter[0] - 54, 40)
        
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, letter[1] - 36, "LeadHunter AI — Official Operations & Architecture Manual")
            self.line(54, letter[1] - 42, letter[0] - 54, letter[1] - 42)
            
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(letter[0] - 54, 25, page_text)
        self.drawString(54, 25, "Confidential — For Internal & Agency Use Only")
        self.restoreState()


def generate_pdf(output_path="LeadHunter_AI_Documentation.pdf"):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    # Custom Palette
    primary = colors.HexColor("#1E293B")
    accent = colors.HexColor("#2563EB")
    secondary = colors.HexColor("#0F172A")
    light_bg = colors.HexColor("#F8FAFC")
    border_color = colors.HexColor("#E2E8F0")

    # Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=accent,
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#475569"),
        spaceAfter=14
    )

    h1_style = ParagraphStyle(
        'H1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        textColor=primary,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'H2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=accent,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor("#334155"),
        spaceAfter=6
    )

    code_style = ParagraphStyle(
        'CodeBlock',
        parent=styles['Code'],
        fontName='Courier',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#0F172A"),
        backColor=colors.HexColor("#F1F5F9"),
        borderColor=border_color,
        borderWidth=0.5,
        borderPadding=6,
        spaceBefore=4,
        spaceAfter=8
    )

    story = []

    # Title Banner
    story.append(Paragraph("LeadHunter AI", title_style))
    story.append(Paragraph("Autonomous B2B Lead Engine & Local Outreach Platform — Operations Manual", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=accent, spaceBefore=0, spaceAfter=12))

    # Executive Overview
    story.append(Paragraph("1. Executive Overview", h1_style))
    story.append(Paragraph(
        "<b>LeadHunter AI</b> is an autonomous agent designed for digital agencies, web design freelancers, and growth consultants. "
        "The system scans local businesses via Google Maps (SerpAPI), classifies online presence (missing, broken, or social-only websites), "
        "scores prospect urgency, builds live mobile demo sites on custom preview URLs, and prepares cold outreach via Gmail SMTP and WhatsApp.",
        body_style
    ))

    # Architecture Overview
    story.append(Paragraph("2. Pipeline Architecture (11 Stages)", h1_style))
    
    stages_data = [
        ["Stage", "Name", "Key Functionality"],
        ["1", "Discovery", "Queries SerpAPI Google Maps; extracts phone, address, rating, review count."],
        ["2", "Dedup & Normalization", "Strips +91, cleans URLs, generates deterministic SHA256 lead_id hash."],
        ["3", "Website Verification", "HTTP crawler detects NO_WEBSITE, BROKEN_WEBSITE, SOCIAL_ONLY, VALID_WEBSITE."],
        ["4", "Scoring & Tiering", "Assigns 0-100 score: HOT (≥70), WARM (45-69), LOW (<45)."],
        ["5", "AI Personalization", "Generates custom subject lines, cold email, & WhatsApp copy via Claude/Template."],
        ["6", "Demo Website Engine", "Creates single-page mobile preview websites hosted on /preview/{slug}."],
        ["7", "Google Sheets Sync", "Synchronizes 26 columns to 'Leads' tab and batch logs to 'Runs' tab."],
        ["8", "Human Approval Gate", "Interactive Web UI & terminal cards ([A]pprove / [R]eject / [S]kip)."],
        ["9", "Outbound Outreach", "Dispatches emails (Gmail SMTP) & WhatsApp with rolling hourly rate limits."],
        ["10", "Follow-Up Lifecycle", "Automated Day 3 (Follow-up 1), Day 7 (Follow-up 2), and Day 10 (Cold) schedule."]
    ]

    t_stages = Table(stages_data, colWidths=[40, 130, 334])
    t_stages.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, border_color),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, light_bg])
    ]))
    story.append(t_stages)
    story.append(Spacer(1, 10))

    # Scoring Criteria Table
    story.append(Paragraph("3. Prospect Scoring Engine", h1_style))
    scoring_data = [
        ["Signal / Condition", "Points Awarded", "Qualification Tier"],
        ["NO_WEBSITE (No site found)", "+40 pts", "HOT (Score ≥ 70) — Immediate Outreach"],
        ["BROKEN_WEBSITE (HTTP 4xx/5xx/SSL)", "+35 pts", "HOT (Score ≥ 70) — High Urgency Pitch"],
        ["SOCIAL_ONLY (Facebook / IG only)", "+30 pts", "WARM (Score 45-69) — Opportunity Pitch"],
        ["Has Phone Number (10 digits)", "+15 pts", "Required for WhatsApp Dispatch"],
        ["Rating 4.0+ with 20+ Reviews", "+15 pts", "Strong local reputation signal"],
        ["Target Niche (Restaurant, Clinic, Salon, Gym)", "+10 pts", "High web-conversion sector"],
        ["VALID_WEBSITE (Active custom website)", "0 pts", "LOW (< 45 pts) — Archived in Database"]
    ]
    t_scoring = Table(scoring_data, colWidths=[180, 110, 214])
    t_scoring.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), secondary),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, border_color),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, light_bg])
    ]))
    story.append(t_scoring)
    story.append(Spacer(1, 10))

    # CLI & Operations Guide
    story.append(Paragraph("4. Key Operational Commands", h1_style))
    story.append(Paragraph("<b>1. Start Web Control Center (Port 8500):</b>", h2_style))
    story.append(Paragraph("python main.py --web --port 8500", code_style))

    story.append(Paragraph("<b>2. Start Cloudflare Public Tunnel (Allows mobile preview):</b>", h2_style))
    story.append(Paragraph("cloudflared tunnel --url http://localhost:8500", code_style))

    story.append(Paragraph("<b>3. Run Full Pipeline for Any City (CLI Mode):</b>", h2_style))
    story.append(Paragraph("python main.py --all --city \"Chandigarh\" --category \"restaurants\" --limit 5", code_style))

    story.append(Paragraph("<b>4. Run Automated Follow-Up Cycle:</b>", h2_style))
    story.append(Paragraph("python main.py --followups", code_style))

    story.append(Paragraph("5. Environment Configuration (.env Reference)", h1_style))
    env_content = (
        "# --- Google Maps Discovery ---\n"
        "SERPAPI_KEY=8b9e65a6e530034833b3d1f0b555227a54e956330dc6de4324ca95a182efd643\n\n"
        "# --- Public Demo Base URL (Cloudflare Tunnel) ---\n"
        "DEMO_BASE_URL=https://your-tunnel.trycloudflare.com\n\n"
        "# --- Email Outreach (Gmail SMTP) ---\n"
        "SENDER_EMAIL=your-real-email@gmail.com\n"
        "SENDER_NAME=Your Agency Name\n"
        "GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx  # 16-character App Password\n\n"
        "# --- Safety Guards ---\n"
        "DRY_RUN=true    # Set false only when ready for real dispatch"
    )
    story.append(Paragraph(env_content.replace("\n", "<br/>"), code_style))

    story.append(Paragraph("6. Safety & Anti-Spam Compliance Guardrails", h1_style))
    story.append(Paragraph(
        "• <b>DRY_RUN Safety Net:</b> Outreach execution is simulated by default unless DRY_RUN=false is explicitly set.<br/>"
        "• <b>Mandatory Human Approval Gate:</b> System strictly prevents email/WhatsApp dispatch unless approval_status is APPROVED.<br/>"
        "• <b>Rate Limiting:</b> Cap of 10 emails/hour and 20 WhatsApp messages/hour with 3-second inter-message delay.<br/>"
        "• <b>Opt-out & Reply Tracking:</b> Leads marked as REPLIED or DO_NOT_CONTACT are permanently excluded from follow-ups.",
        body_style
    ))

    # Build Document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[SUCCESS] PDF Documentation generated successfully at: {output_path}")

if __name__ == "__main__":
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    generate_pdf()
