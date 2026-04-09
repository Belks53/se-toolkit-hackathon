"""
Configuration Module
====================
Loads environment variables for the Telegram bot, PostgreSQL database,
and LLM API credentials. All values come from environment (typically
set via .env file or Docker Compose).
"""

import os

# Telegram Bot Token — get from @BotFather on Telegram
BOT_TOKEN = os.getenv("BOT_TOKEN")

# PostgreSQL connection parameters
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# OpenRouter API key for LLM access (https://openrouter.ai/)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Mistral AI API key as backup provider (https://console.mistral.ai/)
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

# LLM model to use as primary. Can be overridden via LLM_MODEL env var.
# Default: google/gemma-4-26b-a4b-it:free
LLM_MODEL = os.getenv("LLM_MODEL", "google/gemma-4-26b-a4b-it:free")
