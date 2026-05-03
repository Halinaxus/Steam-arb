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
def opportunities():
    items = get_market_items()
    results = analyze_items(items)
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
