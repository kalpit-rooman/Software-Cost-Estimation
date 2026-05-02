from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from the backend directory (if present).
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SUPPORTED_DATASETS = ["china", "cocomo81", "desharnais"]
INSIGHT_TEMPLATE = "Best model for this dataset is {best_model}"

# ---------------------------------------------------------------------------
# Runtime mode
# ---------------------------------------------------------------------------
# PREDICTION_MODE: "ai" – use AI provider | "model" – use saved ML models
PREDICTION_MODE: str = os.getenv("PREDICTION_MODE", "model")

# ---------------------------------------------------------------------------
# AI provider settings
# ---------------------------------------------------------------------------
AI_PROVIDER: str = os.getenv("AI_PROVIDER", "openai")
AI_MODEL: str = os.getenv("AI_MODEL", "")

# Provider API keys (backend-only, never forwarded to the client)
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "")   # override for Groq / Mistral etc.
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")

# Prompt profile: "conservative" | "balanced" | "optimistic"
AI_PROFILE: str = os.getenv("AI_PROFILE", "balanced")

# ---------------------------------------------------------------------------
# Cost / currency settings
# ---------------------------------------------------------------------------
# Blended monthly rate per person in INR.  Admin can override via env var.
DEFAULT_MONTHLY_RATE_INR: float = float(os.getenv("DEFAULT_MONTHLY_RATE_INR", "150000"))

# ---------------------------------------------------------------------------
# Intake cache settings (Phase 10)
# ---------------------------------------------------------------------------
REDIS_URL: str = os.getenv("REDIS_URL", "")
INTAKE_CACHE_TTL_SECONDS: int = int(os.getenv("INTAKE_CACHE_TTL_SECONDS", "3600"))
MAX_CACHED_INTAKES: int = int(os.getenv("MAX_CACHED_INTAKES", "1000"))
