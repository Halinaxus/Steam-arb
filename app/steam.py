import requests

BASE_URL = "https://steamcommunity.com/market/search/render/"

def fetch_market_data(query="trading card", count=20):
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

    response = requests.get(BASE_URL, params=params, headers=headers)

    if response.status_code != 200:
        print("Error fetching data:", response.status_code)
        return []

    data = response.json()
    return data.get("results", [])

def parse_items(raw_items):
    parsed = []

    for item in raw_items:
        try:
            name = item["name"]

            # price is in cents string like "$0.10"
            price_str = item.get("sell_price_text", "$0.00")
            price = float(price_str.replace("$", "").replace(",", ""))

            parsed.append({
                "name": name,
                "price": price,
                "gems": estimate_gems(name)
            })

        except Exception as e:
            continue

    return parsed

def estimate_gems(name):
    # VERY rough placeholder logic
    # Most cards give ~10–40 gems
    return 20

def get_market_items():
    raw = fetch_market_data()
    return parse_items(raw)
