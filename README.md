# YouAreBot

An LLM-powered chatbot that tries to pass as human, with zero-shot classification to detect bot-like behavior. Part of the HumanOrBot project.

## Overview

Three-tier architecture:

- **FastAPI inference service** — stores messages in SQLite, generates replies via llama.cpp (GGUF models), classifies conversations using a HuggingFace zero-shot pipeline
- **Streamlit UI** — chat interface that shows bot/human probability scores for each message
- **llama.cpp server** — serves a local LLM (Qwen2.5 GGUF) via OpenAI-compatible API

## Running

### Docker (recommended)

```bash
just up
```

### Local dev

```bash
./run_all_linux.sh
```

Or manually:

```bash
uv sync
uv run uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --reload
uv run streamlit run app/web/streamlit_app.py --server.port=8501 --server.address=0.0.0.0
```

## Endpoints

- `POST /get_message` — send a user message, get an LLM reply + bot probability for the conversation
- `POST /predict` — classify a single message
- `GET /health` — health check
