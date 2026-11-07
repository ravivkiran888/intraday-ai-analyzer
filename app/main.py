import os
from contextlib import asynccontextmanager

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request

from app.adapters.groww import GrowwMarketDataAdapter

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):

    api_key = os.getenv("GROWW_API_KEY")

    if not api_key:
        raise RuntimeError("GROWW_API_KEY is not configured")

    async with httpx.AsyncClient(
        base_url="https://api.groww.in",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
            "X-API-VERSION": "1.0"
        },
        timeout=10.0,
        limits=httpx.Limits(
            max_connections=30,
            max_keepalive_connections=20
        )
    ) as client:

        app.state.groww = GrowwMarketDataAdapter(client)

        yield


app = FastAPI(
    title="Intraday AI Stock Analyzer",
    lifespan=lifespan
)


@app.get("/health")
async def health_check():
    return {"status": "UP"}


@app.get("/api/v1/market/quote/{trading_symbol}")
async def get_live_quote(
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
            detail=f"Groww returned HTTP {exc.response.status_code}"
        )

    except httpx.RequestError:
        raise HTTPException(
            status_code=502,
            detail="Unable to connect to Groww"
        )

    except (RuntimeError, KeyError, ValueError) as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc)
        )