
"""Epic Games — Game Deal Radar."""

import requests

from config import require_egdata_key

BASE_URL = "https://devs.egdata.app/proxy"

HEADERS = {
    "User-Agent": "GameDealRadar/2.1",
    "Accept": "application/json"
}


def api_request(endpoint, params=None):
    """Виконує запит до EGDATA API."""

    headers = HEADERS.copy()
    headers["X-API-Key"] = require_egdata_key()

    response = requests.get(
        BASE_URL + endpoint,
        params=params,
        headers=headers,
        timeout=25
    )

    response.raise_for_status()
    return response.json()


def get_epic_free_games():
    """Отримує безкоштовні ігри Epic Games."""

    try:
        data = api_request(
            "/free-games",
            {
                "country": "UA",
                "locale": "uk-UA"
            }
        )

        if not isinstance(data, list):
            print("Epic: неправильний формат роздач.")
            return []

        games = []

        for item in data:
            giveaway = item.get("giveaway") or {}

            if not giveaway:
                continue

            whitelist = item.get("countriesWhitelist") or []
            blacklist = item.get("countriesBlacklist") or []

            if whitelist and "UA" not in whitelist:
                continue

            if "UA" in blacklist:
                continue

            slug = item.get("productSlug")

            games.append({
                "title": item.get("title", "Невідома гра"),
                "start": giveaway.get("startDate", ""),
                "end": giveaway.get("endDate", ""),
                "url": (
                    f"https://store.epicgames.com/p/{slug}"
                    if slug
                    else "https://store.epicgames.com/"
                )
            })

        print(f"Game: знайдено роздач: {len(games)}")
        return games

    except requests.RequestException as error:
        print(f"Epic Free Games HTTP error: {error}")
        return []

    except (ValueError, TypeError, KeyError) as error:
        print(f"Epic Free Games parsing error: {error}")
        return []


def extract_price(item):
    """Отримує цінові дані гри."""

    price = item.get("price")

    if not isinstance(price, dict):
        return None

    current = price.get("currentPrice")

    if isinstance(current, dict):
        price = current.get("price") or price

    if not isinstance(price, dict):
        return None

    currency = price.get("currencyCode")

    old_price = (
        price.get("originalPrice")
        or price.get("basePrice")
        or price.get("original")
    )

    new_price = (
        price.get("discountPrice")
        if price.get("discountPrice") is not None
        else price.get("finalPrice")
    )

    discount = price.get("discount")

    if old_price is None or new_price is None:
        return None

    try:
        old_price = float(old_price)
        new_price = float(new_price)
    except (ValueError, TypeError):
        return None

    if old_price <= 0 or new_price >= old_price:
        return None

    if not currency:
        return None


    old_price /= 100
    new_price /= 100

    if discount is None:
        discount = round(
            (1 - new_price / old_price) * 100
        )

    return {
        "old_price": round(old_price, 2),
        "new_price": round(new_price, 2),
        "discount": int(discount),
        "currency": currency
    }


def get_epic_deals(limit=20):
    """Отримує ігри Epic Games зі знижками."""

    try:
        data = api_request(
            "/v1/search",
            {
                "country": "UA",
                "locale": "uk-UA",
                "offerType": "BASE_GAME",
                "onSale": "true",
                "sortBy": "discountPercent",
                "sortDir": "desc",
                "limit": limit,
                "fields": "full"
            }
        )

        if not isinstance(data, dict):
            print("Epic: неправильний формат каталогу.")
            return []

        items = data.get("data", [])

        if not isinstance(items, list):
            print("Epic: поле data не є списком.")
            return []

        games = []

        for item in items:
            prices = extract_price(item)

            if not prices:
                continue

            slug = item.get("productSlug")

            games.append({
                "title": item.get("title", "Невідома гра"),
                **prices,
                "url": (
                    f"https://store.epicgames.com/p/{slug}"
                    if slug
                    else "https://store.epicgames.com/"
                )
            })

        print(
            f"Game: отримано {len(items)} пропозицій, "
            f"знайдено {len(games)} ігор зі знижками."
        )

        return games

    except requests.RequestException as error:
        print(f"Epic Deals HTTP error: {error}")
        return []

    except (ValueError, TypeError, KeyError) as error:
        print(f"Epic Deals parsing error: {error}")
        return []
