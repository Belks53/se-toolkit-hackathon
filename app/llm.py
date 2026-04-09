"""
LLM Integration Module
======================
Handles communication with LLM APIs to generate activity suggestions
for user's free time periods.

Provider chain (tried sequentially):
1. OpenRouter (primary — free models)
2. Mistral AI (backup — paid, more reliable)
3. Pre-written fallback messages (last resort)

Design: fail fast on each provider, move to next immediately.
No retries within a provider — rate limits mean waiting won't help.
"""

from openai import OpenAI
from config import *
import asyncio
import logging

logger = logging.getLogger(__name__)

# OpenRouter client — primary provider (free tier models)
openrouter_client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url="https://openrouter.ai/api/v1",
    max_retries=0,  # We handle fallback manually
)

# Mistral client — backup provider (paid, but more reliable)
mistral_client = None
if MISTRAL_API_KEY:
    mistral_client = OpenAI(
        api_key=MISTRAL_API_KEY,
        base_url="https://api.mistral.ai/v1",
        max_retries=0,
    )
else:
    logger.warning("MISTRAL_API_KEY not set — Mistral fallback disabled")

# Free models on OpenRouter to try (in order)
OPENROUTER_MODELS = [
    LLM_MODEL,  # Primary model from config
    "qwen/qwen3-next-80b-a3b-instruct:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "google/gemma-4-26b-a4b-it:free",
]
OPENROUTER_MODELS = list(dict.fromkeys(OPENROUTER_MODELS))

# Mistral models (paid, but cheap and reliable)
MISTRAL_MODELS = [
    "mistral-small-latest",   # Cheap, fast
    "mistral-medium-latest",  # Better quality
]


async def suggest_activities(free_slots, lang="ru"):
    """
    Generate activity suggestions for each free time period.

    Tries OpenRouter models first, then Mistral, then raises exception
    so the caller uses pre-written fallback messages.

    Args:
        free_slots: Newline-separated time ranges, e.g. "09:00-11:30\n14:00-16:00"
        lang: Language code ("ru" or "en")

    Returns:
        str: LLM-generated activity suggestions.

    Raises:
        ValueError: If all providers fail.
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
• Выбирай стикеры под тему
• Пиши коротко и по делу

Оформи ответ СТРОГО в таком формате для каждого периода:

⏰ 09:00-11:30
🎯 Идея: [название идеи]
📂 Категория: [категория]
📝 Описание: [1-2 предложения, почему это подходит именно для этого времени]

⏰ 14:00-16:00
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
• Description should be tied to this specific time window
• Choose stickers according to the theme
• Write briefly and to the point


Format the response STRICTLY like this for each period:

⏰ 09:00-11:30
🎯 Idea: [idea name]
📂 Category: [category]
📝 Description: [1-2 sentences, why this fits this specific time]

⏰ 14:00-16:00
🎯 Idea: [idea name]
📂 Category: [category]
📝 Description: [1-2 sentences, why this fits this specific time]

...and so on for each period.

At the end, add a short motivational phrase.
Respond in English.
""",
    }
    prompt = prompts.get(lang, prompts["ru"])

    # === Phase 1: Try OpenRouter free models ===
    for model in OPENROUTER_MODELS:
        try:
            res = await asyncio.to_thread(
                openrouter_client.chat.completions.create,
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.9,
            )

            if not res.choices or res.choices[0] is None:
                raise ValueError("Empty response from LLM")

            content = res.choices[0].message.content
            if not content:
                raise ValueError("No content in LLM response")

            if model != OPENROUTER_MODELS[0]:
                logger.info(f"Used OpenRouter fallback model: {model}")
            return content

        except Exception as e:
            error_str = str(e).lower()
            if "429" in error_str or "rate" in error_str or "temporarily" in error_str:
                logger.debug(f"OpenRouter rate limited on {model}")
            else:
                logger.debug(f"OpenRouter error on {model}: {e}")
            continue

    # === Phase 2: Try Mistral (if configured) ===
    if mistral_client:
        for model in MISTRAL_MODELS:
            try:
                res = await asyncio.to_thread(
                    mistral_client.chat.completions.create,
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.9,
                )

                if not res.choices or res.choices[0] is None:
                    raise ValueError("Empty response from Mistral")

                content = res.choices[0].message.content
                if not content:
                    raise ValueError("No content in Mistral response")

                logger.info(f"Used Mistral model: {model}")
                return content

            except Exception as e:
                logger.debug(f"Mistral error on {model}: {e}")
                continue
    else:
        logger.debug("Mistral not configured, skipping")

    # === All providers failed ===
    raise ValueError("All LLM providers failed — using fallback messages")
