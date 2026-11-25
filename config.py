
import os
from pathlib import Path
from dotenv import load_dotenv


ENV_PATH = Path(__file__).resolve().parent / ".env"

load_dotenv(dotenv_path=ENV_PATH, override=True)


TOKEN = os.getenv("TOKEN", "").strip()
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
EGDATA_API_KEY = os.getenv("EGDATA_API_KEY", "").strip()


if not TOKEN:
    TOKEN = BOT_TOKEN

if not BOT_TOKEN:
    BOT_TOKEN = TOKEN


def require_token():
    """Повертає Telegram-токен."""
    if not TOKEN or TOKEN == "REPLACE_WITH_TOKEN":
        raise RuntimeError(
            "Не знайдено TOKEN. Перевір файл .env."
        )

    return TOKEN


def require_egdata_key():
    """Повертає EGDATA API-ключ."""
    if not EGDATA_API_KEY:
        raise RuntimeError(
            "Не знайдено EGDATA_API_KEY у файлі .env."
        )

    return EGDATA_API_KEY
