import os
import httpx

from pathlib import Path
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException

from app.adapters.groww import GrowwMarketDataAdapter

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

        print("Groww HTTP client initialized")

        yield

    print("Groww HTTP client closed")


app = FastAPI(lifespan=lifespan)


@app.get("/health")
async def health():
    return {"status": "UP"}


@app.get("/api/v1/market/quote/{trading_symbol}")
async def get_quote(
    trading_symbol: str,
    request: Request
):
    try:
        return await request.app.state.groww.get_live_quote(
            trading_symbol
        )

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="Groww API request timed out"
        )

    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Groww API returned HTTP {exc.response.status_code}"
        )

    except httpx.RequestError:
        raise HTTPException(
            status_code=502,
            detail="Unable to connect to Groww API"
        )