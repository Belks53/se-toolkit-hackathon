"""
Localization and Fallback Messages Module
==========================================
Contains all user-facing text strings in Russian and English.

Structure:
- T: Translation dictionary with keys for every UI message
- FALLBACK_* lists: Pre-written activity suggestions (30 each per time period)
- get(): Translation lookup function with fallback to Russian
- get_fallback_messages(): Random suggestion for a single time period
- get_fallback_for_slots(): Unique suggestions for each free slot
"""

T = {
    "ru": {
        "menu_title": "⏰ <b>Time Manager</b>",
        "menu_desc": "Управляй своим временем легко!",
        "menu_add": "➕ <b>Добавить</b> — занять интервал",
        "menu_delete": "❌ <b>Удалить</b> — убрать интервал",
        "menu_busy": "📋 <b>Моя занятость</b> — всё расписание",
        "menu_notif": "⏰ <b>Напоминания</b> — время уведомлений",
        "menu_help": "📖 <b>Справка</b> — /help",
        "select_day": "Выбери день:",
        "start_hour": "⏰ Час начала:",
        "start_minute": "⏱ Минуты начала:",
        "end_hour": "⏰ Час окончания:",
        "end_minute": "⏱ Минуты окончания:",
        "added": "✅ Добавлено: {day} {start}-{end}\n\nВыбери день для нового интервала:",
        "done": "Готово",
        "no_busy": "Нет занятости",
        "delete_title": "Удалить:",
        "deleted": "Удалено",
        "busy_title": "📅 <b>Твоя занятость:</b>",
        "no_busy_list": "У тебя нет занятости",
        "notif_current": "Текущее время: {time}\n⏰ Час напоминания:",
        "notif_hour": "⏱ Минуты напоминания:",
        "notif_set": "✅ Время напоминаний установлено на {time}",
        "conflict_time": "Начало должно быть раньше окончания!",
        "conflict_slot": "⚠️ Это время пересекается с другой занятостью!",
        "help_title": "📖 <b>Справка по боту</b>",
        "help_add": "➕ <b>Добавить</b> — добавь занятость:\n  1. Выбери день недели\n  2. Укажи час и минуту начала\n  3. Укажи час и минуту окончания",
        "help_del": "❌ <b>Удалить</b> — удали занятость кнопкой",
        "help_busy": "📋 <b>Моя занятость</b> — посмотреть всё расписание",
        "help_notif": "⏰ <b>Напоминания</b> — настроить время уведомлений",
        "help_info": "🔔 Уведомления приходят каждый день в выбранное время\nБот покажет свободные окна и предложит идеи",
        "help_start": "/start — главное меню",
        "help_help": "/help — эта справка",
        "lang_title": "🌐 Выбери язык / Choose language:",
        "lang_set_ru": "✅ Язык изменён на русский",
        "lang_set_en": "✅ Language changed to English",
        "back": "⬅️ Назад",
        "free_time": "📅 Свободное время:",
        "no_suggestions": "Нет предложений",
        "tz_title": "🌍 Выбери часовой пояс:",
        "tz_current": "Текущий: {tz}",
        "tz_set": "✅ Часовой пояс установлен: {tz}",
        "tz_btn": "🌍 Часовой пояс",
        "first_launch_welcome": "👋 Добро пожаловать в <b>Time Manager</b>!\n\nПрежде чем начать, выбери язык интерфейса:",
        "first_launch_tz": "Отлично! Теперь выбери свой часовой пояс:",
        "first_launch_setup_done": "✅ Настройки сохранены!\n\nТеперь ты можешь пользоваться ботом. Нажми /start для начала.",
    },
    "en": {
        "menu_title": "⏰ <b>Time Manager</b>",
        "menu_desc": "Manage your time easily!",
        "menu_add": "➕ <b>Add</b> — busy slot",
        "menu_delete": "❌ <b>Delete</b> — remove slot",
        "menu_busy": "📋 <b>My Schedule</b> — full timetable",
        "menu_notif": "⏰ <b>Notifications</b> — notification time",
        "menu_help": "📖 <b>Help</b> — /help",
        "select_day": "Select a day:",
        "start_hour": "⏰ Start hour:",
        "start_minute": "⏱ Start minute:",
        "end_hour": "⏰ End hour:",
        "end_minute": "⏱ End minute:",
        "added": "✅ Added: {day} {start}-{end}\n\nSelect a day for another slot:",
        "done": "Done",
        "no_busy": "No busy slots",
        "delete_title": "Delete:",
        "deleted": "Deleted",
        "busy_title": "📅 <b>Your Schedule:</b>",
        "no_busy_list": "You have no busy slots",
        "notif_current": "Current time: {time}\n⏰ Notification hour:",
        "notif_hour": "⏱ Notification minute:",
        "notif_set": "✅ Notification time set to {time}",
        "conflict_time": "Start must be before end!",
        "conflict_slot": "⚠️ This time overlaps with another slot!",
        "help_title": "📖 <b>Bot Help</b>",
        "help_add": "➕ <b>Add</b> — add busy slot:\n  1. Select a day of week\n  2. Set start hour and minute\n  3. Set end hour and minute",
        "help_del": "❌ <b>Delete</b> — remove a slot with button",
        "help_busy": "📋 <b>My Schedule</b> — view full timetable",
        "help_notif": "⏰ <b>Notifications</b> — set notification time",
        "help_info": "🔔 Notifications arrive daily at your chosen time\nBot shows free windows and suggests ideas",
        "help_start": "/start — main menu",
        "help_help": "/help — this help",
        "lang_title": "🌐 Choose language / Выбери язык:",
        "lang_set_ru": "✅ Язык изменён на русский",
        "lang_set_en": "✅ Language changed to English",
        "back": "⬅️ Back",
        "free_time": "📅 Free time:",
        "no_suggestions": "No suggestions",
        "tz_title": "🌍 Choose timezone:",
        "tz_current": "Current: {tz}",
        "tz_set": "✅ Timezone set to: {tz}",
        "tz_btn": "🌍 Timezone",
        "first_launch_welcome": "👋 Welcome to <b>Time Manager</b>!\n\nBefore we start, please choose your interface language:",
        "first_launch_tz": "Great! Now choose your timezone:",
        "first_launch_setup_done": "✅ Settings saved!\n\nNow you can use the bot. Press /start to begin.",
    }
}

def get(user_lang, key):
    """
    Look up a translation string for the given language and key.
    Falls back to Russian if the language or key is missing.

    Args:
        user_lang: Language code ("ru" or "en").
        key: Translation key from the T dictionary.

    Returns:
        Translated string, or the key itself if not found.
    """
    return T.get(user_lang, T["ru"]).get(key, T["ru"].get(key, key))

import random

FALLBACK_MORNING_RU = [
    "🌅 Доброе утро! Начни день с зарядки — это бодрит лучше кофе!",
    "☀️ Утро — лучшее время для пробежки. Свежий воздух зарядит энергией!",
    "🧘‍♂️ Утром отлично подходит для медитации. 10 минут тишины зададут тон всему дню!",
    "📚 Посвяти утро чтению — даже 15 минут расширят кругозор!",
    "🎵 Включи любимую музыку и потанцуй — отличный способ проснуться!",
    "🍳 Приготовь вкусный завтрак — правильное начало дня важно!",
    "✍️ Утром хорошо писать в дневник или планировать день — мысли станут яснее!",
    "🚶‍♂️ Утренняя прогулка поможет проснуться и настроиться на день!",
    "🎨 Попробуй порисовать — творчество с утра вдохновляет!",
    "💪 Сделай утреннюю тренировку — тело скажет спасибо!",
    "🧹 Утренняя уборка — порядок дома, порядок в голове!",
    "📝 Выучи 10 новых слов на иностранном языке — утро для этого идеально!",
    "🎯 Утром хорошо ставить цели на день — фокус и продуктивность!",
    "🥤 Приготовь свежий смузи — витамины и энергия на весь день!",
    "🧠 Реши головоломку или кроссворд — разминка для мозга с утра!",
    "🌻 Полей цветы и позаботься о растениях — забота о природе успокаивает!",
    "🏊‍♂️ Утреннее плавание — отличный способ активировать все мышцы!",
    "🎸 Попрактикуйся в игре на музыкальном инструменте — утро для музыки!",
    "🥗 Приготовь здоровый завтрак — овсянка, фрукты и орехи!",
    "📱 Сделай цифровую детоксикацию — отложи телефон на 30 минут!",
    "🧘‍♀️ Йога утром — гибкость и баланс на весь день!",
    "🌳 Выйди на балкон или в парк — природа с утра восстанавливает!",
    "💭 Составь список благодарности — 3 вещи, за которые ты благодарен!",
    "🏃‍♀️ Интервальный бег — 30 секунд быстро, 30 секунд медленно, 10 минут!",
    "🎯 Сделай доску визуализации — мечты станут ближе!",
    "📖 Читай мотивирующую книгу — настройся на успех!",
    "🎬 Посмотри TED talk — вдохновение и новые идеи!",
    "🧹 Разбери один ящик или полку — маленький порядок ведёт к большому!",
    "☕ Приготовь кофе по-новому рецепту — экспериментируй с утра!",
    "🌈 Спланируй что-то приятное на сегодня — ожидание уже радует!",
]

FALLBACK_AFTERNOON_RU = [
    "🌞 День — время активности! Попробуй новый вид спорта!",
    "💼 Послеобеденное время идеально для работы над проектом!",
    "🚴‍♂️ Прогулка на велосипеде — отличный способ провести день!",
    "🎸 Попробуй освоить музыкальный инструмент — день для творчества!",
    "🏃‍♂️ Сходи на пробежку в парк — свежий воздух и движение!",
    "📖 Читай книгу — послеобеденное время для погружения в знания!",
    "🎬 Посмотри документальный фильм — узнай что-то новое!",
    "🧑‍🍳 Приготовь новое блюдо — кулинария это творчество!",
    "🤝 Встреться с другом — общение заряжает позитивом!",
    "🏋️‍♂️ Сходи в тренажерный зал — день для силы и энергии!",
    "📸 Попробуй фотографию — лови моменты и развивай взгляд!",
    "🌿 Проведи время на природе — растения и свежий воздух восстанавливают!",
    "🎲 Поиграй в настольные игры — весело и развивает мышление!",
    "📝 Напиши пост в блог или статью — делись знаниями с миром!",
    "🔧 Займись рукоделием или почини что-то — практика важна!",
    "🎯 Начни изучать новый навык — день для роста!",
    "🏊‍♀️ Плавание — отличная дневная активность для всего тела!",
    "🎨 Рисуй или раскрашивай — творчество в разгар дня!",
    "🧩 Собери пазл или головоломку — тренировка логики!",
    "🌳 Пикник в парке — свежий воздух и вкусная еда!",
    "🎭 Сходи на выставку или в музей — культурная программа!",
    "🏀 Поиграй в командный спорт — баскетбол, волейбол, футбол!",
    "📚 Посети библиотеку или книжный — выбери что-то интересное!",
    "🎵 Создай новый плейлист — музыка для настроения!",
    "🧘‍♂️ Дневная медитация — перезагрузка среди дня!",
    "🍕 Освой новый рецепт — удиви себя и близких!",
    "📝 Составь список целей на месяц — фокус на результате!",
    "🎮 Поиграй в развивающую игру — время для стратегии!",
    "🌺 Займись садоводством — растения радуют глаз!",
    "💡 Придумай идеальный проект — день для идей!",
]

FALLBACK_EVENING_RU = [
    "🌆 Вечер — время расслабления. Спокойная прогулка поможет уснуть!",
    "🛁 Тёплая ванна с солью — идеальный вечерний ритуал!",
    "📺 Посмотри хороший фильм — отдых после напряжённого дня!",
    "🎵 Послушай спокойную музыку — расслабься и отдохни!",
    "🧘‍♀️ Вечерняя медитация поможет снять стресс и подготовиться ко сну!",
    "📚 Чтение перед сном — классика для спокойного вечера!",
    "🍵 Выпей травяной чай с мёдом — уют и тепло вечера!",
    "✍️ Вечером хорошо писать дневник — подведи итоги дня!",
    "🎨 Рисование или раскраски — творческий вечерний отдых!",
    "🧩 Собери пазл — спокойное занятие для вечера!",
    "💆‍♂️ Сделай самомассаж — тело расслабится и отдохнёт!",
    "🌟 Спланируй завтрашний день — вечер для организации!",
    "🎮 Поиграй в спокойную игру — время для развлечения!",
    "📝 Поучись чему-то новому онлайн — вечер для саморазвития!",
    "🤗 Позвони близким — общение с семьёй согревает душу!",
    "🎬 Посмотри комедию — смех снимает стресс!",
    "🌙 Вечерняя прогулка под звёздами — романтика и покой!",
    "🧘‍♂️ Йога нидра — глубокое расслабление перед сном!",
    "🍷 Бокал вина и сыр — вечерний релакс для гурмана!",
    "📖 Читай художественную литературу — погружение в другой мир!",
    "🎵 Создай вечерний плейлист — музыка для отдыха!",
    "🕯 Зажги ароматические свечи — атмосфера уюта!",
    "🧹 Лёгкая уборка — порядок создаёт спокойствие!",
    "🎸 Поиграй на гитаре или пианино — вечерняя мелодия!",
    "📸 Просмотри старые фото — ностальгия и тёплые воспоминания!",
    "🌿 Уход за растениями — спокойное вечернее занятие!",
    "💭 Мечтай и фантазируй — вечер для воображения!",
    "🎲 Настольная игра с семьёй — весёлый вечер!",
    "🍳 Приготовь что-то простое и вкусное — кулинарный вечер!",
    "📝 Напиши письмо себе в будущее — послание завтрашнему дню!",
]

FALLBACK_NIGHT_RU = [
    "🌙 Поздний вечер — время тишины. Отдохни и наберись сил!",
    "⭐ Посмотри на звёзды — ночное небо вдохновляет!",
    "📖 Читай спокойную книгу — время для глубоких мыслей!",
    "🎵 Включи тихую музыку — пусть ночь будет спокойной!",
    "🧘‍♂️ Глубокая медитация перед сном — путь к внутреннему покою!",
    "🌌 Подумай о хорошем, что было сегодня — благодарность перед сном!",
    "💤 Подготовка ко сну важна — выключи экраны и расслабься!",
    "📝 Запиши мысли в дневник — освободи голову перед сном!",
    "🌿 Чай с ромашкой поможет уснуть — натуральный релаксант!",
    "🎨 Вечернее рисование — спокойное творчество перед сном!",
    "🕯 Зажги свечи — создай уютную атмосферу вечера!",
    "🧠 Решай спокойные головоломки — мягкая нагрузка для ума!",
    "💭 Помечтай о будущем — ночь время для фантазий!",
    "📱 Отложи телефон за час до сна — пусть отдых будет полным!",
    "🌙 Ночная тишина — лучшее время для самоанализа!",
    "🌠 Пожелай что-нибудь на падающую звезду — магия ночи!",
    "📚 Аудиокнига в темноте — закрой глаза и слушай!",
    "🎧 Послушай подкаст — интересные истории на ночь!",
    "🌃 Ночная прогулка — город спит, а ты наслаждайся тишиной!",
    "✍️ Напиши рассказ или стих — ночное вдохновение!",
    "🧘‍♀️ Дыхательные упражнения — успокой ум и тело!",
    "🌙 Лунная йога — мягкие позы для расслабления!",
    "🎵 Звуки природы для сна — шум дождя или океана!",
    "💜 Визуализируй спокойное место — мысленно отправляйся туда!",
    "📝 Составь список целей на завтра — день будет продуктивным!",
    "🌲 Ароматерапия лавандой — естественное успокоительное!",
    "🌊 Посмотри на воду — фонтан или аквариум умиротворяют!",
    "🔮 Подумай о своих достижениях — ты молодец, отдыхай!",
    "🌌 Космические документалы — бесконечность вселенной убаюкивает!",
    "💫 Запиши 3 хороших события дня — благодарность помогает спать крепче!",
]

FALLBACK_MORNING_EN = [
    "🌅 Good morning! Start your day with a workout — it energizes better than coffee!",
    "☀️ Morning is the best time for a run. Fresh air will charge you with energy!",
    "🧘‍♂️ Morning is perfect for meditation. 10 minutes of silence set the tone for the day!",
    "📚 Dedicate your morning to reading — even 15 minutes broaden your horizons!",
    "🎵 Play your favorite music and dance — a great way to wake up!",
    "🍳 Cook a tasty breakfast — a proper start to the day matters!",
    "✍️ Morning is good for journaling or planning the day — thoughts become clearer!",
    "🚶‍♂️ A morning walk helps you wake up and tune in for the day!",
    "🎨 Try drawing — creativity in the morning is inspiring!",
    "💪 Do a morning workout — your body will thank you!",
    "🧹 Morning cleaning — order at home, order in your head!",
    "📝 Learn 10 new words in a foreign language — morning is ideal for this!",
    "🎯 Morning is great for setting daily goals — focus and productivity!",
    "🥤 Make a fresh smoothie — vitamins and energy for the whole day!",
    "🧠 Solve a puzzle or crossword — a warm-up for the brain in the morning!",
    "🌻 Water your plants and care for nature — nurturing is calming!",
    "🏊‍♂️ Morning swimming — a great way to activate all muscles!",
    "🎸 Practice a musical instrument — morning is for music!",
    "🥗 Make a healthy breakfast — oatmeal, fruits and nuts!",
    "📱 Digital detox — put away your phone for 30 minutes!",
    "🧘‍♀️ Morning yoga — flexibility and balance for the day!",
    "🌳 Go to the balcony or park — nature in the morning restores!",
    "💭 Make a gratitude list — 3 things you're thankful for!",
    "🏃‍♀️ Interval running — 30 sec fast, 30 sec slow, 10 minutes!",
    "🎯 Create a vision board — dreams become closer!",
    "📖 Read a motivational book — tune in for success!",
    "🎬 Watch a TED talk — inspiration and new ideas!",
    "🧹 Organize one drawer or shelf — small order leads to big!",
    "☕ Make coffee with a new recipe — experiment in the morning!",
    "🌈 Plan something nice for today — anticipation is already joy!",
]

FALLBACK_AFTERNOON_EN = [
    "🌞 Afternoon is the time for action! Try a new sport!",
    "💼 Afternoon is ideal for working on a project!",
    "🚴‍♂️ A bike ride — a great way to spend the afternoon!",
    "🎸 Try mastering a musical instrument — afternoon for creativity!",
    "🏃‍♂️ Go for a run in the park — fresh air and movement!",
    "📖 Read a book — afternoon is time for deep dive into knowledge!",
    "🎬 Watch a documentary — learn something new!",
    "🧑‍🍳 Cook a new dish — cooking is creativity!",
    "🤝 Meet a friend — socializing charges you with positivity!",
    "🏋️‍♂️ Go to the gym — a day for strength and energy!",
    "📸 Try photography — capture moments and develop your vision!",
    "🌿 Spend time in nature — plants and fresh air restore!",
    "🎲 Play board games — fun and develops thinking!",
    "📝 Write a blog post or article — share your knowledge with the world!",
    "🔧 Do crafts or fix something — practice is important!",
    "🎯 Start learning a new skill — afternoon for growth!",
    "🏊‍♀️ Swimming — a great full-body daytime activity!",
    "🎨 Paint or color — creativity in the middle of the day!",
    "🧩 Assemble a puzzle or brain teaser — logic training!",
    "🌳 Picnic in the park — fresh air and tasty food!",
    "🎭 Visit an exhibition or museum — cultural program!",
    "🏀 Play team sports — basketball, volleyball, football!",
    "📚 Visit a library or bookstore — pick something interesting!",
    "🎵 Create a new playlist — music for mood!",
    "🧘‍♂️ Afternoon meditation — midday reboot!",
    "🍕 Master a new recipe — surprise yourself and loved ones!",
    "📝 Make a monthly goal list — focus on results!",
    "🎮 Play a strategy game — time for tactics!",
    "🌺 Do gardening — plants please the eye!",
    "💡 Come up with the perfect project — afternoon for ideas!",
]

FALLBACK_EVENING_EN = [
    "🌆 Evening is time for relaxation. A calm walk helps you sleep!",
    "🛁 A warm bath with salt — the perfect evening ritual!",
    "📺 Watch a good movie — rest after a hard day!",
    "🎵 Listen to calm music — relax and unwind!",
    "🧘‍♀️ Evening meditation helps relieve stress and prepare for sleep!",
    "📚 Reading before bed — a classic for a calm evening!",
    "🍵 Drink herbal tea with honey — coziness and warmth of the evening!",
    "✍️ Evening is good for journaling — sum up the day!",
    "🎨 Drawing or coloring — creative evening relaxation!",
    "🧩 Assemble a puzzle — a calm activity for the evening!",
    "💆‍♂️ Do self-massage — your body will relax and rest!",
    "🌟 Plan tomorrow — evening for organization!",
    "🎮 Play a calm game — time for entertainment!",
    "📝 Learn something new online — evening for self-development!",
    "🤗 Call your loved ones — family communication warms the soul!",
    "🎬 Watch a comedy — laughter relieves stress!",
    "🌙 Evening walk under the stars — romance and peace!",
    "🧘‍♂️ Yoga nidra — deep relaxation before sleep!",
    "🍷 A glass of wine and cheese — evening relaxation for a gourmet!",
    "📖 Read fiction — immersion in another world!",
    "🎵 Create an evening playlist — music for rest!",
    "🕯 Light aromatic candles — an atmosphere of coziness!",
    "🧹 Light cleaning — order creates calm!",
    "🎸 Play guitar or piano — an evening melody!",
    "📸 Browse old photos — nostalgia and warm memories!",
    "🌿 Plant care — a calm evening hobby!",
    "💭 Dream and imagine — evening for imagination!",
    "🎲 Board game with family — a fun evening!",
    "🍳 Cook something simple and tasty — a culinary evening!",
    "📝 Write a letter to your future self — a message to tomorrow!",
]

FALLBACK_NIGHT_EN = [
    "🌙 Late evening is time for silence. Rest and gather strength!",
    "⭐ Look at the stars — the night sky is inspiring!",
    "📖 Read a calm book — time for deep thoughts!",
    "🎵 Play quiet music — let the night be peaceful!",
    "🧘‍♂️ Deep meditation before sleep — a path to inner peace!",
    "🌌 Think about the good things today — gratitude before sleep!",
    "💤 Preparing for sleep is important — turn off screens and relax!",
    "📝 Write thoughts in a journal — clear your head before sleep!",
    "🌿 Chamomile tea helps you sleep — a natural relaxant!",
    "🎨 Evening drawing — calm creativity before sleep!",
    "🕯 Light candles — create a cozy evening atmosphere!",
    "🧠 Solve calm puzzles — gentle mental load!",
    "💭 Dream about the future — night is time for fantasies!",
    "📱 Put away your phone an hour before sleep — let rest be complete!",
    "🌙 Night silence is the best time for self-reflection!",
    "🌠 Make a wish on a shooting star — the magic of the night!",
    "📚 Audiobook in the dark — close your eyes and listen!",
    "🎧 Listen to a podcast — interesting bedtime stories!",
    "🌃 Night walk — the city sleeps, enjoy the silence!",
    "✍️ Write a story or poem — nighttime inspiration!",
    "🧘‍♀️ Breathing exercises — calm your mind and body!",
    "🌙 Moon yoga — gentle poses for relaxation!",
    "🎵 Nature sounds for sleep — rain or ocean noise!",
    "💜 Visualize a peaceful place — mentally travel there!",
    "📝 Make a to-do list for tomorrow — the day will be productive!",
    "🌲 Lavender aromatherapy — a natural calmant!",
    "🌊 Watch water — a fountain or aquarium is soothing!",
    "🔮 Think about your achievements — you did great, rest!",
    "🌌 Space documentaries — the infinity of the universe lulls you!",
    "💫 Write down 3 good events of the day — gratitude helps sleep better!",
]

def get_fallback_messages(period, lang="ru"):
    """Get random fallback message for a time period"""
    period_map = {
        "morning": (FALLBACK_MORNING_RU, FALLBACK_MORNING_EN),
        "afternoon": (FALLBACK_AFTERNOON_RU, FALLBACK_AFTERNOON_EN),
        "evening": (FALLBACK_EVENING_RU, FALLBACK_EVENING_EN),
        "night": (FALLBACK_NIGHT_RU, FALLBACK_NIGHT_EN),
    }

    if period not in period_map:
        period = "afternoon"

    ru_msgs, en_msgs = period_map[period]
    msgs = ru_msgs if lang == "ru" else en_msgs
    return random.choice(msgs)


def get_fallback_for_slots(free_slots, lang="ru"):
    """
    Generate fallback messages for each free slot.
    free_slots — список строк вида ["09:00-11:30", "14:00-16:00"]
    Возвращает словарь {slot: message}
    """
    # Определяем период для каждого слота
    def get_period_for_slot(slot):
        try:
            start_str = slot.split("-")[0]
            hour = int(start_str.split(":")[0])
            if 5 <= hour < 12:
                return "morning"
            elif 12 <= hour < 17:
                return "afternoon"
            elif 17 <= hour < 22:
                return "evening"
            else:
                return "night"
        except:
            return "afternoon"

    result = {}
    used_messages = set()

    for slot in free_slots:
        period = get_period_for_slot(slot)
        period_map = {
            "morning": (FALLBACK_MORNING_RU, FALLBACK_MORNING_EN),
            "afternoon": (FALLBACK_AFTERNOON_RU, FALLBACK_AFTERNOON_EN),
            "evening": (FALLBACK_EVENING_RU, FALLBACK_EVENING_EN),
            "night": (FALLBACK_NIGHT_RU, FALLBACK_NIGHT_EN),
        }

        ru_msgs, en_msgs = period_map.get(period, period_map["afternoon"])
        msgs = ru_msgs if lang == "ru" else en_msgs

        # Выбираем случайное сообщение, стараясь не повторяться
        available = [m for m in msgs if m not in used_messages]
        if not available:
            available = msgs  # Если все использованы, сбрасываем
            used_messages = set()

        msg = random.choice(available)
        used_messages.add(msg)
        result[slot] = msg

    return result
