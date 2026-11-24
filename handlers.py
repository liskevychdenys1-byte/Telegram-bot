
"""Логіка повідомлень Game Deal Radar."""


def start_text(name):
    name = (name or "друже").strip() or "друже"

    return (
        f"Привіт, {name}! \n\n"
        f"Я Game Deal Radar!\n"
        f"Допоможу знаходити найкращі знижки "
        f"на ігри Steam та Epic Games.\n\n"
        f"Обирай потрібний розділ у меню нижче!"
    )


def help_text():
    return (
        " GAME DEAL RADAR — команди:\n\n"
        "/start — головне меню\n"
        "/help — допомога\n"
        "/deals — усі знижки\n"
        "/steam — знижки Steam\n"
        "/epic — знижки Epic Games\n"
        "/free — безкоштовні ігри Epic\n"
        "/search — пошук гри\n"
        "/top — ТОП-10 знижок\n"
        "/random — випадкова гра зі знижкою"
    )


def format_price(price, currency="UAH"):
    """Форматує ціну."""

    if price is None:
        return "Невідома"




    symbols = {
        "USD": "$",
        "EUR": "€",
        "UAH": "₴",
        "GBP": "£"
    }

    symbol = symbols.get(currency, currency)

    return f"{price:.2f} {symbol}"


def format_game(game):
    """Формує повідомлення про гру."""

    title = game.get("title", "Невідома гра")
    store = game.get("store", "Невідомий магазин")
    discount = game.get("discount", 0)
    currency = game.get("currency", "UAH")

    if game.get("status") == "free_now":
        return (
            f" <b>{title}</b>\n\n"
            f"Безкоштовно зараз!\n"
            f" Ціна: 0 ₴\n"
            f" Знижка: 100%\n"
            f" Магазин: {store}\n\n"

        )

    if game.get("status") == "upcoming":
        return (
            f" <b>{title}</b>\n\n"
            "Скоро буде безкоштовно!\n"
            f" Магазин: {store}\n\n"
            f'<a href="{game["url"]}">Відкрити магазин</a>'
        )

    old_price = format_price(game.get("old_price"), currency )
    new_price = format_price(game.get("new_price"), currency )

    saving = game.get("old_price", 0) - game.get("new_price", 0)

    return (
        f" <b>{title}</b>\n\n"
        f" Знижка: -{discount}%\n"
        f" Стара ціна: {old_price}\n"
        f" Нова ціна: {new_price}\n"
        f" Економія: {format_price(saving, currency)}\n"
        f" Магазин: {store}\n\n"

    )


def top_games(games, limit=10):
    """Повертає ігри з найбільшими знижками."""

    return sorted(
        games,
        key=lambda game: game.get("discount", 0),
        reverse=True
    )[:limit]


def search_games(games, query):
    """Шукає гру за частиною назви."""

    if not isinstance(query, str) or not query.strip():
        raise ValueError("Введи назву гри")

    query = query.casefold().strip()

    return [
        game for game in games
        if query in game.get("title", "").casefold()
    ]


def unknown_text():
    return (
        "Не зрозумів команду \n"
        "Скористайся кнопками меню або введи /help."
    )
