from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
)
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

translations = {
    "start_message": {
        "en": "Hi there! I'm Fun Entertainment Bot.\nType /games to play or /help to see available commands.",
        "ua": "Привіт! Я бот для розваг.\nНапишіть /games щоб грати або /help щоб побачити команди."
    },
    "choose_game": {
        "en": "Choose the game! Let's make some fun!",
        "ua": "Оберіть гру!"
    },
    "help_message": {
        "en": (
            "📋 Available commands:\n"
            "/start — Welcome message\n"
            "/games — Show list of games\n"
            "/language — Choose your language\n"
            "/profile — Show your profile\n"
            "/favorite — Choose your favorite game\n"
            "/help — Show this help message"
        ),
        "ua": (
            "📋 Доступні команди:\n"
            "/start — Привітальне повідомлення\n"
            "/games — Показати список ігор\n"
            "/language — Змінити мову\n"
            "/profile — Переглянути профіль\n"
            "/favorite — Вибрати улюблену гру\n"
            "/help — Показати це повідомлення"
        )
    },
    "profile_title": {
        "en": "👤 <b>Your profile</b>",
        "ua": "👤 <b>Твій профіль</b>"
    },
    "language_name": {
        "en": "English",
        "ua": "Українська"
    },
    "achievements": {
        "en": "🏆 Achievements:",
        "ua": "🏆 Досягнення:"
    },
    "no_achievements": {
        "en": "None yet. Play more games to earn achievements!",
        "ua": "Поки що немає. Грай більше, щоб отримати досягнення!"
    },
    "history_title": {
        "en": "🕓 Recent games:",
        "ua": "🕓 Останні ігри:"
    },
    "choose_favorite": {
        "en": "Choose your favorite game:",
        "ua": "Оберіть улюблену гру:"
    },
    "favorite_set": {
        "en": "❤️ Your favorite game is now: {game}",
        "ua": "❤️ Твоя улюблена гра тепер: {game}"
    },
    "starting_game": {
        "en": "🎮 Starting {game}! Good luck!\n{url}",
        "ua": "🎮 Починаємо {game}! Удачі!\n{url}"
    },
    "no_games_played": {
        "en": "No games played yet.",
        "ua": "Ще не зіграно жодної гри."
    }
}

def translate(key: str, context: ContextTypes.DEFAULT_TYPE) -> str:
    lang = context.user_data.get("language", "en")
    return translations.get(key, {}).get(lang, f"[{key}]")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(translate("start_message", context))

async def games_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🐍 Snake", url="https://telegram-snake.vercel.app/")],
        [InlineKeyboardButton("💣 Saper", url="https://telegram-saper.vercel.app/")],
        [InlineKeyboardButton("🧱 Tetris", url="https://telegram-tetris-indol.vercel.app/")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(translate("choose_game", context), reply_markup=reply_markup)

async def play_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    game_name = query.data
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")

    context.user_data["games_played"] = context.user_data.get("games_played", 0) + 1

    history = context.user_data.get("game_history", [])
    history.append({"name": game_name, "time": now_str})
    if len(history) > 10:
        history.pop(0)
    context.user_data["game_history"] = history
    await check_achievements(context)

    game_urls = {
        "Snake": "https://telegram-snake.vercel.app/",
        "Saper": "https://telegram-saper.vercel.app/",
        "Tetris": "https://telegram-tetris-indol.vercel.app/",
    }
    url = game_urls.get(game_name, "#")

    text = translate("starting_game", context).format(game=game_name, url=url)
    await query.edit_message_text(text)

async def check_achievements(context: ContextTypes.DEFAULT_TYPE):
    played = context.user_data.get("games_played", 0)
    history = context.user_data.get("game_history", [])

    achievements = context.user_data.get("achievements", [])

    if played >= 10 and "🎉 Game Explorer" not in achievements:
        achievements.append("🎉 Game Explorer")

    played_games = {entry["name"] for entry in history}
    required_games = {"Snake", "Saper", "Tetris"}
    if required_games.issubset(played_games) and "🔄 Variety Player" not in achievements:
        achievements.append("🔄 Variety Player")

    context.user_data["achievements"] = achievements

async def favorite_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🐍 Snake", callback_data="fav_Snake")],
        [InlineKeyboardButton("💣 Saper", callback_data="fav_Saper")],
        [InlineKeyboardButton("🧱 Tetris", callback_data="fav_Tetris")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(translate("choose_favorite", context), reply_markup=reply_markup)

async def favorite_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    fav_game = query.data.replace("fav_", "")
    context.user_data["favorite_game"] = fav_game

    text = translate("favorite_set", context).format(game=fav_game)
    await query.edit_message_text(text)

async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang = context.user_data.get("language", "en")
    games_played = context.user_data.get("games_played", 0)
    fav_game = context.user_data.get("favorite_game", "None")
    achievements = context.user_data.get("achievements", [])
    history = context.user_data.get("game_history", [])

    lang_display = translate("language_name", context)

    achievements_text = "\n".join(achievements) if achievements else translate("no_achievements", context)

    recent_games = history[-3:]
    recent_text = (
        "\n".join([f"{g['name']} — {g['time']}" for g in recent_games])
        if recent_games else translate("no_games_played", context)
    )

    text = (
        f"{translate('profile_title', context)}\n"
        f"🪪 Name: {user.first_name}\n"
        f"🌐 Language: {lang_display}\n"
        f"🎮 Games played: {games_played}\n"
        f"❤️ Favorite: {fav_game}\n\n"
        f"{translate('achievements', context)}\n{achievements_text}\n\n"
        f"{translate('history_title', context)}\n{recent_text}"
    )

    await update.message.reply_text(text, parse_mode="HTML")

async def set_commands(application):
    commands = [
        BotCommand("start", "Start the bot"),
        BotCommand("games", "Show list of games"),
        BotCommand("help", "List all commands"),
        BotCommand("language", "Choose your language"),
        BotCommand("profile", "Show your profile"),
        BotCommand("favorite", "Choose your favorite game"),
    ]
    await application.bot.set_my_commands(commands)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(translate("help_message", context))

async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Ukrainian", callback_data="lang_ua")],
        [InlineKeyboardButton("English", callback_data="lang_en")]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Choose your language / Оберіть мову:", reply_markup=markup)

async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    lang_code = query.data.replace("lang_", "")
    context.user_data["language"] = lang_code

    if lang_code == "ua":
        await query.edit_message_text("✅ Мова встановлена: Українська")
    else:
        await query.edit_message_text("✅ Language set to: English")

async def games_callback_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🐍 Snake", callback_data="Snake")],
        [InlineKeyboardButton("💣 Saper", callback_data="Saper")],
        [InlineKeyboardButton("🧱 Tetris", callback_data="Tetris")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(translate("choose_game", context), reply_markup=reply_markup)

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app = ApplicationBuilder().token(BOT_TOKEN).post_init(set_commands).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("games", games_callback_menu))  # теперь с кнопками запуска
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("language", language_command))
    app.add_handler(CommandHandler("profile", profile_command))
    app.add_handler(CommandHandler("favorite", favorite_menu))

    app.add_handler(CallbackQueryHandler(language_callback, pattern="^lang_"))
    app.add_handler(CallbackQueryHandler(favorite_callback, pattern="^fav_"))
    app.add_handler(CallbackQueryHandler(play_game, pattern="^(Snake|Saper|Tetris)$"))

    print("Bot started.")
    app.run_polling()
