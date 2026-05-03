from fastapi import FastAPI
from app.steam import get_market_items
from app.calc import analyze_items

app = FastAPI(
    title="Steam Arbitrage Scanner",
    description="Find potential Steam Market card/gem arbitrage opportunities.",
    version="0.1.0"
)


@app.get("/")
def root():
    return {
        "message": "Steam Arbitrage API running",
        "endpoints": {
            "opportunities": "/opportunities",
            "health": "/health"
        }
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/opportunities")
def opportunities(min_roi: float = 0, profitable_only: bool = False):
    items = get_market_items()
    results = analyze_items(items)

    if profitable_only:
        results = [r for r in results if r["profit"] > 0]

    results = [r for r in results if r["roi_percent"] >= min_roi]

    return {
        "count": len(results),
        "results": results
    }


@app.get("/raw-items")
def raw_items():
    items = get_market_items()
    return {
        "count": len(items),
        "items": items
    }
