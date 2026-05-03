from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.steam import get_market_items, get_booster_opportunities
from app.calc import analyze_items, filter_results

app = FastAPI(
    title="Steam Arbitrage Scanner",
    description="Find Steam Market card/gem/booster arbitrage opportunities.",
    version="0.2.0",
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/")
def frontend():
    return FileResponse("app/static/index.html")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/opportunities")
def opportunities(
    query: str = "trading card",
    min_roi: float = 0,
    profitable_only: bool = False,
):
    items = get_market_items(query=query)
    results = analyze_items(items)
    results = filter_results(
        results,
        min_roi=min_roi,
        profitable_only=profitable_only,
    )

    return {
        "query": query,
        "count": len(results),
        "results": results,
    }


@app.get("/booster-opportunities")
def booster_opportunities(
    min_roi: float = 0,
    profitable_only: bool = False,
):
    results = get_booster_opportunities()
    results = filter_results(
        results,
        min_roi=min_roi,
        profitable_only=profitable_only,
    )

    return {
        "count": len(results),
        "results": results,
    }


@app.get("/raw-items")
def raw_items(query: str = "trading card"):
    items = get_market_items(query=query)

    return {
        "query": query,
        "count": len(items),
        "items": items,
    }
