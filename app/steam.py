import requests
import time

BASE_URL = "https://steamcommunity.com/market/search/render/"

CACHE = {
    "data": None,
    "timestamp": 0
}

CACHE_TTL = 60  # seconds


# Add/update these as you verify real gem values by game
GEM_VALUE_BY_GAME = {
    "Wallpaper Engine": 20,
    "Warframe": 20,
    "WARMODE": 20,
    "UpGun": 20,
    "WAVESHAPER": 20,
}


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


def clean_price(price_str):
    try:
        return float(
            price_str.replace("$", "")
            .replace(",", "")
            .strip()
        )
    except Exception:
        return 0.0


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

            parsed.append({
                "name": name,
                "game": app_name,
                "price": price,
                "gems": gems
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
