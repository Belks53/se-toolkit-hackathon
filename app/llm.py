from openai import OpenAI
from config import *
import asyncio
import logging
import random

logger = logging.getLogger(__name__)

client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

# Retry settings for rate limit handling
MAX_RETRIES = 3
RETRY_DELAY_BASE = 2  # seconds
RETRY_DELAY_MAX = 30  # seconds

# Alternative models to try if the primary one fails
FALLBACK_MODELS = [
    LLM_MODEL,
    "qwen/qwen3-next-80b-a3b-instruct:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "microsoft/phi-4:free",
]
# Remove duplicates while preserving order
FALLBACK_MODELS = list(dict.fromkeys(FALLBACK_MODELS))

async def suggest_activities(free_slots, lang="ru"):
    prompts = {
        "ru": f"""
Ты — помощник, который помогает планировать свободное время.

Свободное время пользователя: {free_slots}

Предложи 5 РАЗНЫХ идей из разных категорий: спорт, учёба, творчество, уборка, прогулка, хобби, общение.
Учитывай время суток — утром активное, днём рабочее, вечером спокойное.
НЕ повторяй одно и то же. НЕ предлагай только отдых и медитацию.

Оформи ответ КРАСИВО в следующем формате:

🎯 *Идея 1*
📂 Категория: [категория]
⏰ Время: [подходящее время]
📝 Описание: [краткое описание, 1-2 предложения]

🎯 *Идея 2*
📂 Категория: [категория]
⏰ Время: [подходящее время]
📝 Описание: [краткое описание, 1-2 предложения]

...и так далее для всех 5 идей.

В конце добавь короткую мотивирующую фразу.
Отвечай на русском языке.
""",
        "en": f"""
You are an assistant that helps plan free time.

User's free time: {free_slots}

Suggest 5 DIVERSE ideas from different categories: sport, study, creativity, chores, walk, hobby, social.
Consider time of day — morning = active, afternoon = productive, evening = calm.
Do NOT repeat. Do NOT only suggest rest and meditation.

Format the response BEAUTIFULLY as follows:

🎯 *Idea 1*
📂 Category: [category]
⏰ Time: [suitable time]
📝 Description: [brief description, 1-2 sentences]

🎯 *Idea 2*
📂 Category: [category]
⏰ Time: [suitable time]
📝 Description: [brief description, 1-2 sentences]

...and so on for all 5 ideas.

At the end, add a short motivational phrase.
Respond in English.
""",
    }
    prompt = prompts.get(lang, prompts["ru"])

    # Try multiple models if rate limited on one
    for model in FALLBACK_MODELS:
        last_error = None
        for attempt in range(MAX_RETRIES):
            try:
                res = await asyncio.to_thread(
                    client.chat.completions.create,
                    model=model,
                    messages=[{"role":"user","content":prompt}],
                    temperature=0.9
                )

                if not res.choices or res.choices[0] is None:
                    raise ValueError("Empty response from LLM")

                content = res.choices[0].message.content
                if not content:
                    raise ValueError("No content in LLM response")

                if model != FALLBACK_MODELS[0]:
                    logger.info(f"Successfully used fallback model: {model}")
                return content

            except Exception as e:
                last_error = e
                error_str = str(e).lower()
                
                # Check if it's a rate limit error (429)
                if "429" in error_str or "rate" in error_str or "temporarily" in error_str:
                    if attempt < MAX_RETRIES - 1:
                        # Exponential backoff with jitter
                        delay = min(RETRY_DELAY_BASE * (2 ** attempt) + random.uniform(0, 1), RETRY_DELAY_MAX)
                        logger.warning(f"Rate limited on {model} (attempt {attempt+1}/{MAX_RETRIES}). Retrying in {delay:.1f}s...")
                        await asyncio.sleep(delay)
                    else:
                        logger.warning(f"Rate limit exceeded on {model} after {MAX_RETRIES} retries, trying next model...")
                        break  # Break retry loop, try next model
                else:
                    # Non-rate-limit error, don't retry with this model
                    logger.error(f"LLM error on {model} (non-retryable): {e}")
                    break  # Try next model

    # All models exhausted
    raise last_error if last_error else ValueError("All models failed")
