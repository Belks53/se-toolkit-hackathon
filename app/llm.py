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
    """
    free_slots — строка вида:
        09:00-11:30
        14:00-16:00
        18:30-22:00
    Для каждого периода генерируется отдельная идея.
    """
    prompts = {
        "ru": f"""
Ты — помощник, который помогает планировать свободное время.

У пользователя есть следующие СВОБОДНЫЕ ПЕРИОДЫ:
{free_slots}

Для КАЖДОГО из этих периодов предложи ОДНУ конкретную идею.
Всего идей = количеству периодов.

ПРАВИЛА:
• Учитывай время: утром (5-12) — активное, днём (12-17) — рабочее/продуктивное, вечером (17-22) — спокойное/расслабление, ночью (22-5) — тихое/подготовка ко сну.
• Используй разные категории: спорт, учёба, творчество, уборка, прогулка, хобби, общение.
• НЕ повторяй категории. НЕ предлагай только отдых и медитацию.
• Описание должно быть привязано именно к этому временному окну.

Оформи ответ СТРОГО в таком формате для каждого периода:

⏰ *Период: 09:00-11:30*
🎯 Идея: [название идеи]
📂 Категория: [категория]
📝 Описание: [1-2 предложения, почему это подходит именно для этого времени]

⏰ *Период: 14:00-16:00*
🎯 Идея: [название идеи]
📂 Категория: [категория]
📝 Описание: [1-2 предложения, почему это подходит именно для этого времени]

...и так для каждого периода.

В конце добавь короткую мотивирующую фразу.
Отвечай на русском языке.
""",
        "en": f"""
You are an assistant that helps plan free time.

The user has the following FREE PERIODS:
{free_slots}

For EACH of these periods suggest ONE specific idea.
Total ideas = number of periods.

RULES:
• Consider time: morning (5-12) = active, afternoon (12-17) = productive, evening (17-22) = calm/relaxation, night (22-5) = quiet/wind-down.
• Use different categories: sport, study, creativity, chores, walk, hobby, social.
• Do NOT repeat categories. Do NOT only suggest rest and meditation.
• Description should be tied to this specific time window.

Format the response STRICTLY like this for each period:

⏰ *Period: 09:00-11:30*
🎯 Idea: [idea name]
📂 Category: [category]
📝 Description: [1-2 sentences, why this fits this specific time]

⏰ *Period: 14:00-16:00*
🎯 Idea: [idea name]
📂 Category: [category]
📝 Description: [1-2 sentences, why this fits this specific time]

...and so on for each period.

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
