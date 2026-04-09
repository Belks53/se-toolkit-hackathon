import os

BOT_TOKEN = os.getenv("BOT_TOKEN")

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# LLM Model configuration
# Primary model to use (first in fallback list)
LLM_MODEL = os.getenv("LLM_MODEL", "google/gemma-4-26b-a4b-it:free")