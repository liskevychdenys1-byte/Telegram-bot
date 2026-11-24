
"""Головний файл Game Deal Radar."""

import random
import telebot
from telebot import types

from config import require_token
from steam import get_steam_deals, search_steam_game
from epic import get_epic_deals, get_epic_free_games
import handlers


bot = telebot.TeleBot(require_token())


# Головне меню
def main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        row_width=2
    )

    keyboard.add(
        "🔥 Усі знижки",
        "🎮 Steam"
    )

    keyboard.add(
        "🕹 Epic Games",
        "🎁 Безкоштовні ігри"
    )

    keyboard.add(
        "🔎 Пошук гри",
        "🏆 ТОП-10"
    )

    keyboard.add(
        "🎲 Випадкова гра",
        "❓ Допомога"
    )

    return keyboard


# Надсилання ігор
def send_games(chat_id, games, title):
    if not games:
        bot.send_message(
            chat_id,
            "😔 Ігор не знайдено або сервіс тимчасово недоступний."
        )
        return

    bot.send_message(chat_id, title)

    for game in games:
        bot.send_message(
            chat_id,
            handlers.format_game(game),
            disable_web_page_preview=True
        )


# Безкоштовні ігри Epic
def send_free_games(chat_id):
    games = get_epic_free_games()

    if not games:
        bot.send_message(
            chat_id,
            "😔 Не вдалося отримати безкоштовні ігри Epic."
        )
        return

    for game in games:
        text = (
            f"🎁 {game['title']}\n\n"
            f"📅 Початок: {game.get('start') or 'Не вказано'}\n"
            f"⏰ Завершення: {game.get('end') or 'Не вказано'}\n"
            f"🔗 {game['url']}"
        )

        bot.send_message(
            chat_id,
            text,
            disable_web_page_preview=True
        )


# /start
@bot.message_handler(commands=["start"])
def start(message):
    name = message.from_user.first_name or "друже"

    bot.send_message(
        message.chat.id,
        handlers.start_text(name),
        reply_markup=main_keyboard()
    )


# /help
@bot.message_handler(commands=["help"])
def help_command(message):
    bot.send_message(
        message.chat.id,
        handlers.help_text(),
        reply_markup=main_keyboard()
    )


# /steam
@bot.message_handler(commands=["steam"])
def steam_command(message):
    games = get_steam_deals(limit=20)

    send_games(
        message.chat.id,
        games,
        "🎮 ЗНИЖКИ STEAM"
    )


# /epic
@bot.message_handler(commands=["epic"])
def epic_command(message):
    games = get_epic_deals(limit=20)

    send_games(
        message.chat.id,
        games,
        "🕹 ЗНИЖКИ EPIC GAMES"
    )


# /free
@bot.message_handler(commands=["free"])
def free_command(message):
    send_free_games(message.chat.id)


# /deals
@bot.message_handler(commands=["deals"])
def deals_command(message):
    steam_games = get_steam_deals(limit=20)
    epic_games = get_epic_deals(limit=20)

    games = steam_games + epic_games

    games = handlers.top_games(games, 20)

    send_games(
        message.chat.id,
        games,
        "🔥 УСІ АКТУАЛЬНІ ЗНИЖКИ"
    )


# /top
@bot.message_handler(commands=["top"])
def top_command(message):
    steam_games = get_steam_deals(limit=60)
    epic_games = get_epic_deals(limit=60)

    games = handlers.top_games(
        steam_games + epic_games,
        10
    )

    send_games(
        message.chat.id,
        games,
        "🏆 ТОП-10 НАЙБІЛЬШИХ ЗНИЖОК"
    )


# /random
@bot.message_handler(commands=["random"])
def random_command(message):
    games = (
        get_steam_deals(limit=60)
        + get_epic_deals(limit=60)
    )

    if not games:
        bot.send_message(
            message.chat.id,
            "😔 Наразі немає доступних ігор."
        )
        return

    game = random.choice(games)

    send_games(
        message.chat.id,
        [game],
        "🎲 ВИПАДКОВА ГРА"
    )


# /search
@bot.message_handler(commands=["search"])
def search_command(message):
    bot.send_message(
        message.chat.id,
        "🔎 Напиши назву гри, яку потрібно знайти:"
    )

    bot.register_next_step_handler(
        message,
        process_search
    )


def process_search(message):
    query = message.text.strip() if message.text else ""

    if not query:
        bot.send_message(
            message.chat.id,
            "❌ Введи текстову назву гри."
        )
        return

    bot.send_message(
        message.chat.id,
        "🔍 Шукаю гру, зачекай..."
    )

    games = search_steam_game(query)

    if not games:
        bot.send_message(
            message.chat.id,
            f"😔 Гру «{query}» не знайдено."
        )
        return

    send_games(
        message.chat.id,
        games,
        f"🔎 РЕЗУЛЬТАТИ ПОШУКУ: {query}"
    )


# Обробка кнопок меню
@bot.message_handler(func=lambda message: True)
def menu_handler(message):
    text = message.text

    if text == "🎮 Steam":
        steam_command(message)

    elif text == "🕹 Epic Games":
        epic_command(message)

    elif text == "🎁 Безкоштовні ігри":
        free_command(message)

    elif text == "🔥 Усі знижки":
        deals_command(message)

    elif text == "🏆 ТОП-10":
        top_command(message)

    elif text == "🎲 Випадкова гра":
        random_command(message)

    elif text == "🔎 Пошук гри":
        search_command(message)

    elif text == "❓ Допомога":
        help_command(message)

    else:
        bot.send_message(
            message.chat.id,
            "Не розумію команду. Скористайся меню або /help."
        )


# Запуск бота
if __name__ == "__main__":
    print("🎮 Game Deal Radar запущено!")

    bot.infinity_polling(
        skip_pending=True,
        timeout=30,
        long_polling_timeout=30
    )
