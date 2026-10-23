"""Tests for environment-backed configuration."""

import pytest

from app.config.settings import (
    DEFAULT_MODEL,
    DEFAULT_TEMPERATURE,
    ConfigurationError,
    load_settings,
)


def test_load_settings_uses_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("app.config.settings.load_dotenv", lambda **kwargs: False)
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.delenv("GEMINI_MODEL", raising=False)
    monkeypatch.delenv("TEMPERATURE", raising=False)

    settings = load_settings()

    assert settings.api_key == "test-key"
    assert settings.model == DEFAULT_MODEL
    assert settings.temperature == DEFAULT_TEMPERATURE
    assert "test-key" not in repr(settings)


def test_load_settings_reads_configured_values(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("app.config.settings.load_dotenv", lambda **kwargs: False)
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setenv("GEMINI_MODEL", "custom-model")
    monkeypatch.setenv("TEMPERATURE", "0.7")

    settings = load_settings()

    assert settings.model == "custom-model"
    assert settings.temperature == 0.7


def test_load_settings_requires_api_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("app.config.settings.load_dotenv", lambda **kwargs: False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    with pytest.raises(ConfigurationError, match=r"(?i)\.env file"):
        load_settings()


@pytest.mark.parametrize("temperature", ["not-a-number", "-0.1", "2.1"])
def test_load_settings_rejects_invalid_temperature(
    monkeypatch: pytest.MonkeyPatch,
    temperature: str,
) -> None:
    monkeypatch.setattr("app.config.settings.load_dotenv", lambda **kwargs: False)
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setenv("TEMPERATURE", temperature)

    with pytest.raises(ConfigurationError):
        load_settings()
