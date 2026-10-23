
"""Streamlit interface for the question-answering application."""

from __future__ import annotations

import logging

import streamlit as st

from app.config.settings import ConfigurationError, load_settings
from app.services.gemini_service import (
    ConversationMessage,
    GeminiQAService,
    GeminiServiceError,
)
from app.utils.logging_config import configure_logging

logger = logging.getLogger(__name__)


def _initialize_conversation() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = []


def main() -> None:
    configure_logging()
    st.set_page_config(
        page_title="AI Question & Answering System",
        page_icon="💬",
    )
    st.title("AI Question & Answering System")
    st.write(
        "Ask a question and get an answer from Google Gemini. "
        "Continue the conversation with follow-up questions."
    )

    try:
        settings = load_settings()
    except ConfigurationError as error:
        st.error(str(error))
        return

    with st.sidebar:
        st.subheader("Conversation")
        st.caption(f"Model: `{settings.model}`")
        st.caption(f"Temperature: `{settings.temperature}`")

        if st.button("Clear Conversation", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

    _initialize_conversation()

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input("Enter your question")
    if question is None:
        return

    question = question.strip()
    if not question:
        st.warning("Please enter a question before submitting.")
        return

    user_message: ConversationMessage = {
        "role": "user",
        "content": question,
    }

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Generating an answer with Gemini..."):
            try:
                service = GeminiQAService(settings)
                history = [
                    *st.session_state.messages,
                    user_message,
                ]
                answer = service.generate_answer(history)
            except GeminiServiceError as error:
                logger.warning("Could not generate an answer.")
                st.error(str(error))
                return

        st.markdown(answer)

    st.session_state.messages.extend(
        [
            user_message,
            {"role": "assistant", "content": answer},
        ]
    )


if __name__ == "__main__":
    main()
