"""
Notification Scheduler Module
=============================
Manages daily notification jobs using APScheduler. For each user, it:
1. Finds free time periods (gaps between busy slots)
2. Requests LLM-generated activity suggestions for each free period
3. Falls back to pre-written messages if LLM is unavailable
4. Sends formatted notifications via Telegram Bot

The scheduler respects user timezones and notification time preferences.
"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, time
from llm import suggest_activities
from lang import get, get_fallback_messages, get_fallback_for_slots
import logging
from pytz import utc

logger = logging.getLogger(__name__)

# Global scheduler instance (initialized in start_scheduler)
sch = None


def find_free(busy):
    """
    Calculate free time periods by finding gaps between busy slots.

    Given a list of busy time slots (sorted by start_time), this function
    identifies gaps from 00:00 to 23:59 that represent free time.

    Example:
        busy = [
            {"start_time": "09:00:00", "end_time": "10:30:00"},
            {"start_time": "14:00:00", "end_time": "15:00:00"}
        ]
        Returns: ["00:00-09:00", "10:30-14:00", "15:00-23:59"]

    Args:
        busy: List of dicts with "start_time" and "end_time" keys.

    Returns:
        List of strings in "HH:MM-HH:MM" format representing free periods.
        Returns ["00:00-23:59"] if no busy slots (fully free day).
    """
    if not busy:
        return ["00:00-23:59"]

    busy = sorted(busy, key=lambda x: x["start_time"])
    free = []
    prev = "00:00"

    for s in busy:
        start_str = str(s["start_time"])[:5]
        end_str = str(s["end_time"])[:5]
        # Gap exists if previous end is before current start
        if prev < start_str:
            free.append(f"{prev}-{start_str}")
        prev = end_str

    # Add remaining time after last busy slot
    if prev < "23:59":
        free.append(f"{prev}-23:59")

    return free


async def notify_user(user_id, notif_time, bot, db):
    """
    Send daily notification with free time and activity suggestions.

    This is the main job callback triggered by APScheduler at the user's
    configured notification time. It:
    1. Fetches user's language and timezone preferences
    2. Retrieves busy slots for the current day
    3. Calculates free time periods
    4. Requests LLM suggestions (or falls back to pre-written messages)
    5. Sends formatted message to the user

    Args:
        user_id: Telegram user ID.
        notif_time: Scheduled notification time (datetime.time object).
        bot: aiogram Bot instance for sending messages.
        db: Database instance for fetching user data.
    """
    logger.info(f"Sending notification to user {user_id}")

    # Fetch user preferences
    lang = await db.get_language(user_id)
    tz_name = await db.get_timezone(user_id)
    logger.info(f"User {user_id} timezone: {tz_name}")

    # Get current time in user's timezone
    try:
        import pytz
        user_tz = pytz.timezone(tz_name)
    except Exception:
        user_tz = pytz.utc

    now = datetime.now(user_tz)
    logger.info(f"User {user_id} current time: {now.strftime('%Y-%m-%d %H:%M:%S')}")

    # Determine current day of week (0=Monday, 6=Sunday)
    today = now.weekday()
    logger.info(f"User {user_id} day of week: {today}")

    # Get busy slots and calculate free time
    busy = await db.get_busy_for_day(user_id, today)
    logger.info(f"User {user_id} busy slots: {len(busy)}")
    free = find_free(busy)

    # Build notification message starting with free time header
    text = get(lang, "free_time") + "\n"

    # Try to get LLM-generated suggestions for all free periods
    try:
        ideas = await suggest_activities("\n".join(free), lang)
        text += f"\n💡 {ideas}\n"
    except Exception as e:
        # LLM failed — use pre-written fallback messages for each slot
        logger.error(f"LLM error: {e}")
        fallback_map = get_fallback_for_slots(free, lang)
        for slot, msg in fallback_map.items():
            text += f"\n⏰ <b>{slot}</b>\n💡 {msg}\n"

    # Send the notification to the user
    await bot.send_message(user_id, text, parse_mode="HTML")
    logger.info(f"Notification sent to user {user_id}")


async def schedule_notifications(bot, db):
    """
    Schedule daily notification jobs for all registered users.

    Iterates through all users in the database and creates a cron job
    for each at their configured notification time and timezone.
    Jobs are replaceable (replace_existing=True) to handle restarts.

    Args:
        bot: aiogram Bot instance passed to the notify_user callback.
        db: Database instance for fetching users list.
    """
    users = await db.get_users()
    logger.info(f"Found {len(users)} users for scheduling")
    logger.info(f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    for u in users:
        notif_time = u["notification_time"]
        tz_name = u.get("timezone") or "UTC"
        try:
            import pytz
            tz = pytz.timezone(tz_name)
        except Exception:
            tz = pytz.utc

        if notif_time:
            hour = notif_time.hour
            minute = notif_time.minute
            job = sch.add_job(
                notify_user, "cron",
                hour=hour, minute=minute,
                timezone=tz,
                args=[u["id"], notif_time, bot, db],
                id=f"notif_{u['id']}",
                replace_existing=True
            )
            logger.info(f"✅ Scheduled for user {u['id']} at {hour:02d}:{minute:02d} ({tz_name}) | Job: {job.id}")
        else:
            logger.info(f"User {u['id']} has no notification_time, skipping")

    logger.info(f"All jobs: {[(j.id, j.trigger) for j in sch.get_jobs()]}")


async def start_scheduler(bot, db):
    """
    Initialize and start the APScheduler instance.

    Creates the global scheduler object, schedules all user notifications,
    and starts the scheduler. Called during bot startup in main().

    Args:
        bot: aiogram Bot instance.
        db: Database instance.
    """
    global sch
    sch = AsyncIOScheduler()
    await schedule_notifications(bot, db)
    sch.start()
