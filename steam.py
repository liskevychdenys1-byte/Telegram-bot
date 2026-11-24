
"""Модуль для отримання знижок на ігри Steam."""

import requests


API_URL = "https://www.cheapshark.com/api/1.0/deals"

HEADERS = {
    "User-Agent": "GameDealRadar/1.0"
}


def get_steam_deals(min_discount=0, limit=10):
    """Отримує список актуальних знижок Steam."""

    if not isinstance(min_discount, (int, float)) or not 0 <= min_discount <= 100:
        raise ValueError("Знижка повинна бути від 0 до 100%")

    if not isinstance(limit, int) or not 1 <= limit <= 60:
        raise ValueError("Кількість ігор повинна бути від 1 до 60")

    params = {
        "storeID": 1,
        "onSale": 1,
        "pageSize": 60,
        "sortBy": "Savings",
        "desc": 1
    }

    try:
        response = requests.get(
            API_URL,
            params=params,
            headers=HEADERS,
            timeout=15
        )

        response.raise_for_status()
        games = response.json()

        result = []

        for game in games:
            discount = float(game.get("savings", 0))
            old_price = float(game.get("normalPrice", 0))
            new_price = float(game.get("salePrice", 0))

            if discount < min_discount:
                continue

            if old_price <= 0 or new_price < 0:
                continue

            result.append({
                "title": game.get("title", "Невідома гра"),
                "old_price": old_price,
                "new_price": new_price,
                "discount": round(discount),
                "currency": "UAH",
                "store": "Steam",
                "url": (
                    "https://www.cheapshark.com/redirect?dealID="
                    + game.get("dealID", "")
                )
            })

            if len(result) >= limit:
                break

        return result

    except requests.RequestException as error:
        raise RuntimeError(
            f"Не вдалося отримати знижки Steam: {error}"
        ) from error

    except (ValueError, TypeError, AttributeError) as error:
        raise RuntimeError(
            f"Помилка обробки даних Steam: {error}"
        ) from error


def search_steam_game(title):
    """Шукає гру Steam за назвою."""

    if not isinstance(title, str) or not title.strip():
        raise ValueError("Введи назву гри для пошуку")

    params = {
        "storeID": 1,
        "onSale": 1,
        "title": title.strip(),
        "pageSize": 20
    }

    try:
        response = requests.get(
            API_URL,
            params=params,
            headers=HEADERS,
            timeout=15
        )

        response.raise_for_status()
        games = response.json()

        result = []

        for game in games:
            old_price = float(game.get("normalPrice", 0))
            new_price = float(game.get("salePrice", 0))
            discount = float(game.get("savings", 0))

            if old_price <= 0:
                continue

            result.append({
                "title": game.get("title", "Невідома гра"),
                "old_price": old_price,
                "new_price": new_price,
                "discount": round(discount),
                "currency": "UAH",
                "store": "Steam",
                "url": (
                    "https://www.cheapshark.com/redirect?dealID="
                    + game.get("dealID", "")
                )
            })

        return result

    except requests.RequestException as error:
        raise RuntimeError(
            f"Помилка пошуку гри: {error}"
        ) from error

    except (ValueError, TypeError, AttributeError) as error:
        raise RuntimeError(
            f"Не вдалося обробити результати пошуку: {error}"
        ) from error
