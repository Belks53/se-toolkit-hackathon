from openai import OpenAI
from config import *
import asyncio
import logging

logger = logging.getLogger(__name__)

client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

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

    res = await asyncio.to_thread(
        client.chat.completions.create,
        model="qwen/qwen3-235b-a22b:free",
        messages=[{"role":"user","content":prompt}],
        temperature=0.9
    )
    return res.choices[0].message.content