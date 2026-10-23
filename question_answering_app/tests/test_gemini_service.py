"""Tests for Gemini service initialization and response handling."""

from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from app.config.settings import Settings
from app.services.gemini_service import GeminiQAService, GeminiServiceError


def _response(text: str | None) -> SimpleNamespace:
    return SimpleNamespace(text=text)


def test_service_initializes_gemini_client(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = Mock()
    client_constructor = Mock(return_value=client)
    monkeypatch.setattr("app.services.gemini_service.genai.Client", client_constructor)

    GeminiQAService(Settings(api_key="test-key"))

    client_constructor.assert_called_once_with(api_key="test-key")


def test_generate_answer_sends_history_and_returns_text(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = Mock()
    client.models.generate_content.return_value = _response("  Hello there.  ")
    client_constructor = Mock(return_value=client)
    config = Mock()
    config_constructor = Mock(return_value=config)
    monkeypatch.setattr("app.services.gemini_service.genai.Client", client_constructor)
    monkeypatch.setattr(
        "app.services.gemini_service.types.GenerateContentConfig",
        config_constructor,
    )
    settings = Settings("test-key", "test-model", 0.4)
    service = GeminiQAService(settings)
    messages = [
        {"role": "user", "content": "Hi"},
        {"role": "assistant", "content": "Hello!"},
        {"role": "user", "content": "Can you clarify?"},
    ]

    answer = service.generate_answer(messages)

    assert answer == "Hello there."
    client.models.generate_content.assert_called_once_with(
        model="test-model",
        contents=[
            {"role": "user", "parts": [{"text": "Hi"}]},
            {"role": "model", "parts": [{"text": "Hello!"}]},
            {"role": "user", "parts": [{"text": "Can you clarify?"}]},
        ],
        config=config,
    )
    config_constructor.assert_called_once_with(
        system_instruction=(
            "You are a helpful question-answering assistant. Answer the user's "
            "question clearly and be concise while providing sufficient detail. "
            "Admit when you do not know something and do not fabricate facts. "
            "Use the conversation history to understand and answer follow-up "
            "questions. Use Markdown formatting when it improves readability."
        ),
        temperature=0.4,
    )


def test_generate_answer_hides_api_exception_details(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeAPIError(Exception):
        code = 401

    monkeypatch.setattr(
        "app.services.gemini_service.errors.APIError",
        FakeAPIError,
    )
    client = Mock()
    client.models.generate_content.side_effect = FakeAPIError(
        "sensitive response details"
    )
    monkeypatch.setattr(
        "app.services.gemini_service.genai.Client",
        Mock(return_value=client),
    )
    service = GeminiQAService(Settings(api_key="test-key"))

    with pytest.raises(GeminiServiceError) as error:
        service.generate_answer([{"role": "user", "content": "Hello"}])

    assert "sensitive response details" not in str(error.value)
    assert "test-key" not in str(error.value)


def test_generate_answer_rejects_empty_history(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "app.services.gemini_service.genai.Client",
        Mock(return_value=Mock()),
    )
    service = GeminiQAService(Settings(api_key="test-key"))

    with pytest.raises(ValueError, match="At least one"):
        service.generate_answer([])


def test_generate_answer_rejects_empty_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = Mock()
    client.models.generate_content.return_value = _response("  ")
    monkeypatch.setattr(
        "app.services.gemini_service.genai.Client",
        Mock(return_value=client),
    )
    service = GeminiQAService(Settings(api_key="test-key"))

    with pytest.raises(GeminiServiceError, match="empty response"):
        service.generate_answer([{"role": "user", "content": "Hello"}])
