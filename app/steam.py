import requests
import time
from urllib.parse import quote

BASE_URL = "https://steamcommunity.com/market/search/render/"
PRICE_OVERVIEW_URL = "https://steamcommunity.com/market/priceoverview/"

CACHE = {
    "data": None,
    "timestamp": 0
}

GEM_PRICE_CACHE = {
    "price": None,
    "timestamp": 0
}

CACHE_TTL = 60
GEM_CACHE_TTL = 300  # 5 minutes

SACK_OF_GEMS_NAME = "753-Sack of Gems"


GEM_VALUE_BY_GAME = {
    "Wallpaper Engine": 20,
    "Warframe": 20,
    "WARMODE": 20,
    "UpGun": 20,
    "WAVESHAPER": 20,
}


def clean_price(price_str):
    try:
        return float(
            price_str.replace("$", "")
            .replace("USD", "")
            .replace(",", "")
            .strip()
        )
    except Exception:
        return 0.0


def fetch_gem_sack_price(force_refresh=False):
    """
    Fetches live Steam Market price for Sack of Gems.
    A Sack of Gems = 1000 gems.
    """

    current_time = time.time()

    if (
        not force_refresh
        and GEM_PRICE_CACHE["price"] is not None
        and current_time - GEM_PRICE_CACHE["timestamp"] < GEM_CACHE_TTL
    ):
        return GEM_PRICE_CACHE["price"]

    params = {
        "appid": 753,
        "currency": 1,
        "market_hash_name": SACK_OF_GEMS_NAME
    }

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(
            PRICE_OVERVIEW_URL,
            params=params,
            headers=headers,
            timeout=10
        )

        if response.status_code != 200:
            print("Gem price error:", response.status_code)
            return None

        data = response.json()

        price_text = (
            data.get("lowest_price")
            or data.get("median_price")
            or "$0.00"
        )

        price = clean_price(price_text)

        if price <= 0:
            return None

        GEM_PRICE_CACHE["price"] = price
        GEM_PRICE_CACHE["timestamp"] = current_time

        return price

    except Exception as e:
        print("Gem price request failed:", e)
        return None


def get_gem_value_per_gem():
    sack_price = fetch_gem_sack_price()

    if not sack_price:
        return 0.0003  # fallback: $0.30 / 1000 gems

    return sack_price / 1000


def fetch_market_data(query="trading card", count=30):
    params = {
        "query": query,
        "start": 0,
        "count": count,
        "search_descriptions": 0,
        "sort_column": "price",
        "sort_dir": "asc",
        "appid": 753,
        "norender": 1
    }

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(
            BASE_URL,
            params=params,
            headers=headers,
            timeout=10
        )

        if response.status_code != 200:
            print("Error fetching data:", response.status_code)
            return []

        data = response.json()
        return data.get("results", [])

    except Exception as e:
        print("Request failed:", e)
        return []


def extract_game_name(name):
    for game in GEM_VALUE_BY_GAME:
        if game.lower() in name.lower():
            return game

    return None


def estimate_gems(name, game_name=None):
    name_lower = name.lower()

    game_key = game_name or extract_game_name(name)
    base_gems = GEM_VALUE_BY_GAME.get(game_key, 20)

    if "foil" in name_lower:
        return base_gems * 10

    return base_gems


def parse_items(raw_items):
    parsed = []
    gem_value_per_gem = get_gem_value_per_gem()
    sack_price = fetch_gem_sack_price()

    for item in raw_items:
        try:
            name = item.get("name", "Unknown")

            app_name = (
                item.get("app_name")
                or item.get("asset_description", {}).get("app_name")
                or extract_game_name(name)
                or "Unknown"
            )

            price_str = item.get("sell_price_text", "$0.00")
            price = clean_price(price_str)

            if price <= 0:
                continue

            gems = estimate_gems(name, app_name)
            gem_value = gems * gem_value_per_gem

            parsed.append({
                "name": name,
                "game": app_name,
                "price": round(price, 4),
                "gems": gems,
                "gem_value": round(gem_value, 4),
                "gem_sack_price": sack_price,
                "gem_value_per_gem": round(gem_value_per_gem, 6)
            })

        except Exception:
            continue

    return parsed


def get_market_items(force_refresh=False):
    current_time = time.time()

    if (
        not force_refresh
        and CACHE["data"] is not None
        and current_time - CACHE["timestamp"] < CACHE_TTL
    ):
        return CACHE["data"]

    raw = fetch_market_data()
    parsed = parse_items(raw)

    CACHE["data"] = parsed
    CACHE["timestamp"] = current_time

    return parsed
