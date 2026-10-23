# AI Question & Answering System

A modular Streamlit chat application that uses Google Gemini to answer
questions and maintain follow-up conversation context for the current session.

## Features

- ChatGPT-style interface using Streamlit chat components.
- Multi-turn conversation history held in Streamlit session state.
- Configurable Gemini model and response temperature.
- Loading feedback, empty-input validation, and friendly API error messages.
- Gemini credentials loaded from a local `.env` file and excluded from Git.
- Unit tests use mocked Gemini responses; they do not make real API calls.

## Architecture

The Streamlit UI is in `app/main.py`; validated environment configuration lives
in `app/config/settings.py`; all Gemini communication is encapsulated in
`app/services/gemini_service.py`. The system prompt and logging configuration
are kept in `app/prompts/qa_prompt.py` and `app/utils/logging_config.py`.

## Project structure

```text
question_answering_app/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py
│   ├── prompts/
│   │   ├── __init__.py
│   │   └── qa_prompt.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── gemini_service.py
│   └── utils/
│       ├── __init__.py
│       └── logging_config.py
├── tests/
│   ├── __init__.py
│   ├── test_config.py
│   └── test_gemini_service.py
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
└── run.sh
```

## Prerequisites

- Python 3.10 or newer.
- A Gemini API key with access to the model you configure.
- Internet access when the application calls the Gemini API.

## Setup

Run these commands from the `question_answering_app` directory.

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate it on macOS/Linux:

```bash
source .venv/bin/activate
```

Activate it on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

If PowerShell prevents activation, use Command Prompt:

```bat
.venv\Scripts\activate.bat
```

Install runtime and test dependencies:

```bash
python -m pip install -r requirements.txt
```

## Gemini API key and `.env` configuration

Copy `.env.example` to `.env`, then replace the placeholder with your own
Gemini API key. Do not commit or share `.env`.

macOS/Linux:

```bash
cp .env.example .env
```

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Set values in `.env`:

```dotenv
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-3.5-flash-lite
TEMPERATURE=0.2
```

`GEMINI_API_KEY` is required. `GEMINI_MODEL` defaults to
`gemini-3.5-flash-lite` and `TEMPERATURE` defaults to `0.2`. Temperature must
be between `0` and `2`; available models and parameter support depend on your
Google AI account and model.

## Run the application

From the project directory, with the virtual environment active:

```bash
streamlit run app/main.py
```

On macOS/Linux, the convenience script can also be used:

```bash
bash run.sh
```

Streamlit prints the local URL to open in a browser. Use the sidebar's
**Clear Conversation** button to reset the current session.

## Run tests

Tests use mock clients and require no valid API key:

```bash
pytest
```

## Example questions

- What is the difference between supervised and unsupervised learning?
- Explain how a heat pump works in simple terms.
- What are three ways to make a Python function easier to test?
- Can you summarize that answer as a short checklist?

## Troubleshooting

- **Configuration error:** create `.env` from `.env.example` and set
  `GEMINI_API_KEY`.
- **Authentication or permission error:** verify the key is active and has
  access to the configured Gemini model. The UI intentionally does not show raw
  API errors.
- **Model error:** set `GEMINI_MODEL` to a model available to your account and
  supporting the configured parameters.
- **Invalid temperature:** use a numeric value from `0` through `2`.
- **Command not found:** activate the virtual environment and install
  `requirements.txt`; use `python -m streamlit run app/main.py` if needed.
- **Port already in use:** run Streamlit with a different port, for example
  `streamlit run app/main.py --server.port 8502`.

## Security considerations

- Keep `.env` private; it is excluded from version control.
- `.env.example` contains placeholders only.
- The application never displays or logs the API key.
- Application logs avoid recording prompt or conversation content.
- Conversation history is held in Streamlit session state and is not persisted
  by this application. Avoid entering sensitive or confidential information.
- For production, manage credentials through a secrets manager and apply
  appropriate access, network, privacy, and usage controls.

## Stop the application and deactivate the environment

Stop Streamlit in the terminal where it is running with **Ctrl+C**. Deactivate
the Python virtual environment with:

```bash
deactivate
```

## Future enhancements

- Persistent, user-scoped conversation storage with retention controls.
- Authentication and per-user rate limits.
- Streaming responses and token-usage reporting.
- Configurable system prompts and supported model selection in the UI.
- Deployment health checks, metrics, and structured observability.
