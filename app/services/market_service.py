from app.adapters.groww import GrowwMarketDataAdapter
from app.schemas.market import Candle
import asyncio


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

        for symbol, result in zip(symbols, results):
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
