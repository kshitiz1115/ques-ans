
"""Environment-backed application settings."""

import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

DEFAULT_MODEL = "gemini-3.5-flash-lite"
DEFAULT_TEMPERATURE = 0.2


class ConfigurationError(ValueError):
    """Raised when required or invalid configuration is found."""


@dataclass(frozen=True, slots=True)
class Settings:
    """Validated settings used by the application."""

    api_key: str = field(repr=False)
    model: str = DEFAULT_MODEL
    temperature: float = DEFAULT_TEMPERATURE


def load_settings() -> Settings:
    """Load and validate Gemini configuration."""
    load_dotenv(override=True)

    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise ConfigurationError(
            "GEMINI_API_KEY is missing. Add your Gemini API key to the .env file."
        )

    model = os.getenv("GEMINI_MODEL", DEFAULT_MODEL).strip()
    if not model:
        raise ConfigurationError("GEMINI_MODEL cannot be empty.")

    try:
        temperature = float(
            os.getenv("TEMPERATURE", str(DEFAULT_TEMPERATURE))
        )
    except ValueError as error:
        raise ConfigurationError(
            "TEMPERATURE must be a number between 0 and 2."
        ) from error

    if not 0 <= temperature <= 2:
        raise ConfigurationError("TEMPERATURE must be between 0 and 2.")

    return Settings(
        api_key=api_key,
        model=model,
        temperature=temperature,
    )
