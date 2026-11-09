from fastapi import APIRouter, Request

from fastapi import APIRouter, Depends
from app.api.dependencies import get_market_service
from app.services.market_service import MarketService

router = APIRouter()

@router.get("/quote/{trading_symbol}")
async def get_quote(
    trading_symbol: str,
    market_service: MarketService = Depends(get_market_service)
):
    quote = await market_service.get_stock_quote(trading_symbol)
    return quote