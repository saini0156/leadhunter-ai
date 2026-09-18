"""
LeadHunter AI - Unified LLM Client

Supported providers:
- Groq
- Gemini
- OpenAI
- OpenRouter

Recommended:
    Groq + openai/gpt-oss-20b

Notes:
- Groq uses the native Groq SDK.
- Do NOT pass GROQ_BASE_URL to the native Groq client.
- GPT-OSS is a reasoning model, so completion limits must be large enough.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional


# ============================================================
# ERROR
# ============================================================

class LLMError(Exception):
    """Raised when an LLM request fails."""


# ============================================================
# SETTINGS
# ============================================================

@dataclass
class LLMSettings:
    provider: str
    model: str
    api_key: str
    base_url: Optional[str] = None


# ============================================================
# LLM CLIENT
# ============================================================

class LLMClient:
    """
    Unified LLM client.

    Example:

        client = LLMClient(
            provider="groq",
            model="openai/gpt-oss-20b",
        )

        response = client.generate_text(
            "You are an assistant.",
            "Say OK",
            1000,
        )
    """

    def __init__(
        self,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        env_provider = (provider or os.getenv("LLM_PROVIDER") or "").strip().lower()
        if not env_provider:
            if os.getenv("GROQ_API_KEY"):
                env_provider = "groq"
            elif os.getenv("GEMINI_API_KEY"):
                env_provider = "gemini"
            elif os.getenv("OPENAI_API_KEY"):
                env_provider = "openai"
            else:
                env_provider = "groq"

        self.provider = env_provider

        default_model = "gemini-2.5-flash" if self.provider == "gemini" else "openai/gpt-oss-20b"
        self.model = (
            model
            or os.getenv("LLM_MODEL")
            or default_model
        ).strip()

        self.api_key = (
            api_key
            or self._get_api_key()
        )

        self.base_url = (
            base_url
            or self._get_base_url()
        )

        if not self.api_key:
            raise LLMError(
                f"No API key found for provider '{self.provider}'."
            )

        self.settings = LLMSettings(
            provider=self.provider,
            model=self.model,
            api_key=self.api_key,
            base_url=self.base_url,
        )

    # ========================================================
    # API KEY
    # ========================================================

    def _get_api_key(self) -> str:
        """Return API key for selected provider."""

        if self.provider == "groq":
            return os.getenv(
                "GROQ_API_KEY",
                "",
            ).strip()

        if self.provider == "gemini":
            return os.getenv(
                "GEMINI_API_KEY",
                "",
            ).strip()

        if self.provider == "openai":
            return os.getenv(
                "OPENAI_API_KEY",
                "",
            ).strip()

        if self.provider == "openrouter":
            return os.getenv(
                "OPENROUTER_API_KEY",
                "",
            ).strip()

        raise LLMError(
            f"Unsupported LLM provider: {self.provider}"
        )

    # ========================================================
    # BASE URL
    # ========================================================

    def _get_base_url(self) -> Optional[str]:
        """
        Return base URL.

        Groq intentionally returns None because the native
        Groq SDK already knows its API endpoint.
        """

        if self.provider == "groq":
            return None

        if self.provider == "gemini":
            return None

        if self.provider == "openai":
            value = os.getenv(
                "OPENAI_BASE_URL",
                "",
            ).strip()

            return value or None

        if self.provider == "openrouter":
            return os.getenv(
                "OPENROUTER_BASE_URL",
                "https://openrouter.ai/api/v1",
            ).strip()

        return None

    # ========================================================
    # MAIN GENERATE METHOD
    # ========================================================

    def generate_text(
        self,
        system_prompt: str,
        user_prompt: str,
        max_output_tokens: int = 1000,
    ) -> str:
        """
        Generate text using configured provider.
        """

        system_prompt = system_prompt or ""

        if not user_prompt:
            raise LLMError(
                "user_prompt cannot be empty."
            )

        try:
            max_output_tokens = int(
                max_output_tokens
            )
        except (TypeError, ValueError):
            max_output_tokens = 1000

        if max_output_tokens <= 0:
            max_output_tokens = 1000

        provider = self.provider.lower().strip()

        # ----------------------------------------------------
        # GROQ
        # ----------------------------------------------------

        if provider == "groq":
            return self._generate_groq(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                max_output_tokens=max_output_tokens,
            )

        # ----------------------------------------------------
        # GEMINI
        # ----------------------------------------------------

        if provider == "gemini":
            return self._generate_gemini(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                max_output_tokens=max_output_tokens,
            )

        # ----------------------------------------------------
        # OPENAI
        # ----------------------------------------------------

        if provider == "openai":
            return self._generate_openai(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                max_output_tokens=max_output_tokens,
            )

        # ----------------------------------------------------
        # OPENROUTER
        # ----------------------------------------------------

        if provider == "openrouter":
            return self._generate_openrouter(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                max_output_tokens=max_output_tokens,
            )

        raise LLMError(
            f"Unsupported LLM provider: {provider}"
        )

    def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        max_output_tokens: int = 1000,
    ) -> Any:
        """
        Generate text and parse as JSON object/array.
        """
        import json
        import re

        raw = self.generate_text(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_output_tokens=max_output_tokens,
        )
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\n?", "", cleaned, flags=re.IGNORECASE)
            cleaned = re.sub(r"\n?```$", "", cleaned)
            cleaned = cleaned.strip()

        try:
            return json.loads(cleaned)
        except Exception as exc:
            raise LLMError(
                f"Failed to parse LLM JSON output: {exc}\nRaw output: {raw}"
            ) from exc

    # ========================================================
    # GROQ CLIENT
    # ========================================================

    def _create_groq_client(self):
        """
        Create native Groq client.

        IMPORTANT:
        Do not provide base_url.

        Native Groq SDK automatically uses:

            https://api.groq.com/openai/v1

        Providing the same URL manually can produce:

            /openai/v1/openai/v1/...
        """

        try:
            from groq import Groq

        except ImportError as exc:
            raise LLMError(
                "Groq SDK is not installed.\n\n"
                "Run:\n"
                "pip install -U groq"
            ) from exc

        try:
            return Groq(
                api_key=self.settings.api_key
            )

        except Exception as exc:
            raise LLMError(
                f"Could not initialize Groq client: {exc}"
            ) from exc

    # ========================================================
    # GROQ GENERATION
    # ========================================================

    def _generate_groq(
        self,
        system_prompt: str,
        user_prompt: str,
        max_output_tokens: int,
    ) -> str:
        """
        Generate response using Groq.

        GPT-OSS is a reasoning model. A small token limit can
        cause the model to spend the entire completion budget
        on reasoning and return empty content.

        Therefore we enforce a minimum completion budget.
        """

        client = self._create_groq_client()

        # GPT-OSS needs enough tokens for reasoning + answer.
        completion_limit = max(
            int(max_output_tokens),
            1000,
        )

        try:
            completion = client.chat.completions.create(
                model=self.settings.model,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": user_prompt,
                    },
                ],
                max_completion_tokens=completion_limit,
                include_reasoning=False,
            )

        except Exception as exc:
            raise LLMError(
                f"Groq request failed: {exc}"
            ) from exc

        # ----------------------------------------------------
        # RESPONSE VALIDATION
        # ----------------------------------------------------

        try:
            choices = getattr(
                completion,
                "choices",
                None,
            )

            if not choices:
                raise LLMError(
                    "Groq returned no choices."
                )

            choice = choices[0]

            message = getattr(
                choice,
                "message",
                None,
            )

            if message is None:
                raise LLMError(
                    "Groq returned no message."
                )

            text = getattr(
                message,
                "content",
                None,
            )

            # Normal response
            if text:
                return str(text).strip()

            # ------------------------------------------------
            # DIAGNOSTIC INFORMATION
            # ------------------------------------------------

            finish_reason = getattr(
                choice,
                "finish_reason",
                None,
            )

            reasoning_tokens = None

            usage = getattr(
                completion,
                "usage",
                None,
            )

            if usage:

                details = getattr(
                    usage,
                    "completion_tokens_details",
                    None,
                )

                if details:
                    reasoning_tokens = getattr(
                        details,
                        "reasoning_tokens",
                        None,
                    )

            raise LLMError(
                "Groq returned an empty response.\n"
                f"Finish reason: {finish_reason}\n"
                f"Reasoning tokens: {reasoning_tokens}\n"
                f"Completion limit: {completion_limit}"
            )

        except LLMError:
            raise

        except Exception as exc:
            raise LLMError(
                f"Could not read Groq response: {exc}"
            ) from exc

    # ========================================================
    # GEMINI CLIENT
    # ========================================================

    def _create_gemini_client(self):
        """Create Gemini client."""

        try:
            from google import genai

        except ImportError as exc:
            raise LLMError(
                "Google GenAI SDK is not installed.\n\n"
                "Run:\n"
                "pip install -U google-genai"
            ) from exc

        try:
            return genai.Client(
                api_key=self.settings.api_key
            )

        except Exception as exc:
            raise LLMError(
                f"Could not initialize Gemini client: {exc}"
            ) from exc

    # ========================================================
    # GEMINI GENERATION
    # ========================================================

    def _generate_gemini(
        self,
        system_prompt: str,
        user_prompt: str,
        max_output_tokens: int,
    ) -> str:
        """Generate response using Gemini."""

        client = self._create_gemini_client()

        prompt = (
            f"{system_prompt}\n\n"
            f"USER REQUEST:\n"
            f"{user_prompt}"
        )

        try:
            response = client.models.generate_content(
                model=self.settings.model,
                contents=prompt,
                config={
                    "max_output_tokens": max_output_tokens,
                },
            )

        except Exception as exc:
            raise LLMError(
                f"Gemini request failed: {exc}"
            ) from exc

        try:
            text = getattr(
                response,
                "text",
                None,
            )

            if text:
                return str(text).strip()

            candidates = getattr(
                response,
                "candidates",
                None,
            )

            if not candidates:
                raise LLMError(
                    "Gemini returned no candidates."
                )

            collected = []

            for candidate in candidates:

                content = getattr(
                    candidate,
                    "content",
                    None,
                )

                if not content:
                    continue

                parts = getattr(
                    content,
                    "parts",
                    None,
                )

                if not parts:
                    continue

                for part in parts:

                    part_text = getattr(
                        part,
                        "text",
                        None,
                    )

                    if part_text:
                        collected.append(
                            str(part_text)
                        )

            if collected:
                return "\n".join(
                    collected
                ).strip()

            raise LLMError(
                "Gemini returned an empty response."
            )

        except LLMError:
            raise

        except Exception as exc:
            raise LLMError(
                f"Could not read Gemini response: {exc}"
            ) from exc

    # ========================================================
    # OPENAI CLIENT
    # ========================================================

    def _create_openai_client(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        """Create OpenAI-compatible client."""

        try:
            from openai import OpenAI

        except ImportError as exc:
            raise LLMError(
                "OpenAI SDK is not installed.\n\n"
                "Run:\n"
                "pip install -U openai"
            ) from exc

        kwargs = {
            "api_key": (
                api_key
                or self.settings.api_key
            )
        }

        if base_url:
            kwargs["base_url"] = base_url

        try:
            return OpenAI(**kwargs)

        except Exception as exc:
            raise LLMError(
                f"Could not initialize OpenAI client: {exc}"
            ) from exc

    # ========================================================
    # OPENAI GENERATION
    # ========================================================

    def _generate_openai(
        self,
        system_prompt: str,
        user_prompt: str,
        max_output_tokens: int,
    ) -> str:
        """Generate response using OpenAI."""

        client = self._create_openai_client(
            api_key=self.settings.api_key,
            base_url=self.settings.base_url,
        )

        try:
            completion = client.chat.completions.create(
                model=self.settings.model,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": user_prompt,
                    },
                ],
                max_tokens=max_output_tokens,
            )

        except Exception as exc:
            raise LLMError(
                f"OpenAI request failed: {exc}"
            ) from exc

        try:
            choices = completion.choices

            if not choices:
                raise LLMError(
                    "OpenAI returned no choices."
                )

            text = choices[0].message.content

            if text:
                return str(text).strip()

            raise LLMError(
                "OpenAI returned an empty response."
            )

        except LLMError:
            raise

        except Exception as exc:
            raise LLMError(
                f"Could not read OpenAI response: {exc}"
            ) from exc

    # ========================================================
    # OPENROUTER GENERATION
    # ========================================================

    def _generate_openrouter(
        self,
        system_prompt: str,
        user_prompt: str,
        max_output_tokens: int,
    ) -> str:
        """Generate response using OpenRouter."""

        base_url = (
            self.settings.base_url
            or "https://openrouter.ai/api/v1"
        )

        client = self._create_openai_client(
            api_key=self.settings.api_key,
            base_url=base_url,
        )

        try:
            completion = client.chat.completions.create(
                model=self.settings.model,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": user_prompt,
                    },
                ],
                max_tokens=max_output_tokens,
            )

        except Exception as exc:
            raise LLMError(
                f"OpenRouter request failed: {exc}"
            ) from exc

        try:
            choices = completion.choices

            if not choices:
                raise LLMError(
                    "OpenRouter returned no choices."
                )

            text = choices[0].message.content

            if text:
                return str(text).strip()

            raise LLMError(
                "OpenRouter returned an empty response."
            )

        except LLMError:
            raise

        except Exception as exc:
            raise LLMError(
                f"Could not read OpenRouter response: {exc}"
            ) from exc


# ============================================================
# HELPER
# ============================================================

def get_llm_client() -> LLMClient:
    """
    Create an LLM client from .env configuration.
    """

    return LLMClient(
        provider=os.getenv(
            "LLM_PROVIDER",
            "groq",
        ),
        model=os.getenv(
            "LLM_MODEL",
            "openai/gpt-oss-20b",
        ),
    )