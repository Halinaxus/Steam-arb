import requests
import time

BASE_URL = "https://steamcommunity.com/market/search/render/"

# simple in-memory cache
CACHE = {
    "data": None,
    "timestamp": 0
}

CACHE_TTL = 60  # seconds


def fetch_market_data(query="trading card", count=30):
    params = {
        "query": query,
        "start": 0,
        "count": count,
        "search_descriptions": 0,
        "sort_column": "price",
        "sort_dir": "asc",
        "appid": 753,  # Steam community items
        "norender": 1
    }

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(BASE_URL, params=params, headers=headers, timeout=10)

        if response.status_code != 200:
            print("Error fetching data:", response.status_code)
            return []

        data = response.json()
        return data.get("results", [])

    except Exception as e:
        print("Request failed:", e)
        return []


def clean_price(price_str):
    """
    Converts '$0.10' → 0.10
    Handles commas and empty values safely
    """
    try:
        return float(
            price_str.replace("$", "")
                     .replace(",", "")
                     .strip()
        )
    except:
        return 0.0


def estimate_gems(name):
    """
    Placeholder logic.

    Most trading cards give between 10–40 gems.
    We’ll improve this later with real mappings.
    """

    name_lower = name.lower()

    # crude heuristics (better than flat 20)
    if "foil" in name_lower:
        return 40
    elif "rare" in name_lower:
        return 30
    else:
        return 20


def parse_items(raw_items):
    parsed = []

    for item in raw_items:
        try:
            name = item.get("name", "Unknown")

            price_str = item.get("sell_price_text", "$0.00")
            price = clean_price(price_str)

            if price <= 0:
                continue

            parsed.append({
                "name": name,
                "price": price,
                "gems": estimate_gems(name)
            })

        except Exception:
            continue

    return parsed


def get_market_items(force_refresh=False):
    """
    Main function used by your API.
    Includes caching to avoid hitting Steam too often.
    """

    current_time = time.time()

    # return cached data if still valid
    if (
        not force_refresh and
        CACHE["data"] is not None and
        current_time - CACHE["timestamp"] < CACHE_TTL
    ):
        return CACHE["data"]

    raw = fetch_market_data()
    parsed = parse_items(raw)

    # update cache
    CACHE["data"] = parsed
    CACHE["timestamp"] = current_time

    return parsed
