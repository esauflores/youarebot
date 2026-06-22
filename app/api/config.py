import os

DB_PATH = os.getenv("DB_PATH", "/app/data/chat.db")

MODEL_NAME = os.getenv("MODEL_NAME", "typeform/distilbert-base-uncased-mnli")
CANDIDATE_LABELS = ["bot", "human"]
HYPOTHESIS_TEMPLATE = "The author of this dialog is a {}."

LLM_URL = os.getenv("LLM_URL", "http://localhost:8080")
