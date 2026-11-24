
"""Головний Telegram-бот Game Deal Radar."""

import random
import html
import telebot
from telebot import types

import handlers
from steam import get_steam_deals, search_steam_game
from epic import get_epic_deals, get_epic_free_games
from config import require_token


bot = telebot.TeleBot(require_token())



bot.set_my_commands([
    types.BotCommand("start", "Запустити бота"),
    types.BotCommand("help", "Допомога"),
    types.BotCommand("deals", "Усі знижки"),
    types.BotCommand("steam", "Знижки Steam"),
    types.BotCommand("epic", "Знижки Epic Games"),
    types.BotCommand("free", "Безкоштовні ігри"),
    types.BotCommand("search", "Пошук гри"),
    types.BotCommand("top", "ТОП-10 знижок"),
    types.BotCommand("random", "Випадкова гра")
])



def main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        row_width=2
    )

    keyboard.add("Усі знижки", "Steam")
    keyboard.add("Epic Games", "Безкоштовні ігри")
    keyboard.add("Пошук гри", "ТОП-10")
    keyboard.add("Випадкова гра", "Допомога")

    return keyboard



def get_all_deals():
    games = []

    try:
        games.extend(get_steam_deals(limit=10))
    except Exception as error:
        print(f"Помилка Steam: {error}")

    try:
        games.extend(get_epic_deals(limit=10))
    except Exception as error:
        print(f"Помилка Epic Games: {error}")

    return games



def send_games(chat_id, games, title):
    if not games:
        bot.send_message(
            chat_id,
            "Ігор не знайдено або магазини тимчасово недоступні."
        )
        return

    bot.send_message(chat_id, title)

    for game in games:
        try:
            text = handlers.format_game(game)

            bot.send_message(
                chat_id,
                text,
                parse_mode="HTML",
                disable_web_page_preview=True
            )

        except Exception as error:
            print(f"Помилка відправлення гри: {error}")

            bot.send_message(
                chat_id,
                "Не вдалося показати цю гру."
            )



@bot.message_handler(commands=["start"])
def on_start(message):
    name = (
        message.from_user.first_name
        if message.from_user else "користувач"
    )

    bot.send_message(
        message.chat.id,
        handlers.start_text(name),
        reply_markup=main_keyboard()
    )



@bot.message_handler(commands=["help"])
def on_help(message):
    bot.send_message(
        message.chat.id,
        handlers.help_text(),
        reply_markup=main_keyboard()
    )



@bot.message_handler(commands=["deals"])
def on_deals(message):
    bot.send_message(
        message.chat.id,
        "Шукаю актуальні знижки..."
    )

    games = get_all_deals()

    send_games(
        message.chat.id,
        games,
        "Актуальні знижки Steam та Epic Games:"
    )



@bot.message_handler(commands=["steam"])
def on_steam(message):
    bot.send_message(
        message.chat.id,
        "Шукаю знижки Steam..."
    )

    try:
        games = get_steam_deals(limit=10)

        send_games(
            message.chat.id,
            games,
            "Знижки Steam:"
        )

    except Exception as error:
        print(error)

        bot.send_message(
            message.chat.id,
            "Не вдалося отримати знижки Steam."
        )



@bot.message_handler(commands=["epic"])
def on_epic(message):
    bot.send_message(
        message.chat.id,
        "Шукаю пропозиції Epic Games..."
    )

    games = []

    try:
        games.extend(get_epic_deals(limit=10))
    except Exception as error:
        print(f"Epic deals: {error}")

    try:
        games.extend(get_epic_free_games())
    except Exception as error:
        print(f"Epic free games: {error}")

    send_games(
        message.chat.id,
        games,
        "Пропозиції Epic Games:"
    )



@bot.message_handler(commands=["free"])
def on_free(message):
    bot.send_message(
        message.chat.id,
        "Шукаю безкоштовні ігри..."
    )

    try:
        games = get_epic_free_games()

        send_games(
            message.chat.id,
            games,
            "Безкоштовні ігри Epic Games:"
        )

    except Exception as error:
        print(error)

        bot.send_message(
            message.chat.id,
            "Не вдалося отримати безкоштовні ігри."
        )



@bot.message_handler(commands=["top"])
def on_top(message):
    bot.send_message(
        message.chat.id,
        "Формую ТОП-10 знижок..."
    )

    games = get_all_deals()

    games = handlers.top_games(
        games,
        limit=10
    )

    send_games(
        message.chat.id,
        games,
        "ТОП-10 найбільших знижок:"
    )



@bot.message_handler(commands=["random"])
def on_random(message):
    games = get_all_deals()

    if not games:
        bot.send_message(
            message.chat.id,
            "Наразі немає доступних пропозицій."
        )
        return

    game = random.choice(games)

    bot.send_message(
        message.chat.id,
        "Випадкова гра:"
    )

    bot.send_message(
        message.chat.id,
        handlers.format_game(game),
        parse_mode="HTML",
        disable_web_page_preview=True
    )



def perform_search(message, query):
    query = query.strip()

    if not query:
        bot.send_message(
            message.chat.id,
            "Введи назву гри."
        )
        return

    bot.send_message(
        message.chat.id,
        f"Шукаю гру: {html.escape(query)}..."
    )

    games = []

    try:
        games.extend(search_steam_game(query))
    except Exception as error:
        print(f"Steam search: {error}")

    try:
        epic_games = get_epic_deals(limit=50)

        games.extend(
            handlers.search_games(epic_games, query)
        )
    except Exception as error:
        print(f"Epic search: {error}")

    try:
        free_games = get_epic_free_games()

        games.extend(
            handlers.search_games(free_games, query)
        )
    except Exception as error:
        print(f"Epic free search: {error}")

    if not games:
        bot.send_message(
            message.chat.id,
            f"Гру «{html.escape(query)}» не знайдено."
        )
        return

    send_games(
        message.chat.id,
        games[:10],
        f"Результати пошуку: {html.escape(query)}"
    )



@bot.message_handler(commands=["search"])
def on_search(message):
    parts = message.text.split(maxsplit=1)

    if len(parts) > 1:
        perform_search(message, parts[1])
    else:
        msg = bot.send_message(
            message.chat.id,
            "Введи назву гри:"
        )

        bot.register_next_step_handler(
            msg,
            search_step
        )



def search_step(message):
    if not message.text:
        bot.send_message(
            message.chat.id,
            "Введи назву гри текстом."
        )
        return

    if message.text.startswith("/"):
        bot.send_message(
            message.chat.id,
            "Пошук скасовано."
        )
        return

    perform_search(message, message.text)



@bot.message_handler(
    func=lambda message: (
        message.text is not None
        and not message.text.startswith("/")
    )
)
def on_text(message):
    text = message.text.strip()

    if text == "Усі знижки":
        on_deals(message)

    elif text == "Steam":
        on_steam(message)

    elif text == "Epic Games":
        on_epic(message)

    elif text == "Безкоштовні ігри":
        on_free(message)

    elif text == "Пошук гри":
        msg = bot.send_message(
            message.chat.id,
            "Введи назву гри:"
        )

        bot.register_next_step_handler(
            msg,
            search_step
        )

    elif text == "ТОП-10":
        on_top(message)

    elif text == "Випадкова гра":
        on_random(message)

    elif text == "Допомога":
        on_help(message)

    else:
        bot.send_message(
            message.chat.id,
            handlers.unknown_text(),
            reply_markup=main_keyboard()
        )



if __name__ == "__main__":
    print("Game Deal Radar запущено!")

    bot.infinity_polling(
        skip_pending=True,
        timeout=30,
        long_polling_timeout=30
    )
