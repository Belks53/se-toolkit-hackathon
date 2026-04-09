from openai import OpenAI
from config import *
import asyncio
import logging
import random

logger = logging.getLogger(__name__)

client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url="https://openrouter.ai/api/v1",
    max_retries=0,  # Disable OpenAI client's built-in retries — we handle it ourselves
)

# Models to try in order (free first, then paid)
FALLBACK_MODELS = [
    LLM_MODEL,
    "qwen/qwen3-next-80b-a3b-instruct:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "google/gemma-4-26b-a4b-it:free",
    "qwen/qwen-2.5-72b-instruct:free",
    "meta-llama/llama-3.1-8b-instruct:free",
    "mistralai/mistral-7b-instruct:free",
    # Paid fallbacks (cheaper models)
    "qwen/qwen-2.5-72b-instruct",
    "meta-llama/llama-3.3-70b-instruct",
]
FALLBACK_MODELS = list(dict.fromkeys(FALLBACK_MODELS))

# Retry strategy: only 1 retry per model, long delay between models
MODEL_SWITCH_DELAY = 60  # seconds to wait before switching to next model after rate limit


async def suggest_activities(free_slots, lang="ru"):
    """
    Generate activity suggestions for each free time period.
    Tries multiple models but avoids hammering with retries.
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

    # Try each model ONCE — no retries on rate limit (free models die fast)
    for model in FALLBACK_MODELS:
        try:
            res = await asyncio.to_thread(
                client.chat.completions.create,
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.9,
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
            error_str = str(e).lower()

            # Rate limit — try next model (but wait a bit to not burn through them all)
            if "429" in error_str or "rate" in error_str or "temporarily" in error_str:
                logger.warning(f"Rate limited on {model}, will try next model after {MODEL_SWITCH_DELAY}s...")
                # Wait before trying next model to avoid burning through all rate limits
                await asyncio.sleep(MODEL_SWITCH_DELAY)
                continue  # Try next model

            # Non-rate-limit error — don't retry, try next model immediately
            if "404" in error_str or "not found" in error_str:
                logger.warning(f"Model not found: {model}")
                continue

            logger.error(f"LLM error on {model}: {e}")
            continue  # Try next model

    # All models failed
    raise ValueError("All LLM models failed — using fallback messages")
