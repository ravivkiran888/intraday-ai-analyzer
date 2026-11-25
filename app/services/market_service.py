import asyncio

from app.adapters.groww import GrowwMarketDataAdapter
from app.schemas.market import Candle, SectorQuote

class MarketService:

    def __init__(self, groww_adapter: GrowwMarketDataAdapter):
        self.groww_adapter = groww_adapter

    async def get_stock_quote(self, symbol: str):
        quote = await self.groww_adapter.get_live_quote(symbol)
        return quote

    async def get_multiple_quotes(self, symbols: list[str]):
        tasks = [self.get_stock_quote(symbol) for symbol in symbols]

        results = await asyncio.gather(
            *tasks,
            return_exceptions=True,
        )

        quotes = []

        for _, result in zip(symbols, results):
            if not isinstance(result, Exception):
                quotes.append(result)

        return quotes

    async def get_historical_candles(
        self,
        groww_symbol: str,
        start_time: str,
        end_time: str,
        candle_interval: str = "5minute",
    ):
        response = await self.groww_adapter.get_historical_candles(
            groww_symbol, start_time, end_time, candle_interval
        )

        raw_candles = response["payload"]["candles"]

        candles = [Candle.convert_to_candle(raw_candle) for raw_candle in raw_candles]

        return candles

    async def get_sector_quote(self, sector_symbol: str) -> SectorQuote:
        data = await self.groww_adapter.get_sector_quote(sector_symbol)

        if data.get("status") != "SUCCESS":
            raise RuntimeError("Groww sector quote request failed")

        payload = data["payload"]
        ohlc = payload.get("ohlc") or {}

        return SectorQuote(
            symbol=sector_symbol.upper(),
            last_price=payload["last_price"],
            day_change=payload["day_change"],
            day_change_perc=payload["day_change_perc"],
            open=ohlc.get("open"),
            high=ohlc.get("high"),
            low=ohlc.get("low"),
            close=ohlc.get("close"),
            week_52_high=payload.get("week_52_high"),
            week_52_low=payload.get("week_52_low"),
        )
