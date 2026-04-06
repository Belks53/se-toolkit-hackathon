from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

days = [("Пн",0),("Вт",1),("Ср",2),("Чт",3),("Пт",4),("Сб",5),("Вс",6)]
days_map = ["Пн","Вт","Ср","Чт","Пт","Сб","Вс"]
days_en = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]

def day_names(lang):
    return days_map if lang == "ru" else days_en

def one_day_kb(lang="ru"):
    dn = day_names(lang)
    kb = []
    row = []
    for (name, day), en_name in zip(days, days_en):
        label = name if lang == "ru" else en_name
        row.append(InlineKeyboardButton(text=label, callback_data=f"oday_{day}"))
        if len(row) == 3:
            kb.append(row)
            row = []
    if row:
        kb.append(row)
    done_text = "✅ Готово" if lang == "ru" else "✅ Done"
    kb.append([InlineKeyboardButton(text=done_text, callback_data="done_add")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

def one_day_kb_with_done(lang="ru"):
    dn = day_names(lang)
    kb = []
    row = []
    for (name, day), en_name in zip(days, days_en):
        label = name if lang == "ru" else en_name
        row.append(InlineKeyboardButton(text=label, callback_data=f"oday_{day}"))
        if len(row) == 3:
            kb.append(row)
            row = []
    if row:
        kb.append(row)
    done_text = "✅ Готово" if lang == "ru" else "✅ Done"
    kb.append([InlineKeyboardButton(text=done_text, callback_data="done_add")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

def delete_menu(slots, lang="ru"):
    dn = day_names(lang)
    kb = []
    for s in slots:
        start = str(s['start_time'])[:5]
        end = str(s['end_time'])[:5]
        text = f"{dn[s['day_of_week']]} {start} — {end}"
        kb.append([InlineKeyboardButton(text=text, callback_data=f"del_{s['id']}")])
    back_text = "⬅️ Назад" if lang == "ru" else "⬅️ Back"
    kb.append([InlineKeyboardButton(text=back_text, callback_data="back")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

def notif_hours_kb(lang="ru"):
    kb = []
    row = []
    for h in range(24):
        row.append(InlineKeyboardButton(text=f"{h:02d}", callback_data=f"nh_{h}"))
        if len(row) == 6:
            kb.append(row)
            row = []
    if row:
        kb.append(row)
    back_text = "⬅️ Назад" if lang == "ru" else "⬅️ Back"
    kb.append([InlineKeyboardButton(text=back_text, callback_data="back")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

def notif_minutes_kb(lang="ru"):
    kb = []
    row = []
    for m in [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55]:
        row.append(InlineKeyboardButton(text=f"{m:02d}", callback_data=f"nm_{m}"))
        if len(row) == 4:
            kb.append(row)
            row = []
    if row:
        kb.append(row)
    back_text = "⬅️ Назад" if lang == "ru" else "⬅️ Back"
    kb.append([InlineKeyboardButton(text=back_text, callback_data="back")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

def hours_kb(lang="ru"):
    kb = []
    row = []
    for h in range(24):
        row.append(InlineKeyboardButton(text=f"{h:02d}", callback_data=f"sh_{h}"))
        if len(row) == 6:
            kb.append(row)
            row = []
    if row:
        kb.append(row)
    back_text = "⬅️ Назад" if lang == "ru" else "⬅️ Back"
    kb.append([InlineKeyboardButton(text=back_text, callback_data="back")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

def minutes_kb(lang="ru"):
    kb = []
    row = []
    for m in [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55]:
        row.append(InlineKeyboardButton(text=f"{m:02d}", callback_data=f"sm_{m}"))
        if len(row) == 4:
            kb.append(row)
            row = []
    if row:
        kb.append(row)
    back_text = "⬅️ Назад" if lang == "ru" else "⬅️ Back"
    kb.append([InlineKeyboardButton(text=back_text, callback_data="back")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

def end_hours_kb(lang="ru"):
    kb = []
    row = []
    for h in range(24):
        row.append(InlineKeyboardButton(text=f"{h:02d}", callback_data=f"eh_{h}"))
        if len(row) == 6:
            kb.append(row)
            row = []
    if row:
        kb.append(row)
    back_text = "⬅️ Назад" if lang == "ru" else "⬅️ Back"
    kb.append([InlineKeyboardButton(text=back_text, callback_data="back")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

def end_minutes_kb(lang="ru"):
    kb = []
    row = []
    for m in [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55]:
        row.append(InlineKeyboardButton(text=f"{m:02d}", callback_data=f"em_{m}"))
        if len(row) == 4:
            kb.append(row)
            row = []
    if row:
        kb.append(row)
    back_text = "⬅️ Назад" if lang == "ru" else "⬅️ Back"
    kb.append([InlineKeyboardButton(text=back_text, callback_data="back")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

def lang_kb():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")],
    ])
    return kb

def tz_kb(lang="ru"):
    timezones_ru = [
        ("UTC", "UTC+0"),
        ("Europe/Kaliningrad", "UTC+2 Калининград"),
        ("Europe/Moscow", "UTC+3 Москва"),
        ("Europe/Samara", "UTC+4 Самара"),
        ("Asia/Yekaterinburg", "UTC+5 Екатеринбург"),
        ("Asia/Omsk", "UTC+6 Омск"),
        ("Asia/Krasnoyarsk", "UTC+7 Красноярск"),
        ("Asia/Irkutsk", "UTC+8 Иркутск"),
        ("Asia/Yakutsk", "UTC+9 Якутск"),
        ("Asia/Vladivostok", "UTC+10 Владивосток"),
        ("Asia/Magadan", "UTC+11 Магадан"),
        ("Asia/Kamchatka", "UTC+12 Камчатка"),
        ("Europe/London", "UTC+0 Лондон"),
        ("Europe/Berlin", "UTC+1 Берлин"),
        ("Europe/Paris", "UTC+1 Париж"),
        ("America/New_York", "UTC-5 Нью-Йорк"),
        ("America/Chicago", "UTC-6 Чикаго"),
        ("America/Denver", "UTC-7 Денвер"),
        ("America/Los_Angeles", "UTC-8 Лос-Анджелес"),
    ]
    timezones_en = [
        ("UTC", "UTC+0"),
        ("Europe/Kaliningrad", "UTC+2 Kaliningrad"),
        ("Europe/Moscow", "UTC+3 Moscow"),
        ("Europe/Samara", "UTC+4 Samara"),
        ("Asia/Yekaterinburg", "UTC+5 Yekaterinburg"),
        ("Asia/Omsk", "UTC+6 Omsk"),
        ("Asia/Krasnoyarsk", "UTC+7 Krasnoyarsk"),
        ("Asia/Irkutsk", "UTC+8 Irkutsk"),
        ("Asia/Yakutsk", "UTC+9 Yakutsk"),
        ("Asia/Vladivostok", "UTC+10 Vladivostok"),
        ("Asia/Magadan", "UTC+11 Magadan"),
        ("Asia/Kamchatka", "UTC+12 Kamchatka"),
        ("Europe/London", "UTC+0 London"),
        ("Europe/Berlin", "UTC+1 Berlin"),
        ("Europe/Paris", "UTC+1 Paris"),
        ("America/New_York", "UTC-5 New York"),
        ("America/Chicago", "UTC-6 Chicago"),
        ("America/Denver", "UTC-7 Denver"),
        ("America/Los_Angeles", "UTC-8 Los Angeles"),
    ]
    timezones = timezones_en if lang == "en" else timezones_ru
    back_text = "⬅️ Назад" if lang == "ru" else "⬅️ Back"
    kb = []
    row = []
    for tz, label in timezones:
        row.append(InlineKeyboardButton(text=label, callback_data=f"tz_{tz}"))
        if len(row) == 2:
            kb.append(row)
            row = []
    if row:
        kb.append(row)
    kb.append([InlineKeyboardButton(text=back_text, callback_data="back_from_tz")])
    return InlineKeyboardMarkup(inline_keyboard=kb)
