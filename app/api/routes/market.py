from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.dependencies import get_market_service
from app.schemas.market import Candle, LiveQuote, SectorQuote
from app.schemas.StockAnalysisRequest import StockAnalysisRequest
from app.services.market_service import MarketService

router = APIRouter()


@router.get("/quote/{trading_symbol}")
async def get_quote(
    trading_symbol: str,
    market_service: MarketService = Depends(get_market_service),
):
    try:
        quote = await market_service.get_stock_quote(trading_symbol)
        return quote

    except RuntimeError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc)
        )


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


@router.get("/quotes", response_model=list[LiveQuote])
async def get_multiple_quotes(
    symbols: list[str] = Query(...),
    market_service: MarketService = Depends(get_market_service),
):
    try:
        return await market_service.get_multiple_quotes(symbols)
    except Exception as exc:
        raise HTTPException(
            status_code=502, detail=f"Unable to fetch stock quotes: {str(exc)}"
        )


@router.post("/analyze")
async def analyze_stock(request: StockAnalysisRequest):
    return {
        "symbol": request.symbol,
        "candle_interval": request.candle_interval,
        "period": request.period,
    }


@router.get("/sector/{sector_symbol}", response_model=SectorQuote)
async def get_sector_quote(
    sector_symbol: str,
    market_service: MarketService = Depends(get_market_service),
):
    try:
        return await market_service.get_sector_quote(sector_symbol)
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
