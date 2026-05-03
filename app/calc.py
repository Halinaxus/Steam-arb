def analyze_items(items):
    results = []

    for item in items:
        price = item.get("price", 0)
        gem_value = item.get("gem_value", 0)

        if price <= 0:
            continue

        profit = gem_value - price
        roi_percent = (profit / price) * 100

        results.append({
            "name": item.get("name", "Unknown"),
            "game": item.get("game", "Unknown"),
            "price": round(price, 4),
            "gems": item.get("gems", 0),
            "gem_value": round(gem_value, 4),
            "profit": round(profit, 4),
            "roi_percent": round(roi_percent, 2),
            "gem_sack_price": item.get("gem_sack_price"),
            "gem_value_per_gem": item.get("gem_value_per_gem"),
        })

    results.sort(key=lambda x: x["roi_percent"], reverse=True)

    return results


def filter_results(results, min_roi=0, profitable_only=False):
    if profitable_only:
        results = [r for r in results if r["profit"] > 0]

    results = [r for r in results if r["roi_percent"] >= min_roi]

    return results
