import os
from dotenv import load_dotenv

load_dotenv()

# LLM Configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "ollama/mistral:instruct")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini/gemini-1.5-flash")

# API Keys
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")

# Project Configuration
PROJECT_NAME = "Financial Analysis Crew"
DATA_DIR = "data"
REPORTS_DIR = os.path.join(DATA_DIR, "reports")
CACHE_DIR = os.path.join(DATA_DIR, "cache")

# Create directories if they don't exist
os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)

# Model Configuration
MODEL_CONFIG_OLLAMA = {
    "base_url": OLLAMA_BASE_URL,
    "model": OLLAMA_MODEL,
}

MODEL_CONFIG_GEMINI = {
    "model": GEMINI_MODEL,
    "temperature": 0.7,
}
