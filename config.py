"""
config.py
---------
Centralized configuration for the AI Research Agent.
Loads environment variables and sets global settings.

Now using Groq (free) instead of OpenAI for the LLM.
SerpAPI is still used for web search.
"""

import os
from dotenv import load_dotenv

# Load variables from the .env file into the environment
load_dotenv()

# ── API Keys ──────────────────────────────────────────────────────────────────
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
SERPAPI_API_KEY: str = os.getenv("SERPAPI_API_KEY", "")

# ── Model Settings ────────────────────────────────────────────────────────────
# Free Groq models: "llama3-70b-8192", "llama3-8b-8192", "mixtral-8x7b-32768"
# llama3-70b-8192 is the most capable and still free.
GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama3-70b-8192")

# Maximum tokens the LLM may produce per call
MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "2000"))

# Temperature controls creativity (0 = deterministic, 1 = very creative)
TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.3"))

# ── Search Settings ───────────────────────────────────────────────────────────
# How many web-search results to retrieve per query
NUM_SEARCH_RESULTS: int = int(os.getenv("NUM_SEARCH_RESULTS", "5"))

# ── Report Settings ───────────────────────────────────────────────────────────
# Directory where finished reports are saved
REPORTS_DIR: str = os.getenv("REPORTS_DIR", "reports")

# ── Validation ────────────────────────────────────────────────────────────────
def validate_config() -> None:
    """
    Raise a clear error if required API keys are missing,
    so the user knows exactly what to fix before anything else runs.
    """
    missing: list[str] = []

    if not GROQ_API_KEY:
        missing.append("GROQ_API_KEY")
    if not SERPAPI_API_KEY:
        missing.append("SERPAPI_API_KEY")

    if missing:
        raise EnvironmentError(
            f"\n[Config Error] The following required environment variables are not set:\n"
            + "\n".join(f"  • {key}" for key in missing)
            + "\n\nCopy .env.example → .env and fill in your keys."
            + "\n\nGet a FREE Groq key at: https://console.groq.com"
        )
