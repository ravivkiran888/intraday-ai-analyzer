import httpx
from fastapi import APIRouter, Depends, HTTPException, Path

from app.api.dependencies import get_market_service
from app.services.market_service import MarketService

router = APIRouter()


@router.get("/quote/{trading_symbol}")
async def get_quote(
    trading_symbol: str = Path(min_length=1, max_length=20),
    market_service: MarketService = Depends(get_market_service)
):
    try:
        quote = await market_service.get_stock_quote(trading_symbol)
        return quote

    except (httpx.HTTPError, RuntimeError) as exc:
        raise HTTPException(
            status_code=502,
            detail="Unable to fetch stock quote from the upstream service"
        ) from exc