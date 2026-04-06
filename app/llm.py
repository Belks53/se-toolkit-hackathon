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
Свободное время пользователя: {free_slots}

Предложи 5 РАЗНЫХ идей из разных категорий: спорт, учёба, творчество, уборка, прогулка, хобби, общение.
Учитывай время суток — утром активное, днём рабочее, вечером спокойное.
НЕ повторяй одно и то же. НЕ предлагай только отдых и медитацию.
Отвечай на русском. Каждую идею с новой строки, кратко.
""",
        "en": f"""
User's free time: {free_slots}

Suggest 5 DIVERSE ideas from different categories: sport, study, creativity, chores, walk, hobby, social.
Consider time of day — morning = active, afternoon = productive, evening = calm.
Do NOT repeat. Do NOT only suggest rest and meditation.
Respond in English. Each idea on a new line, briefly.
""",
    }
    prompt = prompts.get(lang, prompts["ru"])

    res = await asyncio.to_thread(
        client.chat.completions.create,
        model="qwen/qwen3.6-plus:free",
        messages=[{"role":"user","content":prompt}],
        temperature=0.9
    )
    return res.choices[0].message.content