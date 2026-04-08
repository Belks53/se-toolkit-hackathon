import asyncio
import logging
from datetime import datetime
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from db import Database
from keyboards import *
from keyboards import lang_kb, tz_kb
from scheduler import start_scheduler, notify_user
import scheduler
from lang import get
from config import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
db = Database()

start_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="/start")]],
    resize_keyboard=True
)


def make_persistent_kb(lang):
    labels = {
        "ru": ["➕ Добавить", "❌ Удалить", "📋 Моя занятость", "⏰ Напоминания", "🌍 Часовой пояс", "🌐 Язык"],
        "en": ["➕ Add", "❌ Delete", "📋 My Schedule", "⏰ Notifications", "🌍 Timezone", "🌐 Language"],
    }
    l = labels.get(lang, labels["ru"])
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=l[0]), KeyboardButton(text=l[1])],
            [KeyboardButton(text=l[2]), KeyboardButton(text=l[3])],
            [KeyboardButton(text="/start"), KeyboardButton(text="/help")],
            [KeyboardButton(text=l[5]), KeyboardButton(text=l[4])]
        ],
        resize_keyboard=True
    )


def make_menu_text(lang):
    lines = {
        "ru": [
            "⏰ <b>Time Manager</b>",
            "Управляй своим временем легко!",
            "➕ <b>Добавить</b> — занять интервал",
            "❌ <b>Удалить</b> — убрать интервал",
            "📋 <b>Моя занятость</b> — расписание на неделю",
            "⏰ <b>Напоминания</b> — время уведомлений",
            "🌍 <b>Часовой пояс</b> — настроить таймзону",
            "🌐 <b>Language</b> — сменить язык",
        ],
        "en": [
            "⏰ <b>Time Manager</b>",
            "Manage your time easily!",
            "➕ <b>Add</b> — busy slot",
            "❌ <b>Delete</b> — remove slot",
            "📋 <b>My Schedule</b> — weekly timetable",
            "⏰ <b>Notifications</b> — notification time",
            "🌍 <b>Timezone</b> — set your timezone",
            "🌐 <b>Language</b> — switch language",
        ],
    }
    l = lines.get(lang, lines["ru"])
    return "\n\n".join(l)


class Form(StatesGroup):
    select_day = State()
    start_hour = State()
    start_minute = State()
    end_hour = State()
    end_minute = State()
    notif_hour = State()
    notif_minute = State()
    notification = State()


class FirstLaunch(StatesGroup):
    select_lang = State()
    select_tz = State()


async def get_lang(user_id):
    lang = await db.get_language(user_id)
    return lang or "ru"


async def send_menu(msg, state=None):
    if state:
        await state.clear()
    lang = await get_lang(msg.from_user.id)
    text = make_menu_text(lang)
    kb = make_persistent_kb(lang)
    await msg.answer(text, reply_markup=kb, parse_mode="HTML")


async def answer_menu(msg, text, kb=None):
    lang = await get_lang(msg.from_user.id)
    if kb is None:
        kb = make_persistent_kb(lang)
    await msg.answer(text, reply_markup=kb, parse_mode="HTML")


@dp.message(F.text == "/start")
async def start(msg: Message, state: FSMContext = None):
    logger.info(f"/start from user {msg.from_user.id}")
    
    # Check if user exists in DB
    async with db.pool.acquire() as conn:
        exists = await conn.fetchval("SELECT EXISTS(SELECT 1 FROM users WHERE id=$1)", msg.from_user.id)
    
    if not exists:
        # First launch - show language selection
        await state.set_state(FirstLaunch.select_lang)
        await msg.answer(get("ru", "first_launch_welcome"), reply_markup=lang_kb(), parse_mode="HTML")
        return
    
    await send_menu(msg, state)


@dp.message(F.text == "/help")
async def help_cmd(msg: Message):
    lang = await get_lang(msg.from_user.id)
    lines = {
        "ru": [
            "📖 <b>Справка по боту</b>",
            "<b>➕ Добавить</b> — добавь занятость:\n  1. Выбери день недели\n  2. Укажи час и минуту начала\n  3. Укажи час и минуту окончания\n  4. Повтори для других дней или нажми «Готово»",
            "<b>❌ Удалить</b> — удали занятость, нажав на неё",
            "<b>📋 Моя занятость</b> — посмотреть всё расписание на неделю",
            "<b>⏰ Напоминания</b> — настроить время ежедневних уведомлений",
            "<b>🌍 Часовой пояс</b> — выбрать свой часовой пояс",
            "<b>🌐 Language</b> — переключить язык бота",
            "🔔 Уведомления приходят каждый день в выбранное время.\nБот покажет свободные окна и предложит идеи, чем заняться.",
            "/start — главное меню\n/help — эта справка",
        ],
        "en": [
            "📖 <b>Bot Help</b>",
            "<b>➕ Add</b> — add busy slot:\n  1. Select a day of week\n  2. Set start hour and minute\n  3. Set end hour and minute\n  4. Repeat for other days or press «Done»",
            "<b>❌ Delete</b> — remove a slot by tapping it",
            "<b>📋 My Schedule</b> — view full weekly timetable",
            "<b>⏰ Notifications</b> — set daily notification time",
            "<b>🌍 Timezone</b> — choose your timezone",
            "<b>🌐 Language</b> — switch bot language",
            "🔔 Notifications arrive daily at your chosen time.\nBot shows free windows and suggests activity ideas.",
            "/start — main menu\n/help — this help",
        ],
    }
    text = "\n\n".join(lines.get(lang, lines["ru"]))
    await msg.answer(text, reply_markup=make_persistent_kb(lang), parse_mode="HTML")


@dp.message(F.text == "➕ Добавить")
@dp.message(F.text == "➕ Add")
async def add_text(msg: Message, state: FSMContext):
    lang = await get_lang(msg.from_user.id)
    await state.update_data(selected_day=None)
    await state.set_state(Form.select_day)
    await msg.answer(get(lang, "select_day"), reply_markup=one_day_kb(lang))


@dp.callback_query(Form.select_day, F.data.startswith("oday_"))
async def pick_day(cb: CallbackQuery, state: FSMContext):
    lang = await get_lang(cb.from_user.id)
    d = int(cb.data.split("_")[1])
    await state.update_data(selected_day=d)
    await state.set_state(Form.start_hour)
    await cb.message.edit_text(get(lang, "start_hour"), reply_markup=hours_kb(lang))
    await cb.answer()


@dp.callback_query(Form.start_hour, F.data.startswith("sh_"))
async def pick_start_hour(cb: CallbackQuery, state: FSMContext):
    lang = await get_lang(cb.from_user.id)
    h = int(cb.data.split("_")[1])
    await state.update_data(start_hour=h)
    await state.set_state(Form.start_minute)
    await cb.message.edit_text(get(lang, "start_minute"), reply_markup=minutes_kb(lang))
    await cb.answer()


@dp.callback_query(Form.start_minute, F.data.startswith("sm_"))
async def pick_start_minute(cb: CallbackQuery, state: FSMContext):
    lang = await get_lang(cb.from_user.id)
    m = int(cb.data.split("_")[1])
    await state.update_data(start_minute=m)
    await state.set_state(Form.end_hour)
    await cb.message.edit_text(get(lang, "end_hour"), reply_markup=end_hours_kb(lang))
    await cb.answer()


@dp.callback_query(Form.end_hour, F.data.startswith("eh_"))
async def pick_end_hour(cb: CallbackQuery, state: FSMContext):
    lang = await get_lang(cb.from_user.id)
    h = int(cb.data.split("_")[1])
    await state.update_data(end_hour=h)
    await state.set_state(Form.end_minute)
    await cb.message.edit_text(get(lang, "end_minute"), reply_markup=end_minutes_kb(lang))
    await cb.answer()


@dp.callback_query(Form.end_minute, F.data.startswith("em_"))
async def pick_end_minute(cb: CallbackQuery, state: FSMContext):
    lang = await get_lang(cb.from_user.id)
    m = int(cb.data.split("_")[1])
    await state.update_data(end_minute=m)

    data = await state.get_data()
    day = data["selected_day"]
    sh = data["start_hour"]
    sm = data["start_minute"]
    eh = data["end_hour"]
    em = data["end_minute"]

    start_time = datetime(2000, 1, 1, sh, sm).time()
    end_time = datetime(2000, 1, 1, eh, em).time()

    start_str = f"{sh:02d}:{sm:02d}"
    end_str = f"{eh:02d}:{em:02d}"

    if start_time >= end_time:
        await cb.answer(get(lang, "conflict_time"), show_alert=True)
        return

    conflict = await db.check_conflict(cb.from_user.id, day, start_time, end_time)
    if conflict:
        await cb.answer(get(lang, "conflict_slot"), show_alert=True)
        return

    day_names = {"ru": days_map, "en": ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]}
    dn = day_names.get(lang, day_names["ru"])[day]

    await db.add_user(cb.from_user.id)
    await db.add_busy(cb.from_user.id, day, start_time, end_time)

    text = get(lang, "added").format(day=dn, start=start_str, end=end_str)
    await cb.message.edit_text(text, reply_markup=one_day_kb_with_done(lang))
    await state.set_state(Form.select_day)
    await cb.answer()


@dp.callback_query(Form.select_day, F.data == "done_add")
async def done_adding(cb: CallbackQuery, state: FSMContext):
    lang = await get_lang(cb.from_user.id)
    await state.clear()
    text = make_menu_text(lang)
    kb = make_persistent_kb(lang)
    await cb.message.answer(text, reply_markup=kb, parse_mode="HTML")
    await cb.answer()


@dp.message(F.text == "❌ Удалить")
@dp.message(F.text == "❌ Delete")
async def delete_text(msg: Message):
    lang = await get_lang(msg.from_user.id)
    slots = await db.get_all_busy(msg.from_user.id)
    if not slots:
        await msg.answer(get(lang, "no_busy"))
        return
    slots = sorted(slots, key=lambda s: s["day_of_week"])
    await msg.answer(get(lang, "delete_title"), reply_markup=delete_menu(slots, lang))


@dp.callback_query(F.data.startswith("del_"))
async def del_slot(cb: CallbackQuery):
    lang = await get_lang(cb.from_user.id)
    slot_id = int(cb.data.split("_")[1])
    await db.delete_busy(slot_id)

    slots = await db.get_all_busy(cb.from_user.id)
    if not slots:
        await cb.message.edit_text(get(lang, "no_busy"))
    else:
        slots = sorted(slots, key=lambda s: s["day_of_week"])
        await cb.message.edit_text(get(lang, "delete_title"), reply_markup=delete_menu(slots, lang))
    await cb.answer(get(lang, "deleted"))


@dp.callback_query(F.data == "show_all")
async def show_all(cb: CallbackQuery):
    lang = await get_lang(cb.from_user.id)
    slots = await db.get_all_busy(cb.from_user.id)
    if not slots:
        await cb.message.edit_text(get(lang, "no_busy_list"))
        await cb.answer()
        return

    slots = sorted(slots, key=lambda s: s["day_of_week"])
    day_names = {"ru": days_map, "en": ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]}
    dn = day_names.get(lang, day_names["ru"])

    text = get(lang, "busy_title") + "\n\n"
    current_day = None
    for s in slots:
        day = s["day_of_week"]
        if day != current_day:
            text += f"<b>{dn[day]}</b>\n"
            current_day = day
        start = str(s['start_time'])[:5]
        end = str(s['end_time'])[:5]
        text += f"  • {start} — {end}\n"
    text += "\n"

    back_text = get(lang, "back")
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=f"⬅️ {back_text}", callback_data="back_from_all")]])
    await cb.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await cb.answer()


@dp.callback_query(F.data == "back_from_all")
async def back_from_all(cb: CallbackQuery, state: FSMContext):
    lang = await get_lang(cb.from_user.id)
    await state.clear()
    text = make_menu_text(lang)
    kb = make_persistent_kb(lang)
    await cb.message.answer(text, reply_markup=kb, parse_mode="HTML")
    await cb.answer()


@dp.message(F.text == "📋 Моя занятость")
@dp.message(F.text == "📋 My Schedule")
async def show_all_text(msg: Message):
    lang = await get_lang(msg.from_user.id)
    slots = await db.get_all_busy(msg.from_user.id)
    if not slots:
        await msg.answer(get(lang, "no_busy_list"))
        return

    slots = sorted(slots, key=lambda s: s["day_of_week"])
    day_names = {"ru": days_map, "en": ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]}
    dn = day_names.get(lang, day_names["ru"])

    text = get(lang, "busy_title") + "\n\n"
    current_day = None
    for s in slots:
        day = s["day_of_week"]
        if day != current_day:
            text += f"<b>{dn[day]}</b>\n"
            current_day = day
        start = str(s['start_time'])[:5]
        end = str(s['end_time'])[:5]
        text += f"  • {start} — {end}\n"
    text += "\n"

    await msg.answer(text, parse_mode="HTML")


@dp.message(F.text == "⏰ Напоминания")
@dp.message(F.text == "⏰ Notifications")
async def notification_text(msg: Message, state: FSMContext):
    lang = await get_lang(msg.from_user.id)
    current = await db.get_notification_time(msg.from_user.id)
    current_str = f"{current.hour:02d}:{current.minute:02d}" if current else "09:00"
    await msg.answer(
        get(lang, "notif_current").format(time=current_str),
        reply_markup=notif_hours_kb(lang)
    )
    await state.set_state(Form.notif_hour)


@dp.callback_query(F.data == "notification")
async def notification(cb: CallbackQuery, state: FSMContext):
    lang = await get_lang(cb.from_user.id)
    current = await db.get_notification_time(cb.from_user.id)
    current_str = f"{current.hour:02d}:{current.minute:02d}" if current else "09:00"
    await cb.message.edit_text(
        get(lang, "notif_current").format(time=current_str),
        reply_markup=notif_hours_kb(lang)
    )
    await state.set_state(Form.notif_hour)
    await cb.answer()


@dp.callback_query(Form.notif_hour, F.data.startswith("nh_"))
async def pick_notif_hour(cb: CallbackQuery, state: FSMContext):
    lang = await get_lang(cb.from_user.id)
    h = int(cb.data.split("_")[1])
    await state.update_data(notif_hour=h)
    await state.set_state(Form.notif_minute)
    await cb.message.edit_text(get(lang, "notif_hour"), reply_markup=notif_minutes_kb(lang))
    await cb.answer()


@dp.callback_query(Form.notif_minute, F.data.startswith("nm_"))
async def pick_notif_minute(cb: CallbackQuery, state: FSMContext):
    lang = await get_lang(cb.from_user.id)
    m = int(cb.data.split("_")[1])
    data = await state.get_data()
    h = data["notif_hour"]

    time_obj = datetime(2000, 1, 1, h, m).time()
    time_str = f"{h:02d}:{m:02d}"

    await db.add_user(cb.from_user.id)
    await db.set_notification_time(cb.from_user.id, time_obj)

    if scheduler.sch:
        job_id = f"notif_{cb.from_user.id}"
        try:
            scheduler.sch.remove_job(job_id)
        except:
            pass
        tz_name = await db.get_timezone(cb.from_user.id)
        try:
            import pytz
            tz = pytz.timezone(tz_name)
        except:
            tz = pytz.utc
        scheduler.sch.add_job(notify_user, "cron", hour=h, minute=m,
                    timezone=tz,
                    args=[cb.from_user.id, time_obj, bot, db],
                    id=job_id, replace_existing=True)
        logger.info(f"Rescheduled user {cb.from_user.id} at {h:02d}:{m:02d} ({tz_name})")

    await cb.message.edit_text(get(lang, "notif_set").format(time=time_str))
    await state.clear()
    text = make_menu_text(lang)
    kb = make_persistent_kb(lang)
    await cb.message.answer(text, reply_markup=kb, parse_mode="HTML")
    await cb.answer()


@dp.message(F.text == "🌐 Language")
@dp.message(F.text == "🌐 Язык")
async def lang_select(msg: Message):
    lang = await get_lang(msg.from_user.id)
    await msg.answer(get(lang, "lang_title"), reply_markup=lang_kb())


@dp.message(F.text == "🌍 Часовой пояс")
@dp.message(F.text == "🌍 Timezone")
async def tz_select(msg: Message):
    lang = await get_lang(msg.from_user.id)
    current = await db.get_timezone(msg.from_user.id)
    text = get(lang, "tz_title") + "\n\n" + get(lang, "tz_current").format(tz=current)
    await msg.answer(text, reply_markup=tz_kb(lang))


@dp.callback_query(F.data.startswith("tz_"))
async def set_tz(cb: CallbackQuery, state: FSMContext):
    tz = cb.data.split("_", 1)[1]

    # Check if this is first launch
    current_state = await state.get_state()

    if current_state == FirstLaunch.select_tz.state:
        # First launch completed - create user FIRST, then set timezone
        lang = await get_lang(cb.from_user.id)
        await db.add_user(cb.from_user.id)  # Create user first!
        await db.set_timezone(cb.from_user.id, tz)  # Then set timezone
        
        # Create notification job with selected timezone
        notif_time = await db.get_notification_time(cb.from_user.id)
        if notif_time and scheduler.sch:
            job_id = f"notif_{cb.from_user.id}"
            try:
                scheduler.sch.remove_job(job_id)
            except:
                pass
            try:
                import pytz
                tz_obj = pytz.timezone(tz)
            except:
                tz_obj = pytz.utc
            scheduler.sch.add_job(notify_user, "cron", hour=notif_time.hour, minute=notif_time.minute,
                        timezone=tz_obj,
                        args=[cb.from_user.id, notif_time, bot, db],
                        id=job_id, replace_existing=True)
            logger.info(f"Created notification job for user {cb.from_user.id} at {notif_time.hour:02d}:{notif_time.minute:02d} ({tz})")
        
        await state.clear()
        await cb.answer(get(lang, "tz_set").format(tz=tz))
        await cb.message.answer(get(lang, "first_launch_setup_done"), parse_mode="HTML")
        # Show main menu
        text = make_menu_text(lang)
        kb = make_persistent_kb(lang)
        await cb.message.answer(text, reply_markup=kb, parse_mode="HTML")
    else:
        lang = await get_lang(cb.from_user.id)
        await db.set_timezone(cb.from_user.id, tz)
        await cb.answer(get(lang, "tz_set").format(tz=tz))
        await state.clear()
        text = make_menu_text(lang)
        await cb.message.edit_text(text, parse_mode="HTML")
    await cb.answer()


@dp.callback_query(F.data == "back_from_tz")
async def back_from_tz(cb: CallbackQuery, state: FSMContext):
    lang = await get_lang(cb.from_user.id)
    await state.clear()
    text = make_menu_text(lang)
    await cb.message.edit_text(text, parse_mode="HTML")
    await cb.answer()


@dp.callback_query(F.data == "lang_ru")
async def set_lang_ru(cb: CallbackQuery, state: FSMContext):
    # Check if this is first launch
    current_state = await state.get_state()
    
    # Create user first if not exists
    await db.add_user(cb.from_user.id)
    await db.set_language(cb.from_user.id, "ru")
    
    if current_state == FirstLaunch.select_lang.state:
        # First launch - proceed to timezone selection
        await state.set_state(FirstLaunch.select_tz)
        await cb.message.answer(get("ru", "first_launch_tz"), reply_markup=tz_kb("ru"), parse_mode="HTML")
    else:
        await state.clear()
        text = make_menu_text("ru")
        kb = make_persistent_kb("ru")
        await cb.message.answer(text, reply_markup=kb, parse_mode="HTML")
        await cb.answer(get("ru", "lang_set_ru"), show_alert=True)


@dp.callback_query(F.data == "lang_en")
async def set_lang_en(cb: CallbackQuery, state: FSMContext):
    # Check if this is first launch
    current_state = await state.get_state()
    
    # Create user first if not exists
    await db.add_user(cb.from_user.id)
    await db.set_language(cb.from_user.id, "en")
    
    if current_state == FirstLaunch.select_lang.state:
        # First launch - proceed to timezone selection
        await state.set_state(FirstLaunch.select_tz)
        await cb.message.answer(get("en", "first_launch_tz"), reply_markup=tz_kb("en"), parse_mode="HTML")
    else:
        await state.clear()
        text = make_menu_text("en")
        kb = make_persistent_kb("en")
        await cb.message.answer(text, reply_markup=kb, parse_mode="HTML")
        await cb.answer(get("en", "lang_set_en"), show_alert=True)


@dp.callback_query(Form.start_hour, F.data == "back")
@dp.callback_query(Form.start_minute, F.data == "back")
@dp.callback_query(Form.end_hour, F.data == "back")
@dp.callback_query(Form.end_minute, F.data == "back")
async def back_to_day(cb: CallbackQuery, state: FSMContext):
    lang = await get_lang(cb.from_user.id)
    await state.set_state(Form.select_day)
    await cb.message.edit_text(get(lang, "select_day"), reply_markup=one_day_kb(lang))
    await cb.answer()


@dp.callback_query(Form.notif_hour, F.data == "back")
@dp.callback_query(Form.notif_minute, F.data == "back")
async def back_from_notif(cb: CallbackQuery, state: FSMContext):
    lang = await get_lang(cb.from_user.id)
    await state.clear()
    text = make_menu_text(lang)
    kb = make_persistent_kb(lang)
    await cb.message.answer(text, reply_markup=kb, parse_mode="HTML")
    await cb.answer()


@dp.callback_query(Form.notification, F.data == "back")
@dp.callback_query(Form.select_day, F.data == "back")
@dp.callback_query(F.data == "back")
async def go_back(cb: CallbackQuery, state: FSMContext):
    lang = await get_lang(cb.from_user.id)
    await state.clear()
    text = make_menu_text(lang)
    kb = make_persistent_kb(lang)
    await cb.message.answer(text, reply_markup=kb, parse_mode="HTML")
    await cb.answer()


async def main():
    logger.info("Starting bot...")
    await db.connect()
    logger.info("DB connected")
    await start_scheduler(bot, db)
    logger.info("Scheduler started")
    await dp.start_polling(bot, drop_pending_updates=True)
    logger.info("Bot polling started")


if __name__ == "__main__":
    asyncio.run(main())
