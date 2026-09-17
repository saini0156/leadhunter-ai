"""
LeadHunter AI - Outreach Personalizer

Generates personalized:
- cold email subject
- cold email body
- WhatsApp message

LLM provider is controlled through:
    LLM_PROVIDER
    LLM_MODEL
    GEMINI_API_KEY

Current recommended provider:
    Gemini

The module is compatible with the existing
LeadHunter Database API.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
from typing import Any, Dict, Optional

from leadhunter.ai.llm_client import LLMClient, LLMError
from leadhunter.db import Database


log = logging.getLogger("leadhunter.personalizer")


# ---------------------------------------------------------------------------
# CONSTANTS
# ---------------------------------------------------------------------------

# IMPORTANT:
# Do NOT put {{DEMO_URL}} directly inside the Gemini JSON prompt.
# Curly braces inside generated JSON can sometimes confuse the model.
#
# We use a safe placeholder and convert it back after parsing.
DEMO_PLACEHOLDER = "DEMO_URL_PLACEHOLDER"


# ---------------------------------------------------------------------------
# SYSTEM PROMPT
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """
You are an expert B2B local-business outreach copywriter.

Generate short, natural outreach for the supplied business.

Return ONLY one valid JSON object with exactly these keys:

{
  "email_subject": "short subject",
  "email_message": "short email",
  "whatsapp_message": "short WhatsApp message"
}

Rules:
- Valid JSON only.
- Use double quotes for JSON strings.
- Never use markdown.
- Never use code fences.
- Never add explanations outside JSON.
- Never invent facts.
- Use only supplied lead information.
- Email must be under 120 words.
- WhatsApp must be under 60 words.
- Mention the business name naturally.
- Mention the city naturally.
- Keep the tone professional and human.
- Do not sound like mass spam.
- Do not make fake promises.
- Do not claim an audit was performed.
- Use DEMO_URL_PLACEHOLDER exactly where the demo link belongs.
"""


# ---------------------------------------------------------------------------
# SAFE HELPERS
# ---------------------------------------------------------------------------

def _safe_text(value: Any, default: str = "") -> str:
    """Convert a value safely to a clean string."""

    if value is None:
        return default

    text = str(value).strip()

    if text.lower() in {"none", "null", "nan"}:
        return default

    return text


def _business_name(lead: Any) -> str:
    return _safe_text(
        getattr(lead, "name", None),
        "your business",
    )


def _city(lead: Any) -> str:
    return _safe_text(
        getattr(lead, "city", None),
        "",
    )


def _category(lead: Any) -> str:
    return _safe_text(
        getattr(lead, "category", None),
        "local business",
    )


def _website(lead: Any) -> str:
    return _safe_text(
        getattr(lead, "website", None),
        "",
    )


def _website_status(lead: Any) -> str:
    return _safe_text(
        getattr(lead, "website_status", None),
        "",
    )


def _rating(lead: Any) -> str:
    value = getattr(lead, "rating", None)

    if value is None:
        return ""

    try:
        return f"{float(value):.1f}"
    except (TypeError, ValueError):
        return _safe_text(value)


def _reviews_count(lead: Any) -> str:
    value = getattr(lead, "reviews_count", None)

    if value is None:
        return ""

    try:
        return str(int(value))
    except (TypeError, ValueError):
        return _safe_text(value)


def _lead_tier(lead: Any) -> str:
    return _safe_text(
        getattr(lead, "lead_tier", None),
        "",
    )


def _score(lead: Any) -> str:
    value = getattr(lead, "score", None)

    if value is None:
        return ""

    try:
        return f"{float(value):.0f}"
    except (TypeError, ValueError):
        return _safe_text(value)


# ---------------------------------------------------------------------------
# PROMPT BUILDER
# ---------------------------------------------------------------------------

def build_lead_prompt(lead: Any) -> str:
    """
    Build a compact Gemini prompt.

    The prompt intentionally avoids curly-brace demo placeholders.
    """

    name = _business_name(lead)
    city = _city(lead)
    category = _category(lead)
    website = _website(lead)
    website_status = _website_status(lead)
    rating = _rating(lead)
    reviews = _reviews_count(lead)
    tier = _lead_tier(lead)
    score = _score(lead)

    return f"""
Create outreach for this local business.

Business: {name}
Category: {category}
City: {city}
Website: {website or "not provided"}
Website status: {website_status or "unknown"}
Rating: {rating or "not provided"}
Reviews: {reviews or "not provided"}
Lead tier: {tier or "unknown"}
Lead score: {score or "unknown"}

Offer:
- professional website improvement/development
- local SEO
- more qualified local enquiries

Requirements:
- Personalize using only supplied information.
- Keep email under 120 words.
- Keep WhatsApp under 60 words.
- Include DEMO_URL_PLACEHOLDER in both messages.
- Return ONLY valid JSON.
""".strip()


def build_compact_retry_prompt(lead: Any) -> str:
    """
    Very small retry prompt.

    This is deliberately simple to reduce malformed/truncated JSON.
    """

    name = _business_name(lead)
    city = _city(lead)
    category = _category(lead)

    return f"""
Return ONLY valid JSON.

Business: {name}
City: {city}
Category: {category}

Required keys:
email_subject
email_message
whatsapp_message

Requirements:
- Email under 80 words.
- WhatsApp under 45 words.
- Include DEMO_URL_PLACEHOLDER in both.
- No markdown.
- No explanation.
- No invented facts.
""".strip()


# ---------------------------------------------------------------------------
# JSON PARSING
# ---------------------------------------------------------------------------

def _extract_balanced_json(text: str) -> Optional[str]:
    """
    Extract the first balanced JSON object.

    Handles surrounding text and markdown fences.
    """

    if not text:
        return None

    start = text.find("{")

    if start == -1:
        return None

    depth = 0
    in_string = False
    escaped = False

    for index in range(start, len(text)):

        char = text[index]

        if in_string:

            if escaped:
                escaped = False

            elif char == "\\":
                escaped = True

            elif char == '"':
                in_string = False

            continue

        if char == '"':
            in_string = True

        elif char == "{":
            depth += 1

        elif char == "}":
            depth -= 1

            if depth == 0:
                return text[start:index + 1]

    return None


def _clean_json_text(text: str) -> str:
    """Clean common Gemini JSON wrappers."""

    text = _safe_text(text)

    if not text:
        return ""

    # Remove markdown fences.
    text = text.replace("```json", "")
    text = text.replace("```JSON", "")
    text = text.replace("```", "")

    return text.strip()


def _replace_demo_placeholder(value: str) -> str:
    """
    Convert the safe LLM placeholder into the LeadHunter
    demo placeholder used by the rest of the pipeline.
    """

    return (
        value
        .replace(DEMO_PLACEHOLDER, "{{DEMO_URL}}")
        .replace("{DEMO_URL}", "{{DEMO_URL}}")
    )


def _validate_message_lengths(
    email_message: str,
    whatsapp_message: str,
) -> None:
    """
    Basic safety validation.

    We don't reject slightly over-limit content aggressively,
    but we reject obviously huge generations.
    """

    email_words = len(email_message.split())
    whatsapp_words = len(whatsapp_message.split())

    if email_words > 150:
        raise ValueError(
            f"Email too long: {email_words} words"
        )

    if whatsapp_words > 90:
        raise ValueError(
            f"WhatsApp too long: {whatsapp_words} words"
        )


def parse_llm_json(text: str) -> Dict[str, str]:
    """
    Parse and validate Gemini outreach JSON.

    Raises ValueError when valid outreach cannot be obtained.
    """

    cleaned = _clean_json_text(text)

    if not cleaned:
        raise ValueError(
            "Gemini returned an empty response."
        )

    candidates = []

    # Candidate 1:
    # Entire response.
    candidates.append(cleaned)

    # Candidate 2:
    # Balanced JSON object extracted from response.
    extracted = _extract_balanced_json(cleaned)

    if extracted and extracted not in candidates:
        candidates.append(extracted)

    last_error: Optional[Exception] = None

    for candidate in candidates:

        try:

            data = json.loads(candidate)

            if not isinstance(data, dict):
                continue

            email_subject = _safe_text(
                data.get("email_subject")
            )

            email_message = _safe_text(
                data.get("email_message")
            )

            whatsapp_message = _safe_text(
                data.get("whatsapp_message")
            )

            if not email_subject:
                continue

            if not email_message:
                continue

            if not whatsapp_message:
                continue

            # Convert placeholder after JSON parsing.
            email_subject = _replace_demo_placeholder(
                email_subject
            )

            email_message = _replace_demo_placeholder(
                email_message
            )

            whatsapp_message = _replace_demo_placeholder(
                whatsapp_message
            )

            _validate_message_lengths(
                email_message,
                whatsapp_message,
            )

            return {
                "email_subject": email_subject.strip(),
                "email_message": email_message.strip(),
                "whatsapp_message": whatsapp_message.strip(),
            }

        except (
            json.JSONDecodeError,
            TypeError,
            ValueError,
        ) as exc:

            last_error = exc

    if last_error:

        raise ValueError(
            "Could not parse valid outreach JSON: "
            f"{last_error}"
        ) from last_error

    raise ValueError(
        "Could not parse valid outreach JSON."
    )


# ---------------------------------------------------------------------------
# TEMPLATE FALLBACK
# ---------------------------------------------------------------------------

def _rating_sentence(lead: Any) -> str:
    rating = _rating(lead)
    reviews = _reviews_count(lead)

    if rating and reviews:
        return (
            f"Your business has a {rating}-star rating "
            f"across {reviews} reviews."
        )

    if rating:
        return (
            f"Your business currently shows a "
            f"{rating}-star rating."
        )

    if reviews:
        return (
            f"Your business currently shows "
            f"{reviews} reviews."
        )

    return ""


def generate_template_messages(
    lead: Any,
) -> Dict[str, str]:
    """
    Reliable deterministic fallback.
    """

    name = _business_name(lead)
    city = _city(lead)
    category = _category(lead)

    rating_sentence = _rating_sentence(lead)

    if rating_sentence:
        reputation_line = f" {rating_sentence}"
    else:
        reputation_line = ""

    location = f" in {city}" if city else ""

    email_subject = (
        f"Website & SEO opportunity for {name}"
    )

    email_message = (
        f"Hi {name} team,\n\n"
        f"I came across {name}{location} and noticed "
        f"an opportunity to strengthen its online presence."
        f"{reputation_line}\n\n"
        f"We help {category.lower()} businesses improve "
        f"their website experience and local SEO to "
        f"generate more qualified enquiries.\n\n"
        f"I prepared a demo concept for {name}:\n"
        f"{{{{DEMO_URL}}}}\n\n"
        f"If you'd like, I can show you the key improvements.\n\n"
        f"Best,\n"
        f"LeadHunter AI"
    )

    whatsapp_message = (
        f"Hi {name} team, I found {name}{location} "
        f"and put together a quick website/SEO demo concept:\n"
        f"{{{{DEMO_URL}}}}\n\n"
        f"It focuses on improving your online presence "
        f"and generating more local enquiries."
    )

    return {
        "email_subject": email_subject,
        "email_message": email_message,
        "whatsapp_message": whatsapp_message,
    }


# ---------------------------------------------------------------------------
# LLM CLIENT
# ---------------------------------------------------------------------------

def get_llm_client(
    config: Any = None,
) -> LLMClient:
    """
    Create the configured LLM client.
    """

    provider = os.getenv(
        "LLM_PROVIDER",
        "gemini",
    )

    model = os.getenv(
        "LLM_MODEL",
        "gemini-3.6-flash",
    )

    log.info(
        "LLM client configured: provider=%s, model=%s",
        provider,
        model,
    )

    return LLMClient(
        provider=provider,
        model=model,
    )


# ---------------------------------------------------------------------------
# LLM GENERATION
# ---------------------------------------------------------------------------

def _generate_with_llm(
    client: LLMClient,
    lead: Any,
) -> Dict[str, str]:
    """
    Generate outreach using Gemini.

    Flow:
        Attempt 1
        ↓
        Parse + validate
        ↓
        Compact retry if needed
        ↓
        Raise error
        ↓
        deterministic fallback handled by caller
    """

    # ---------------------------------------------------------------
    # ATTEMPT 1
    # ---------------------------------------------------------------

    prompt = build_lead_prompt(lead)

    try:

        raw_response = client.generate_json(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=prompt,
            max_output_tokens=700,
        )

        return parse_llm_json(
            raw_response
        )

    except (LLMError, ValueError) as first_error:

        log.warning(
            "First Gemini outreach attempt failed "
            "for Lead [%s]: %s",
            getattr(lead, "id", "?"),
            first_error,
        )

    # ---------------------------------------------------------------
    # ATTEMPT 2
    # ---------------------------------------------------------------

    retry_prompt = build_compact_retry_prompt(lead)

    try:

        raw_response = client.generate_json(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=retry_prompt,
            max_output_tokens=450,
        )

        return parse_llm_json(
            raw_response
        )

    except (LLMError, ValueError) as second_error:

        log.warning(
            "Compact Gemini retry failed "
            "for Lead [%s]: %s",
            getattr(lead, "id", "?"),
            second_error,
        )

        raise ValueError(
            "LLM outreach generation failed after retry: "
            f"{second_error}"
        ) from second_error


# ---------------------------------------------------------------------------
# SINGLE LEAD GENERATION
# ---------------------------------------------------------------------------

def generate_messages_for_lead(
    lead: Any,
    client: Optional[LLMClient] = None,
) -> Dict[str, str]:
    """
    Generate outreach for one lead.

    Uses configured LLM first.
    Falls back to deterministic templates.
    """

    if client is None:
        client = get_llm_client()

    try:

        messages = _generate_with_llm(
            client,
            lead,
        )

        # Final cleanup.
        for key in (
            "email_subject",
            "email_message",
            "whatsapp_message",
        ):
            messages[key] = (
                _safe_text(messages.get(key))
                .strip()
            )

        return messages

    except Exception as exc:

        log.warning(
            "Using template fallback for Lead [%s]: %s",
            getattr(lead, "id", "?"),
            exc,
        )

        return generate_template_messages(
            lead
        )


# ---------------------------------------------------------------------------
# PERSONALIZATION PIPELINE
# ---------------------------------------------------------------------------

def personalize_qualified_leads(
    city: Optional[str] = None,
    limit: int = 10,
    db: Optional[Database] = None,
    client: Optional[LLMClient] = None,
    delay_s: float = 0.0,
) -> Dict[str, int]:
    """
    Personalize QUALIFIED HOT/WARM leads.

    Uses the existing Database API:

        db.update_lead(lead_id, fields_dict)

    Then transitions:

        QUALIFIED -> PERSONALIZED
    """

    if db is None:
        db = Database()

    if client is None:
        client = get_llm_client()

    leads = db.get_resumable_leads(
        stage="personalizer",
        city=city,
        limit=limit,
    )

    log.info(
        "Starting AI personalization for %d "
        "QUALIFIED leads (limit=%d)...",
        len(leads),
        limit,
    )

    stats = {
        "found": len(leads),
        "personalized": 0,
        "failed": 0,
        "fallback": 0,
    }

    provider = os.getenv(
        "LLM_PROVIDER",
        "gemini",
    )

    model = os.getenv(
        "LLM_MODEL",
        "gemini-3.6-flash",
    )

    results_list = []

    for lead in leads:

        lead_id = int(lead.id)
        name = _business_name(lead)

        log.info(
            "Generating personalized outreach "
            "for Lead [ID %s]: '%s' (%s, %s)...",
            lead_id,
            name,
            _lead_tier(lead) or "UNKNOWN",
            _website_status(lead) or "UNKNOWN",
        )

        try:

            # -------------------------------------------------------
            # GENERATE
            # -------------------------------------------------------

            messages = generate_messages_for_lead(
                lead,
                client=client,
            )

            # -------------------------------------------------------
            # DETECT FALLBACK
            # -------------------------------------------------------

            fallback_messages = (
                generate_template_messages(
                    lead
                )
            )

            used_fallback = (
                messages["email_subject"]
                == fallback_messages["email_subject"]
            )

            if used_fallback:
                stats["fallback"] += 1

            # -------------------------------------------------------
            # FINAL MESSAGE VALIDATION
            # -------------------------------------------------------

            required_keys = (
                "email_subject",
                "email_message",
                "whatsapp_message",
            )

            for key in required_keys:

                if not _safe_text(
                    messages.get(key)
                ):
                    raise ValueError(
                        f"Generated message missing: {key}"
                    )

            # -------------------------------------------------------
            # DATABASE UPDATE
            # -------------------------------------------------------

            db.update_lead(
                lead_id,
                {
                    "personalized_message": messages[
                        "email_message"
                    ],
                    "email_subject": messages[
                        "email_subject"
                    ],
                    "email_message": messages[
                        "email_message"
                    ],
                    "whatsapp_message": messages[
                        "whatsapp_message"
                    ],
                },
            )

            # -------------------------------------------------------
            # TRANSITION
            # -------------------------------------------------------

            if used_fallback:

                event = (
                    "Generated outreach using deterministic "
                    f"template fallback after {provider} "
                    f"({model}) generation failure"
                )

            else:

                event = (
                    "Generated personalized cold email and "
                    f"WhatsApp messages via {provider} "
                    f"({model})"
                )

            db.transition(
                lead_id,
                "PERSONALIZED",
                stage="personalizer",
                event=event,
            )

            stats["personalized"] += 1

            results_list.append(
                {
                    "id": lead_id,
                    "name": name,
                    "status": "PERSONALIZED",
                    "email_subject": messages.get("email_subject", ""),
                    "email_message": messages.get("email_message", ""),
                    "whatsapp_message": messages.get("whatsapp_message", ""),
                }
            )

            log.info(
                "Lead [ID %s] '%s' -> PERSONALIZED",
                lead_id,
                name,
            )

        except Exception as exc:

            stats["failed"] += 1

            log.exception(
                "Personalization failed for "
                "Lead [ID %s] '%s'",
                lead_id,
                name,
            )

            # -------------------------------------------------------
            # MARK FAILED
            # -------------------------------------------------------

            try:

                error_payload = json.dumps(
                    {
                        "error": str(exc),
                        "retryable": True,
                    }
                )

                db.transition(
                    lead_id,
                    "FAILED",
                    stage="personalizer",
                    event=error_payload,
                    level="ERROR",
                )

            except Exception:

                log.exception(
                    "Could not mark Lead [ID %s] as FAILED",
                    lead_id,
                )

    log.info(
        "Personalization complete: "
        "found=%d personalized=%d fallback=%d failed=%d",
        stats["found"],
        stats["personalized"],
        stats["fallback"],
        stats["failed"],
    )

    class PersonalizedLeadsList(list):
        def __init__(self, items, stats_dict):
            super().__init__(items)
            self.stats = stats_dict

        def __getitem__(self, item):
            if isinstance(item, str):
                return self.stats[item]
            return super().__getitem__(item)

        def get(self, key, default=None):
            if isinstance(key, str):
                return self.stats.get(key, default)
            return default

    return PersonalizedLeadsList(results_list, stats)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:

    parser = argparse.ArgumentParser(
        description=(
            "Generate AI outreach for qualified "
            "LeadHunter leads."
        )
    )

    parser.add_argument(
        "--city",
        type=str,
        default=None,
        help="Only personalize leads from this city.",
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help=(
            "Maximum number of leads to personalize."
        ),
    )

    args = parser.parse_args()

    print(
        "\n=== Running AI Outreach Personalization "
        f"(city='{args.city}', limit={args.limit}) ==="
    )

    try:

        stats = personalize_qualified_leads(
            city=args.city,
            limit=args.limit,
        )

        print("\n=== Personalization Summary ===")
        print(f"Found:        {stats['found']}")
        print(f"Personalized: {stats['personalized']}")
        print(f"Fallback:     {stats['fallback']}")
        print(f"Failed:       {stats['failed']}")

        return 0

    except Exception as exc:

        print(
            "\nERROR: Personalization pipeline failed: "
            f"{exc}"
        )

        return 1


if __name__ == "__main__":
    raise SystemExit(main())