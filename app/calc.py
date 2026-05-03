def analyze_items(items):
    results = []

    for item in items:
        gem_value = item["gems"] * 0.001
        profit = gem_value - item["price"]

        results.append({
            "name": item["name"],
            "profit": profit
        })

    return results
