
"""Отримання актуальних цін Steam для України."""

import requests

BASE_URL = "https://store.steampowered.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 GameDealRadar/1.0"
}


def get_steam_deals(min_discount=0, limit=10):
    """Отримує акційні ігри з українського Steam."""

    if not 0 <= min_discount <= 100:
        raise ValueError("Знижка повинна бути від 0 до 100")

    if not 1 <= limit <= 60:
        raise ValueError("Кількість ігор повинна бути від 1 до 60")

    url = f"{BASE_URL}/api/featuredcategories/"

    params = {
        "cc": "ua",
        "l": "ukrainian"
    }

    try:
        response = requests.get(
            url,
            params=params,
            headers=HEADERS,
            timeout=20
        )
        response.raise_for_status()

        data = response.json()
        specials = data.get("specials", {})
        items = specials.get("items", [])

        games = []

        for game in items:
            discount = int(game.get("discount_percent", 0))

            if discount < min_discount:
                continue

            old_price = game.get("original_price")
            new_price = game.get("final_price")

            if old_price is None or new_price is None:
                continue

            games.append({
                "title": game.get("name", "Невідома гра"),
                "old_price": round(old_price / 100, 2),
                "new_price": round(new_price / 100, 2),
                "discount": discount,
                "currency": "UAH",
                "url": (
                    f"https://store.steampowered.com/app/"
                    f"{game.get('id')}/"
                )
            })

        return games[:limit]

    except requests.RequestException as error:
        print(f"Помилка Steam API: {error}")
        return []

    except (ValueError, TypeError, KeyError) as error:
        print(f"Помилка обробки цін Steam: {error}")
        return []


def search_steam_game(query):
    """Шукає гру та отримує її українську ціну."""

    if not query or not query.strip():
        return []

    try:
        response = requests.get(
            f"{BASE_URL}/api/storesearch/",
            params={
                "term": query.strip(),
                "cc": "ua",
                "l": "ukrainian"
            },
            headers=HEADERS,
            timeout=20
        )
        response.raise_for_status()

        items = response.json().get("items", [])
        results = []

        for item in items[:10]:
            app_id = item.get("id")

            if not app_id:
                continue

            details_response = requests.get(
                f"{BASE_URL}/api/appdetails",
                params={
                    "appids": app_id,
                    "cc": "ua",
                    "l": "ukrainian"
                },
                headers=HEADERS,
                timeout=20
            )
            details_response.raise_for_status()

            details = details_response.json()
            app_data = details.get(str(app_id), {})

            if not app_data.get("success"):
                continue

            game = app_data.get("data", {})
            price = game.get("price_overview")

            if price:
                old_price = price["initial"] / 100
                new_price = price["final"] / 100
                discount = price["discount_percent"]
            else:
                old_price = 0
                new_price = 0
                discount = 0

            results.append({
                "title": game.get("name", item.get("name")),
                "old_price": round(old_price, 2),
                "new_price": round(new_price, 2),
                "discount": discount,
                "currency": "UAH",
                "url": f"https://store.steampowered.com/app/{app_id}/"
            })

        return results

    except (requests.RequestException, ValueError, KeyError) as error:
        print(f"Помилка пошуку Steam: {error}")
        return []
