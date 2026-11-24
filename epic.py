
"""Знижки та безкоштовні ігри Epic Games."""

import requests

BASE_URL = "https://api.egdata.app"
HEADERS = {"User-Agent": "GameDealRadar/1.0"}


def get_epic_free_games(include_upcoming=True):
    """Отримує безкоштовні та майбутні роздачі Epic."""

    try:
        response = requests.get(
            f"{BASE_URL}/free-games",
            params={"country": "UA", "locale": "uk-UA"},
            headers=HEADERS,
            timeout=20
        )
        response.raise_for_status()
        data = response.json()

        result = []

        if isinstance(data, dict):
            current = data.get("currentGames", [])
            upcoming = data.get("upcomingGames", [])
        elif isinstance(data, list):
            current = data
            upcoming = []
        else:
            raise RuntimeError("Невідомий формат відповіді Epic")

        for game in current:
            result.append({
                "title": game.get("title", "Невідома гра"),
                "old_price": None,
                "new_price": 0,
                "discount": 100,
                "currency": "UAH",
                "store": "Epic Games",
                "status": "free_now",
                "status_text": " Безкоштовно зараз!",
                "url": game.get("url") or (
                    "https://store.epicgames.com/uk/browse"
                )
            })

        if include_upcoming:
            for game in upcoming:
                result.append({
                    "title": game.get("title", "Невідома гра"),
                    "old_price": None,
                    "new_price": 0,
                    "discount": 100,
                    "currency": "UAH",
                    "store": "Epic Games",
                    "status": "upcoming",
                    "status_text": " Скоро безкоштовно",
                    "url": game.get("url") or (
                        "https://store.epicgames.com/uk/browse"
                    )
                })

        return result

    except requests.RequestException as error:
        raise RuntimeError(
            f"Помилка отримання безкоштовних ігор Epic: {error}"
        ) from error

    except (ValueError, TypeError, AttributeError) as error:
        raise RuntimeError(
            f"Помилка обробки Epic Games: {error}"
        ) from error


def get_epic_deals(limit=10):
    """Отримує платні ігри Epic зі знижками."""

    if not isinstance(limit, int) or not 1 <= limit <= 50:
        raise ValueError("Кількість ігор має бути від 1 до 50")

    try:
        response = requests.get(
            f"{BASE_URL}/offers",
            params={
                "country": "UA",
                "locale": "uk-UA",
                "page": 1,
                "limit": 50
            },
            headers=HEADERS,
            timeout=20
        )

        response.raise_for_status()
        data = response.json()

        games = data.get("elements", []) if isinstance(data, dict) else data

        result = []

        for game in games:
            price_data = (game.get("price") or {}).get("price") or {}

            old_price = price_data.get("originalPrice")
            new_price = price_data.get("discountPrice")
            currency = price_data.get("currencyCode", "USD")

            if old_price is None or new_price is None:
                continue

            old_price = float(old_price)
            new_price = float(new_price)

            if old_price <= 0 or new_price >= old_price:
                continue

            discount = round(
                (old_price - new_price) / old_price * 100
            )

            url = game.get("url")

            if not url:
                slug = game.get("productSlug") or game.get("urlSlug")
                url = (
                    f"https://store.epicgames.com/uk/p/{slug}"
                    if slug else "https://store.epicgames.com/uk/browse"
                )

            result.append({
                "title": game.get("title", "Невідома гра"),
                "old_price": old_price,
                "new_price": new_price,
                "discount": discount,
                "currency": currency,
                "store": "Epic Games",
                "status": "discount",
                "url": url
            })

        result.sort(
            key=lambda game: game["discount"],
            reverse=True
        )

        return result[:limit]

    except requests.RequestException as error:
        raise RuntimeError(
            f"Помилка отримання знижок Epic: {error}"
        ) from error

    except (ValueError, TypeError, AttributeError) as error:
        raise RuntimeError(
            f"Помилка обробки цін Epic: {error}"
        ) from error
