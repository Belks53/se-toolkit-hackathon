from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, time
from llm import suggest_activities
from lang import get, get_fallback_messages, get_fallback_for_slots
import logging
from pytz import utc

logger = logging.getLogger(__name__)

sch = None

def find_free(busy):
    if not busy:
        return ["00:00-23:59"]

    busy = sorted(busy, key=lambda x: x["start_time"])
    free=[]
    prev="00:00"

    for s in busy:
        start_str = str(s["start_time"])[:5]
        end_str = str(s["end_time"])[:5]
        if prev < start_str:
            free.append(f"{prev}-{start_str}")
        prev=end_str

    if prev<"23:59":
        free.append(f"{prev}-23:59")

    return free

async def notify_user(user_id, notif_time, bot, db):
    logger.info(f"Sending notification to user {user_id}")
    lang = await db.get_language(user_id)
    tz_name = await db.get_timezone(user_id)
    logger.info(f"User {user_id} timezone: {tz_name}")
    try:
        import pytz
        user_tz = pytz.timezone(tz_name)
    except:
        user_tz = pytz.utc
    now = datetime.now(user_tz)
    logger.info(f"User {user_id} current time in their timezone: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    today = now.weekday()
    logger.info(f"User {user_id} current day (0=Mon, 6=Sun): {today}")
    busy=await db.get_busy_for_day(user_id,today)
    logger.info(f"User {user_id} busy slots for day {today}: {len(busy)}")
    free=find_free(busy)

    text = get(lang, "free_time") + "\n"

    # One LLM call for all slots at once
    try:
        ideas = await suggest_activities("\n".join(free), lang)
        text += f"\n💡 {ideas}\n"
    except Exception as e:
        logger.error(f"LLM error: {e}")
        # Use fallback messages for each slot based on its time period
        fallback_map = get_fallback_for_slots(free, lang)
        for slot, msg in fallback_map.items():
            text += f"\n⏰ <b>{slot}</b>\n💡 {msg}\n"

    await bot.send_message(user_id, text, parse_mode="HTML")
    logger.info(f"Notification sent to user {user_id}")

async def schedule_notifications(bot, db):
    users = await db.get_users()
    logger.info(f"Found {len(users)} users for scheduling")
    logger.info(f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    for u in users:
        notif_time = u["notification_time"]
        tz_name = u.get("timezone") or "UTC"
        try:
            import pytz
            tz = pytz.timezone(tz_name)
        except:
            tz = pytz.utc

        if notif_time:
            hour = notif_time.hour
            minute = notif_time.minute
            job = sch.add_job(notify_user, "cron", hour=hour, minute=minute,
                        timezone=tz,
                        args=[u["id"], notif_time, bot, db],
                        id=f"notif_{u['id']}", replace_existing=True)
            logger.info(f"✅ Scheduled for user {u['id']} at {hour:02d}:{minute:02d} ({tz_name}) | Job: {job.id}")
        else:
            logger.info(f"User {u['id']} has no notification_time, skipping")

    logger.info(f"All jobs: {[(j.id, j.trigger) for j in sch.get_jobs()]}")

async def start_scheduler(bot, db):
    global sch
    sch=AsyncIOScheduler()
    await schedule_notifications(bot, db)
    sch.start()