# ─── Services ────────────────────────────────────────────────────────────────

up:                       # Start all services (build if needed)
    docker compose up --build -d

down:                     # Stop all services
    docker compose down

restart: down up          # Restart all services

logs:                     # Tail logs from all services
    docker compose logs -f

logs-api:                 # Tail logs from inference-service only
    docker compose logs -f inference-service

logs-streamlit:           # Tail logs from streamlit only
    docker compose logs -f streamlit

logs-llm:                 # Tail logs from llm only
    docker compose logs -f llm

shell-api:                # Open shell in inference-service
    docker compose exec inference-service /bin/bash

shell-streamlit:          # Open shell in streamlit
    docker compose exec streamlit /bin/bash

# ─── Dependencies ────────────────────────────────────────────────────────────

lock:                     # Regenerate uv.lock from pyproject.toml
    uv lock

sync:                     # Install dependencies locally
    uv sync

download-model:           # Download GGUF model for llama.cpp
    ./download_model.sh

# ─── Dev (local, no Docker) ──────────────────────────────────────────────────

run-api:                  # Run FastAPI locally (requires postgres running)
    uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --reload

run-streamlit:            # Run Streamlit locally (requires API running)
    streamlit run app/web/streamlit_app.py --server.port=8501 --server.address=0.0.0.0

# ─── Maintenance ─────────────────────────────────────────────────────────────

reset:                    # Full reset: down, remove volumes, rebuild
    docker compose down -v
    docker compose up --build -d

clean:                    # Remove all Docker artifacts for this project
    docker compose down -v --rmi all --remove-orphans

# ─── Help ────────────────────────────────────────────────────────────────────

default:                  # Show available commands
    @just --list
