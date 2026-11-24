import telebot

from config import require_token

bot = telebot.TeleBot(require_token())


@bot.message_handler(content_types=["text"])
def echo(message):
    bot.reply_to(message, f"Ти написав: {message.text}")


if __name__ == "__main__":
    print("Echo-бот запущений. Зупинити: Ctrl+C")
    bot.infinity_polling(skip_pending=True)
