import httpx
from fastapi import APIRouter, Depends, HTTPException, Path

from app.api.dependencies import get_market_service
from app.services.market_service import MarketService
from app.schemas.market import Candle

router = APIRouter()


@router.get("/quote/{trading_symbol}")
async def get_quote(
    trading_symbol: str = Path(min_length=1, max_length=20),
    market_service: MarketService = Depends(get_market_service),
):
    try:
        quote = await market_service.get_stock_quote(trading_symbol)
        return quote

    except (httpx.HTTPError, RuntimeError) as exc:
        raise HTTPException(
            status_code=502,
            detail="Unable to fetch stock quote from the upstream service",
        ) from exc


@router.get("/candles/{groww_symbol}", response_model=list[Candle])
async def get_historical_candles(
    groww_symbol: str,
    start_time: str,
    end_time: str,
    candle_interval: str = "5minute",
    market_service: MarketService = Depends(get_market_service),
):
    try:
        return await market_service.get_historical_candles(
            groww_symbol, start_time, end_time, candle_interval
        )

    except Exception as exc:
        raise HTTPException(
            status_code=502, detail=f"Unable to fetch historical candles: {str(exc)}"
        )
