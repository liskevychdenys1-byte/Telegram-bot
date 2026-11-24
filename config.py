from pathlib import Path
import os

from dotenv import load_dotenv

# Шукаємо .env у тій самій папці, де лежить config.py.
load_dotenv(dotenv_path=Path(__file__).parent / ".env")


def require_token():
    """Повертає токен або пояснює, як виправити налаштування."""
    token = os.getenv("BOT_TOKEN", "").strip()
    if not token or token == "REPLACE_WITH_TOKEN":
        raise RuntimeError(
            "Немає BOT_TOKEN. Створи .env поруч із config.py "
            "і встав власний токен від BotFather."
        )
    return token
