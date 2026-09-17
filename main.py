"""
LeadHunter AI — Main Pipeline CLI Entrypoint.

Coordinates pipeline stages:
- Discovery (SerpAPI / Google Maps)
- Processing (Normalization, Deduplication, Website Verification, Scoring)
- AI Personalization (Groq / Gemini / OpenAI / OpenRouter)
- Demo URL generation & landing page validation
- Human Approval Queue & Terminal Viewer
- Outbound Dispatch (Email & WhatsApp with safety rules)
- Google Sheets Sync
- Follow-up Sequence Engine (--followups)

Usage examples:

    python main.py

    python main.py --city Surrey --category "Roofing contractor" --limit 10 --all

    python main.py --city Surrey --category "Roofing contractor" --discover

    python main.py --city Surrey --category "Roofing contractor" --personalize

    python main.py --followups
"""


from __future__ import annotations

import argparse
import sys


# ============================================================
# WINDOWS UTF-8
# ============================================================

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


# ============================================================
# IMPORTS
# ============================================================

from leadhunter.approval.approval_queue import (
    process_approval_queue,
)

from leadhunter.approval.approval_viewer import (
    ApprovalViewer,
)

from leadhunter.config import (
    load_env_file,
    DEFAULT_ENV_PATH,
)

from leadhunter.demo.url_generator import (
    process_and_generate_demo_urls,
)

from leadhunter.discovery.serpapi_search import (
    search_serpapi_google_maps,
)

from leadhunter.followup.followup_engine import (
    FollowupEngine,
)

from leadhunter.outreach.email_sender import (
    EmailSender,
    is_dry_run,
)

from leadhunter.outreach.whatsapp_sender import (
    WhatsAppSender,
)

from leadhunter.processing.deduplicate import (
    process_leads,
)

from leadhunter.processing.lead_scorer import (
    score_and_qualify_leads,
)

from leadhunter.processing.website_checker import (
    verify_leads_batch,
)

from leadhunter.sheets_logger import (
    sync_leads,
)


# ============================================================
# MAIN
# ============================================================

def main():

    parser = argparse.ArgumentParser(
        description="LeadHunter AI Orchestrator"
    )

    # --------------------------------------------------------
    # TARGET
    # --------------------------------------------------------

    parser.add_argument(
        "--city",
        default="",
        help="Target city",
    )

    parser.add_argument(
        "--category",
        default="",
        help="Business category",
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Maximum number of leads to process",
    )

    parser.add_argument(
        "--service",
        type=str,
        default="Digital Marketing",
        choices=[
            "Digital Marketing",
            "SEO",
            "Website Development",
            "Oracle ERP",
            "SEO + Website Development",
            "Digital Marketing + SEO",
            "All Services",
        ],
        help="Service to target",
    )

    # --------------------------------------------------------
    # MODES
    # --------------------------------------------------------

    parser.add_argument(
        "--web",
        "--dashboard",
        dest="web",
        action="store_true",
        help="Launch interactive Web Control Dashboard",
    )

    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Web dashboard server port",
    )

    parser.add_argument(
        "--followups",
        action="store_true",
        help="Run follow-up sequence engine",
    )

    # --------------------------------------------------------
    # PIPELINE STAGES
    # --------------------------------------------------------

    parser.add_argument(
        "--discover",
        action="store_true",
        help="Run discovery",
    )

    parser.add_argument(
        "--dedup",
        action="store_true",
        help="Run normalization and deduplication",
    )

    parser.add_argument(
        "--verify",
        action="store_true",
        help="Run website verification",
    )

    parser.add_argument(
        "--score",
        action="store_true",
        help="Run lead scoring and qualification",
    )

    parser.add_argument(
        "--personalize",
        action="store_true",
        help="Run AI personalization",
    )

    parser.add_argument(
        "--demos",
        action="store_true",
        help="Generate and verify demo URLs",
    )

    parser.add_argument(
        "--approve",
        action="store_true",
        help="Run interactive human approval",
    )

    parser.add_argument(
        "--outreach",
        action="store_true",
        help="Dispatch email and WhatsApp outreach",
    )

    parser.add_argument(
        "--sync",
        action="store_true",
        help="Sync leads with Google Sheets",
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help="Run complete pipeline",
    )

    args = parser.parse_args()

    # ========================================================
    # LOAD ENVIRONMENT
    # ========================================================

    load_env_file(DEFAULT_ENV_PATH)

    # ========================================================
    # DEFAULT EXECUTION
    # ========================================================

    """
    IMPORTANT:

    Previously:

        python main.py

    did absolutely nothing because no stage flag was supplied.

    Now:

        python main.py

    automatically runs the complete pipeline.

    Explicit stage flags still work normally.
    """

    no_mode_selected = not any(
        [
            args.web,
            args.followups,
            args.discover,
            args.dedup,
            args.verify,
            args.score,
            args.personalize,
            args.demos,
            args.approve,
            args.outreach,
            args.sync,
            args.all,
        ]
    )

    if no_mode_selected:
        args.all = True

    # ========================================================
    # WEB DASHBOARD
    # ========================================================

    if args.web:

        from leadhunter.web.app import run_server

        print()
        print("=" * 90)
        print(
            f"⚡ Launching LeadHunter AI Web Control Dashboard "
            f"at http://localhost:{args.port}"
        )
        print("=" * 90)
        print()

        run_server(
            port=args.port
        )

        return

    # ========================================================
    # FOLLOW-UP ENGINE
    # ========================================================

    if args.followups:

        print()
        print("=" * 90)
        print(
            "LEADHUNTER AI — EXECUTING FOLLOW-UP SEQUENCE ENGINE"
        )
        print("=" * 90)

        engine = FollowupEngine()

        results = engine.check_and_stage_followups(
            city=args.city,
            limit=args.limit,
        )

        print()
        print("=" * 90)
        print(
            "LEADS DUE FOR FOLLOW-UP & STAGED MESSAGES"
        )
        print("=" * 90)

        if not results:

            print(
                "No contacted leads currently due for follow-up."
            )

            return

        for result in results:

            print()
            print("-" * 90)

            print(
                f"Lead ID {result['lead_id']} | "
                f"{result['name']} "
                f"({result['city']}) | "
                f"Staged: Follow-up #{result['followup_number']}"
            )

            print(
                f"Demo URL: {result['demo_url']}"
            )

            print(
                f"Approval Queue Status: "
                f"[{result['status']}]"
            )

            print("-" * 90)

            print(
                "📧 FOLLOW-UP EMAIL PREVIEW:"
            )

            print(
                f"Subject: {result['email_subject']}"
            )

            print()
            print(
                result['email_message']
            )

            print()
            print(
                "📱 FOLLOW-UP WHATSAPP PREVIEW:"
            )

            print(
                result['whatsapp_message']
            )

        return

    # ========================================================
    # PIPELINE START
    # ========================================================

    print()
    print("=" * 90)
    print("                    LEADHUNTER AI")
    print("                 AUTOMATED LEAD PIPELINE")
    print("=" * 90)

    print()
    print(
        f"City:       {args.city or 'Configured leads'}"
    )

    print(
        f"Category:   {args.category or 'Existing / configured leads'}"
    )

    print(
        f"Limit:      {args.limit}"
    )

    print(
        f"Service:    {args.service}"
    )

    print(
        f"Mode:       {'FULL PIPELINE' if args.all else 'SELECTED STAGES'}"
    )

    print("=" * 90)

    # ========================================================
    # STAGE 1 — DISCOVERY
    # ========================================================

    if args.discover or args.all:

        print()
        print("=" * 90)
        print(
            f"--- STAGE 1: DISCOVERY ---"
        )
        print(
            f"Searching: {args.category} in {args.city}"
        )
        print("=" * 90)

        try:

            result = search_serpapi_google_maps(
                city=args.city,
                business_type=args.category,
                max_results=args.limit,
            )

            print()
            print(
                "✓ Discovery completed."
            )

            if result is not None:
                print(
                    f"Discovery result: {result}"
                )

        except Exception as exc:

            print()
            print(
                f"✗ Discovery failed: {exc}"
            )

            if args.all:
                raise

    # ========================================================
    # STAGE 2 — DEDUPLICATION
    # ========================================================

    if args.dedup or args.all:

        print()
        print("=" * 90)
        print(
            "--- STAGE 2: NORMALIZATION & DEDUPLICATION ---"
        )
        print("=" * 90)

        try:

            result = process_leads(
                city=args.city
            )

            print()
            print(
                "✓ Normalization and deduplication completed."
            )

            if result is not None:
                print(
                    f"Processing result: {result}"
                )

        except Exception as exc:

            print()
            print(
                f"✗ Deduplication failed: {exc}"
            )

            if args.all:
                raise

    # ========================================================
    # STAGE 3 — WEBSITE VERIFICATION
    # ========================================================

    if args.verify or args.all:

        print()
        print("=" * 90)
        print(
            "--- STAGE 3: WEBSITE VERIFICATION ---"
        )
        print("=" * 90)

        try:

            result = verify_leads_batch(
                city=args.city,
                limit=args.limit,
            )

            print()
            print(
                "✓ Website verification completed."
            )

            if result is not None:
                print(
                    f"Verification result: {result}"
                )

        except Exception as exc:

            print()
            print(
                f"✗ Website verification failed: {exc}"
            )

            if args.all:
                raise

    # ========================================================
    # STAGE 4 — SCORING
    # ========================================================

    if args.score or args.all:

        print()
        print("=" * 90)
        print(
            "--- STAGE 4: SCORING & QUALIFICATION ---"
        )
        print("=" * 90)

        try:

            result = score_and_qualify_leads(
                city=args.city,
                limit=args.limit,
                service=args.service,
            )

            print()
            print(
                "✓ Lead scoring completed."
            )

            if result is not None:
                print(
                    f"Scoring result: {result}"
                )

        except Exception as exc:

            print()
            print(
                f"✗ Lead scoring failed: {exc}"
            )

            if args.all:
                raise

    # ========================================================
    # STAGE 5 — AI PERSONALIZATION
    # ========================================================

    if args.personalize or args.all:

        print()
        print("=" * 90)
        print(
            "--- STAGE 5: AI PERSONALIZATION ---"
        )
        print(
            "Provider: Groq"
        )
        print(
            "Model:    openai/gpt-oss-20b"
        )
        print("=" * 90)

        try:

            from leadhunter.ai.personalizer import (
                personalize_qualified_leads
            )

            result = personalize_qualified_leads(
                city=args.city,
                limit=args.limit,
            )

            print()
            print(
                "✓ AI personalization completed."
            )

            if result is not None:
                print(
                    f"Personalization result: {result}"
                )

        except Exception as exc:

            print()
            print(
                f"✗ AI personalization failed: {exc}"
            )

            if args.all:
                raise

    # ========================================================
    # STAGE 6 — DEMO GENERATION
    # ========================================================

    if args.demos or args.all:

        print()
        print("=" * 90)
        print(
            "--- STAGE 6: DEMO URL GENERATION & VERIFICATION ---"
        )
        print("=" * 90)

        try:

            result = process_and_generate_demo_urls(
                city=args.city,
                limit=args.limit,
            )

            print()
            print(
                "✓ Demo generation completed."
            )

            if result is not None:
                print(
                    f"Demo result: {result}"
                )

        except Exception as exc:

            print()
            print(
                f"✗ Demo generation failed: {exc}"
            )

            if args.all:
                raise

    # ========================================================
    # STAGE 7 — APPROVAL
    # ========================================================

    if args.approve or args.all:

        print()
        print("=" * 90)
        print(
            "--- STAGE 7: HUMAN APPROVAL QUEUE ---"
        )
        print("=" * 90)

        try:

            process_approval_queue(
                city=args.city,
                limit=args.limit,
            )

            viewer = ApprovalViewer()

            viewer.review_interactive(
                city=args.city
            )

        except Exception as exc:

            print()
            print(
                f"✗ Approval stage failed: {exc}"
            )

            if args.all:
                raise

    # ========================================================
    # STAGE 8 — OUTREACH
    # ========================================================

    if args.outreach or args.all:

        print()
        print("=" * 90)
        print(
            "--- STAGE 8: OUTREACH DISPATCH ---"
        )
        print(
            f"DRY_RUN={is_dry_run()}"
        )
        print("=" * 90)

        try:

            wa_sender = WhatsAppSender()

            wa_sender.process_approved_whatsapp(
                city=args.city,
                limit=args.limit,
            )

            email_sender = EmailSender()

            email_sender.process_approved_emails(
                city=args.city,
                limit=args.limit,
            )

            print()
            print(
                "✓ Outreach dispatch completed."
            )

        except Exception as exc:

            print()
            print(
                f"✗ Outreach failed: {exc}"
            )

            if args.all:
                raise

    # ========================================================
    # STAGE 9 — GOOGLE SHEETS SYNC
    # ========================================================

    if args.sync or args.all:

        print()
        print("=" * 90)
        print(
            "--- STAGE 9: GOOGLE SHEETS & LOCAL MIRROR SYNC ---"
        )
        print("=" * 90)

        try:

            result = sync_leads(
                city=args.city
            )

            print()
            print(
                "✓ Google Sheets synchronization completed."
            )

            if result is not None:
                print(
                    f"Sync result: {result}"
                )

        except Exception as exc:

            print()
            print(
                f"✗ Synchronization failed: {exc}"
            )

            if args.all:
                raise

    # ========================================================
    # COMPLETE
    # ========================================================

    print()
    print("=" * 90)
    print(
        "                 LEADHUNTER AI COMPLETED"
    )
    print("=" * 90)
    print()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()