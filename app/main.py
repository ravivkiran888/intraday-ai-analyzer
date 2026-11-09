import os
import httpx

from pathlib import Path
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException

from app.adapters.groww import GrowwMarketDataAdapter
from app.api.routes.market import router as market_router
from app.services.market_service import MarketService


BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

print("Groww API key loaded:", bool(os.getenv("GROWW_API_KEY")))

@asynccontextmanager
async def lifespan(app: FastAPI):

    api_key = os.getenv("GROWW_API_KEY")
 
    if not api_key:
        raise RuntimeError("GROWW_API_KEY is missing")

    # 1. Configure connection limits
    limits = httpx.Limits(
        max_connections=20,
        max_keepalive_connections=10,
        keepalive_expiry=30
    )

    # 2. Configure HTTP timeouts
    timeout = httpx.Timeout(
        10.0,
        connect=5.0,
        pool=3.0
    )

    # 3. Create reusable HTTP client
    async with httpx.AsyncClient(
        base_url=os.getenv(
            "GROWW_BASE_URL",
            "https://api.groww.in"
        ),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
            "X-API-VERSION": "1.0"
        },
        limits=limits,
        timeout=timeout
    ) as client:

        app.state.groww = GrowwMarketDataAdapter(client)
        app.state.market_service = MarketService(app.state.groww)

        print("Groww HTTP client initialized")

        yield

    print("Groww HTTP client closed")


app = FastAPI(lifespan=lifespan)
app.include_router(
    market_router,
    prefix="/api/v1/market",
    tags=["Market"]
)


@app.get("/health")
async def health():
    return {"status": "UP"}

