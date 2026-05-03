import requests
import time

BASE_URL = "https://steamcommunity.com/market/search/render/"
PRICE_OVERVIEW_URL = "https://steamcommunity.com/market/priceoverview/"

CACHE = {}
PRICE_CACHE = {}

CACHE_TTL = 60
PRICE_CACHE_TTL = 300

STEAM_SELLER_NET_RATE = 0.85
SACK_OF_GEMS_NAME = "753-Sack of Gems"


GEM_VALUE_BY_GAME = {
    "Wallpaper Engine": 20,
    "Warframe": 20,
    "WARMODE": 20,
    "UpGun": 20,
    "WAVESHAPER": 20,
}


BOOSTER_PACKS = [
    {
        "game": "Wallpaper Engine",
        "market_hash_name": "Wallpaper Engine Booster Pack",
        "booster_gem_cost": 1000,
    },
    {
        "game": "Warframe",
        "market_hash_name": "Warframe Booster Pack",
        "booster_gem_cost": 1000,
    },
    {
        "game": "WARMODE",
        "market_hash_name": "WARMODE Booster Pack",
        "booster_gem_cost": 1000,
    },
    {
        "game": "UpGun",
        "market_hash_name": "UpGun Booster Pack",
        "booster_gem_cost": 1000,
    },
    {
        "game": "WAVESHAPER",
        "market_hash_name": "WAVESHAPER Booster Pack",
        "booster_gem_cost": 1000,
    },
]


def clean_price(price_str):
    try:
        return float(
            str(price_str)
            .replace("$", "")
            .replace("USD", "")
            .replace(",", "")
            .strip()
        )
    except Exception:
        return 0.0


def fetch_price_overview(market_hash_name, force_refresh=False):
    now = time.time()
    cache_key = f"price:{market_hash_name}"

    if (
        not force_refresh
        and cache_key in PRICE_CACHE
        and now - PRICE_CACHE[cache_key]["timestamp"] < PRICE_CACHE_TTL
    ):
        return PRICE_CACHE[cache_key]["data"]

    params = {
        "appid": 753,
        "currency": 1,
        "market_hash_name": market_hash_name,
    }

    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(
            PRICE_OVERVIEW_URL,
            params=params,
            headers=headers,
            timeout=10,
        )

        if response.status_code != 200:
            print("Price overview error:", response.status_code, market_hash_name)
            return None

        data = response.json()

        lowest_price = clean_price(data.get("lowest_price", 0))
        median_price = clean_price(data.get("median_price", 0))
        volume = data.get("volume", "0")

        price = lowest_price or median_price

        result = {
            "market_hash_name": market_hash_name,
            "lowest_price": lowest_price,
            "median_price": median_price,
            "price": price,
            "volume": volume,
            "success": data.get("success", False),
        }

        PRICE_CACHE[cache_key] = {
            "data": result,
            "timestamp": now,
        }

        return result

    except Exception as e:
        print("Price overview request failed:", e)
        return None


def fetch_gem_sack_price(force_refresh=False):
    data = fetch_price_overview(SACK_OF_GEMS_NAME, force_refresh=force_refresh)

    if not data:
        return None

    price = data.get("price", 0)

    if price <= 0:
        return None

    return price


def get_gem_value_per_gem():
    sack_price = fetch_gem_sack_price()

    if not sack_price:
        return 0.0003

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
        "norender": 1,
    }

    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(
            BASE_URL,
            params=params,
            headers=headers,
            timeout=10,
        )

        if response.status_code != 200:
            print("Market search error:", response.status_code)
            return []

        data = response.json()
        return data.get("results", [])

    except Exception as e:
        print("Market search failed:", e)
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
                "gem_value_per_gem": round(gem_value_per_gem, 6),
            })

        except Exception:
            continue

    return parsed


def get_market_items(query="trading card", force_refresh=False):
    now = time.time()
    cache_key = f"market:{query}"

    if (
        not force_refresh
        and cache_key in CACHE
        and now - CACHE[cache_key]["timestamp"] < CACHE_TTL
    ):
        return CACHE[cache_key]["data"]

    raw = fetch_market_data(query=query)
    parsed = parse_items(raw)

    CACHE[cache_key] = {
        "data": parsed,
        "timestamp": now,
    }

    return parsed


def get_booster_opportunities(force_refresh=False):
    gem_value_per_gem = get_gem_value_per_gem()
    gem_sack_price = fetch_gem_sack_price()
    results = []

    for booster in BOOSTER_PACKS:
        game = booster["game"]
        market_hash_name = booster["market_hash_name"]
        booster_gem_cost = booster["booster_gem_cost"]

        price_data = fetch_price_overview(
            market_hash_name,
            force_refresh=force_refresh,
        )

        if not price_data:
            continue

        booster_market_price = price_data.get("price", 0)

        if booster_market_price <= 0:
            continue

        craft_cost = booster_gem_cost * gem_value_per_gem
        estimated_net_sale = booster_market_price * STEAM_SELLER_NET_RATE
        profit = estimated_net_sale - craft_cost
        roi_percent = (profit / craft_cost) * 100 if craft_cost > 0 else 0

        results.append({
            "game": game,
            "market_hash_name": market_hash_name,
            "booster_gem_cost": booster_gem_cost,
            "gem_sack_price": gem_sack_price,
            "gem_value_per_gem": round(gem_value_per_gem, 6),
            "craft_cost": round(craft_cost, 4),
            "booster_market_price": round(booster_market_price, 4),
            "estimated_net_sale": round(estimated_net_sale, 4),
            "estimated_steam_fee_percent": round((1 - STEAM_SELLER_NET_RATE) * 100, 2),
            "profit": round(profit, 4),
            "roi_percent": round(roi_percent, 2),
            "volume": price_data.get("volume", "0"),
        })

    results.sort(key=lambda x: x["roi_percent"], reverse=True)
    return results
