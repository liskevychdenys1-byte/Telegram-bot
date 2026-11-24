
"""Epic Games — роздачі та акційні ігри."""

import requests

BASE_URL = "https://api.egdata.app"

HEADERS = {
    "User-Agent": "GameDealRadar/1.0"
}


def get_epic_free_games():
    """Отримує безкоштовні та майбутні роздачі."""

    try:
        response = requests.get(
            f"{BASE_URL}/free-games",
            params={
                "country": "UA",
                "locale": "uk-UA"
            },
            headers=HEADERS,
            timeout=20
        )

        response.raise_for_status()
        data = response.json()

        if not isinstance(data, list):
            return []

        games = []

        for item in data:
            giveaway = item.get("giveaway") or {}

            games.append({
                "title": item.get("title", "Невідома гра"),
                "start": giveaway.get("startDate", ""),
                "end": giveaway.get("endDate", ""),
                "url": (
                    "https://store.epicgames.com/p/"
                    + str(item.get("productSlug", ""))
                    if item.get("productSlug")
                    else "https://store.epicgames.com/"
                )
            })

        return games

    except (requests.RequestException, ValueError, TypeError) as error:
        print(f"Epic API error: {error}")
        return []


def get_epic_deals(limit=10):
    """Отримує акційні ігри Epic Games."""

    try:
        response = requests.get(
            f"{BASE_URL}/v1/search",
            params={
                "country": "UA",
                "locale": "uk-UA",
                "offerType": "BASE_GAME",
                "onSale": "true",
                "sortBy": "discountPercent",
                "sortDir": "desc",
                "limit": limit,
                "fields": "full"
            },
            headers=HEADERS,
            timeout=20
        )

        response.raise_for_status()
        data = response.json()

        offers = data.get("data", [])
        games = []

        for item in offers:
            price = item.get("price") or {}

            if not isinstance(price, dict):
                continue

            # Пропускаємо пропозиції без підтвердженої ціни.
            old_price = price.get("originalPrice")
            new_price = price.get("discountPrice")

            if old_price is None or new_price is None:
                continue

            old_price = float(old_price)
            new_price = float(new_price)

            if old_price <= 0 or new_price >= old_price:
                continue

            discount = round(
                (1 - new_price / old_price) * 100
            )

            games.append({
                "title": item.get("title", "Невідома гра"),
                "old_price": old_price,
                "new_price": new_price,
                "discount": discount,
                "currency": price.get("currencyCode", "UAH"),
                "url": "https://store.epicgames.com/"
            })

        return games[:limit]

    except (requests.RequestException, ValueError, TypeError) as error:
        print(f"Epic deals error: {error}")
        return []
