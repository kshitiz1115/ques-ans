
"""Gemini API integration."""

from __future__ import annotations

import logging
from typing import Literal, TypedDict

from google import genai
from google.genai import errors, types

from app.config.settings import Settings
from app.prompts.qa_prompt import SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class ConversationMessage(TypedDict):
    """A message from the conversation history."""

    role: Literal["user", "assistant"]
    content: str


class GeminiServiceError(RuntimeError):
    """A safe, user-displayable error from the Gemini service."""


class GeminiQAService:
    """Generate answers with Google Gemini."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client = genai.Client(api_key=settings.api_key)

    def generate_answer(
        self, messages: list[ConversationMessage]
    ) -> str:
        """Generate an answer using conversation history."""
        if not messages:
            raise ValueError("At least one conversation message is required.")

        contents = [
            {
                "role": "user" if message["role"] == "user" else "model",
                "parts": [{"text": message["content"]}],
            }
            for message in messages
        ]

        try:
            response = self._client.models.generate_content(
                model=self._settings.model,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=self._settings.temperature,
                ),
            )
        except errors.APIError as error:
            logger.error(
                "Gemini request failed (HTTP %s).",
                getattr(error, "code", "unknown"),
            )
            raise GeminiServiceError(
                "The answer could not be generated. Check your Gemini "
                "API key, model access, quota and billing, then try again."
            ) from None

        answer = response.text
        if not answer or not answer.strip():
            logger.warning("Gemini returned an empty response.")
            raise GeminiServiceError(
                "The model returned an empty response. Please try again."
            )

        return answer.strip()
