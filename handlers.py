
"""Допоміжні функції Game Deal Radar."""


def start_text(name):
    name = (name or "друже").strip()

    return (
        f"Привіт, {name}! 🎮\n\n"
        "Я Game Deal Radar!\n"
        "Допоможу знаходити найкращі знижки "
        "на ігри Steam та Epic Games.\n\n"
        "Обирай потрібний розділ у меню!"
    )


def help_text():
    return (
        "🎮 GAME DEAL RADAR — допомога\n\n"
        "/start — головне меню\n"
        "/help — допомога\n"
        "/deals — усі знижки\n"
        "/steam — знижки Steam\n"
        "/epic — знижки Epic Games\n"
        "/free — безкоштовні ігри Epic\n"
        "/search — пошук гри\n"
        "/top — ТОП-10 знижок\n"
        "/random — випадкова гра"
    )


def format_price(price, currency="UAH"):
    """Форматує ціну."""

    symbols = {
        "UAH": "₴",
        "USD": "$",
        "EUR": "€",
        "PLN": "zł"
    }

    symbol = symbols.get(currency, currency)

    return f"{float(price):.2f} {symbol}"


def search_games(games, query):
    """Шукає ігри за назвою."""

    query = query.strip().lower()

    if not query:
        return []

    return [
        game for game in games
        if query in game["title"].lower()
    ]


def top_games(games, limit=10):
    """Сортує ігри за розміром знижки."""

    return sorted(
        games,
        key=lambda game: game.get("discount", 0),
        reverse=True
    )[:limit]


def format_game(game):
    """Формує повідомлення про одну гру."""

    old_price = game.get("old_price", 0)
    new_price = game.get("new_price", 0)
    currency = game.get("currency", "UAH")

    return (
        f"🎮 {game['title']}\n"
        f"━━━━━━━━━━━━━━\n"
        f"💰 Було: {format_price(old_price, currency)}\n"
        f"🔥 Стало: {format_price(new_price, currency)}\n"
        f"📉 Знижка: -{game.get('discount', 0)}%\n"
        f"🔗 {game.get('url', '')}\n"
    )
