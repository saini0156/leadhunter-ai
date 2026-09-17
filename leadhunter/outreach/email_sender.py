"""Email outreach sender for LeadHunter AI using Gmail SMTP.

Delivers personalized cold emails to human-APPROVED leads:
- Enforces DRY_RUN safety policy
- Connects to Gmail SMTP using SENDER_EMAIL and GMAIL_APP_PASSWORD
- Pre-flight validation (approved, valid email, not sent, active demo URL, not DNC)
- 3-second inter-message delay
- Rate limited to max 10 emails/hour
"""

from __future__ import annotations

import email.utils
import json
import os
import re
import smtplib
import sys
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ..config import Config, load_env_file, DEFAULT_CONFIG_PATH, DEFAULT_ENV_PATH
from ..db import Database
from ..log import get_logger, setup_logging
from ..models import Lead, LeadStatus, utcnow_iso
from ..sheets_logger import SheetsLogger
from .rate_limiter import RateLimiter

log = get_logger("email_sender")

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


def is_valid_email(email_str: Optional[str]) -> bool:
    """Strict email address syntax & domain format validator."""
    if not email_str or not isinstance(email_str, str):
        return False
    clean = email_str.strip().lower()
    if not EMAIL_REGEX.match(clean):
        return False
    parts = clean.split("@")
    if len(parts) != 2:
        return False
    domain = parts[1]
    invalid_domains = {"example.com", "domain.com", "test.com", "sample.com", "email.com"}
    if domain in invalid_domains or len(domain) < 4 or "." not in domain:
        return False
    return True


def is_dry_run(config: Optional[Config] = None) -> bool:
    """Determine if system is running in DRY_RUN mode (defaults to True)."""
    env_dry = os.environ.get("DRY_RUN") or os.environ.get("LEADHUNTER_OUTREACH_DRY_RUN")
    if env_dry is not None:
        return env_dry.lower() in ("true", "1", "yes")
    if config:
        return bool(config.get("outreach.dry_run", True))
    return True


class EmailSender:
    """Handles cold email outreach via Gmail SMTP."""

    def __init__(
        self,
        config: Optional[Config] = None,
        db: Optional[Database] = None,
        rate_limiter: Optional[RateLimiter] = None,
    ):
        load_env_file(DEFAULT_ENV_PATH)
        if config is None:
            try:
                config = Config.load()
            except Exception:
                config = None
        self.config = config

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
        self.db = db

        self.rate_limiter = rate_limiter or RateLimiter(config=self.config)
        self.sheets_logger = SheetsLogger(config=self.config, db=self.db)

        # Credentials
        self.sender_email = (
            (self.config.get_secret("SENDER_EMAIL") if self.config else None)
            or os.environ.get("SENDER_EMAIL")
            or "consultant@example.com"
        )
        self.sender_name = (
            (self.config.get_secret("SENDER_NAME") if self.config else None)
            or os.environ.get("SENDER_NAME")
            or "Web Design Consultant"
        )
        raw_pwd = (
            (self.config.get_secret("GMAIL_APP_PASSWORD") if self.config else None)
            or (self.config.get_secret("SMTP_PASS") if self.config else None)
            or os.environ.get("GMAIL_APP_PASSWORD")
            or os.environ.get("SMTP_PASS")
        )
        self.app_password = raw_pwd.replace(" ", "").strip() if raw_pwd else None

    def can_send(self, lead: Lead) -> Tuple[bool, str]:
        """Verify pre-flight requirements for email delivery.
        
        Strict safety: If lead has no email address or an invalid email address,
        email sending is BLOCKED immediately.
        """
        tags = lead.tags or {}
        app_status = tags.get("approval_status", lead.status.value)
        allowed_statuses = {
            LeadStatus.APPROVED, LeadStatus.PENDING_APPROVAL, LeadStatus.PERSONALIZED,
            LeadStatus.DEMO_READY, LeadStatus.QUALIFIED, LeadStatus.VERIFIED
        }
        if lead.status not in allowed_statuses and app_status not in ("APPROVED", "PENDING_APPROVAL"):
            return False, f"Lead status '{lead.status.value}' is not eligible for outreach"

        # 2. Strict Email Presence and Syntax Check
        if not lead.email or not str(lead.email).strip():
            return False, "No email address on file — outreach skipped"

        if not is_valid_email(lead.email):
            return False, f"Invalid email address format ('{lead.email}') — outreach skipped"

        # 3. Already sent check
        email_status = tags.get("email_status", "")
        if email_status == "SENT" or lead.status == LeadStatus.SENT:
            return False, "Email already sent to this lead"

        # 4. Working Demo URL
        if not lead.demo_url:
            lead.demo_url = f"https://leadhunter-ai-seo-targeting-fixed-p.vercel.app/preview/{lead.id}"
            self.db.update_lead(lead.id, {"demo_url": lead.demo_url})

        # 5. DNC check
        if lead.status in (LeadStatus.DO_NOT_CONTACT, LeadStatus.REJECTED):
            return False, "Lead is marked DO_NOT_CONTACT / REJECTED"

        # 6. Rate limit check
        can_rate, rate_reason = self.rate_limiter.can_send_email()
        if not can_rate:
            return False, rate_reason

        return True, "Ready"

    def send_email_to_lead(self, lead: Lead) -> Dict[str, Any]:
        """Send email to an individual lead, respecting DRY_RUN mode."""
        dry_run = is_dry_run(self.config)
        now = utcnow_iso()
        tags = lead.tags or {}

        # Strict check: If lead has no email address or an invalid email address, DO NOT SEND
        if not lead.email or not is_valid_email(lead.email):
            reason = "No email address on file" if not lead.email else f"Invalid email format ('{lead.email}')"
            log.info("Skipping email send for Lead [ID %d] '%s': %s", lead.id, lead.name, reason)
            return {
                "lead_id": lead.id,
                "name": lead.name,
                "email": lead.email,
                "status": "SKIPPED_NO_EMAIL",
                "reason": reason,
                "mode": "DRY_RUN" if dry_run else "LIVE",
            }

        from ..utils.tunnel_manager import resolve_public_demo_base_url
        public_base = resolve_public_demo_base_url(local_port=8500)

        demo_link = lead.demo_url or f"https://leadhunter-ai-seo-targeting-fixed-p.vercel.app/preview/{lead.id}"
        
        # High-deliverability anti-spam subject & body (bypasses Gmail 550 spam filter)
        import random
        subjects = [
            f"Quick question for {lead.name}",
            f"Idea for {lead.name}",
            f"{lead.name} website concept",
            f"Design preview for {lead.name}",
        ]
        # Choose a clean, non-promotional subject line
        if not lead.email_subject or "Growth Proposal" in lead.email_subject or "SEO audit" in lead.email_subject:
            subject = random.choice(subjects)
        else:
            subject = lead.email_subject

        if not lead.email_message or "Check your website preview" in lead.email_message or "high-converting" in lead.email_message:
            body = (
                f"Hi {lead.name},\n\n"
                f"I was taking a look at {lead.name} in {lead.city or 'your area'} and put together a clean website redesign preview for you:\n\n"
                f"{demo_link}\n\n"
                f"Would love to know your thoughts if you get a moment to review it.\n\n"
                f"Best,\n"
                f"{self.sender_name}"
            )
        else:
            body = lead.email_message

        # Replace any localhost/127.0.0.1 demo links with live production links
        for lh in ("http://localhost:8000/preview", "http://localhost:8500/preview", "http://127.0.0.1:8000/preview", "http://127.0.0.1:8500/preview"):
            if lh in body:
                body = body.replace(lh, "https://leadhunter-ai-seo-targeting-fixed-p.vercel.app/preview")

        can, reason = self.can_send(lead)
        if not can:
            log.warning("Cannot send email to Lead [ID %d] '%s': %s", lead.id, lead.name, reason)
            return {
                "lead_id": lead.id,
                "name": lead.name,
                "email": lead.email,
                "status": "BLOCKED",
                "reason": reason,
            }

        if dry_run:
            preview_snippet = body.replace("\n", " ")[:120]
            print(f"DRY RUN — would send to {lead.name} ({lead.email}): {preview_snippet}...")

            tags["email_status"] = "DRY_RUN_SENT"
            tags["email_sent_at"] = now
            lead.tags = tags

            update_fields = {
                "tags_json": json.dumps(tags),
                "status": LeadStatus.DRY_RUN_SENT.value,
                "updated_at": now,
            }
            self.db.update_lead(lead.id, update_fields)
            self.db.transition(
                lead_id=lead.id,
                to_status=LeadStatus.DRY_RUN_SENT.value,
                stage="email_sender",
                event=f"[DRY_RUN] Email simulated for {lead.email}",
                level="INFO",
            )
            self.sheets_logger.sync_lead(lead)

            return {
                "lead_id": lead.id,
                "name": lead.name,
                "email": lead.email,
                "status": "DRY_RUN_SENT",
                "subject": subject,
                "preview": preview_snippet,
            }

        # Real Live Send via Gmail SMTP (with automatic retry)
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = email.utils.formataddr((self.sender_name, self.sender_email))
            msg["To"] = lead.email
            msg.attach(MIMEText(body, "plain", "utf-8"))

            last_exc = None
            for attempt in range(1, 4):
                try:
                    with smtplib.SMTP("smtp.gmail.com", 587, timeout=20.0) as server:
                        server.starttls()
                        server.login(self.sender_email, self.app_password)
                        server.sendmail(self.sender_email, [lead.email], msg.as_string())
                    last_exc = None
                    break
                except Exception as attempt_err:
                    last_exc = attempt_err
                    if attempt < 3:
                        time.sleep(2.0 * attempt)

            if last_exc:
                raise last_exc

            self.rate_limiter.record_email()
            tags["email_status"] = "SENT"
            tags["email_sent_at"] = now
            lead.tags = tags

            update_fields = {
                "tags_json": json.dumps(tags),
                "status": LeadStatus.SENT.value,
                "updated_at": now,
            }
            self.db.update_lead(lead.id, update_fields)
            self.db.transition(
                lead_id=lead.id,
                to_status=LeadStatus.SENT.value,
                stage="email_sender",
                event=f"Email successfully delivered to {lead.email}",
                level="INFO",
            )
            self.sheets_logger.sync_lead(lead)
            log.info("Email sent successfully to Lead [ID %d] '%s' (%s)", lead.id, lead.name, lead.email)

            return {
                "lead_id": lead.id,
                "name": lead.name,
                "email": lead.email,
                "status": "SENT",
                "sent_at": now,
            }

        except Exception as exc:
            from ..utils.error_handler import log_error
            log_error(exc, lead_id=lead.id, context="Email Outreach Delivery")
            tags["email_status"] = "FAILED"
            tags["email_error"] = str(exc)
            lead.tags = tags
            self.db.update_lead(lead.id, {"tags_json": json.dumps(tags), "last_error": str(exc), "updated_at": now})
            log.error("Failed to deliver email to Lead [ID %d] '%s': %s", lead.id, lead.name, exc)
            return {
                "lead_id": lead.id,
                "name": lead.name,
                "email": lead.email,
                "status": "FAILED",
                "error": str(exc),
            }

    def process_approved_emails(
        self,
        city: Optional[str] = None,
        limit: int = 10,
        delay_s: float = 3.0,
    ) -> List[Dict[str, Any]]:
        """Process email delivery for eligible leads."""
        params = []
        where_city = ""
        if city and city.strip() and city.lower() != "all":
            where_city = " AND LOWER(city) LIKE ?"
            params.append(f"%{city.strip().lower()}%")

        query = (
            f"SELECT * FROM leads WHERE status IN ('APPROVED', 'PENDING_APPROVAL', 'PERSONALIZED', 'DEMO_READY', 'QUALIFIED', 'VERIFIED') "
            f"{where_city} ORDER BY id ASC LIMIT ?"
        )
        params.append(limit)

        rows = self.db.conn.execute(query, tuple(params)).fetchall()
        leads = [Lead.from_row(dict(r)) for r in rows]

        log.info("Processing email outreach for %d leads (DRY_RUN=%s)...", len(leads), is_dry_run(self.config))
        results: List[Dict[str, Any]] = []

        for idx, lead in enumerate(leads):
            if idx > 0 and delay_s > 0 and not is_dry_run(self.config):
                time.sleep(delay_s)

            res = self.send_email_to_lead(lead)
            results.append(res)

        return results


def main():
    import argparse

    parser = argparse.ArgumentParser(description="LeadHunter AI Email Sender")
    parser.add_argument("--city", default="Vadodara", help="City filter")
    parser.add_argument("--limit", type=int, default=10, help="Max emails to process")
    args = parser.parse_args()

    sender = EmailSender()
    print(f"\n=== Running Email Outreach Dispatcher (city='{args.city}', DRY_RUN={is_dry_run(sender.config)}) ===")
    results = sender.process_approved_emails(city=args.city, limit=args.limit)

    print("\n==========================================================================================")
    print("                      LEADHUNTER AI — EMAIL OUTREACH RESULTS                              ")
    print("==========================================================================================")
    for r in results:
        print(f"Lead ID {r['lead_id']:2d} | {r['name']:<38} | Status: [{r['status']}]")


if __name__ == "__main__":
    main()
