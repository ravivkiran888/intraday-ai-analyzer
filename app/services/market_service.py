from app.adapters.groww import GrowwMarketDataAdapter


class MarketService:

    def __init__(self, groww_adapter: GrowwMarketDataAdapter):
        self.groww_adapter = groww_adapter

    async def get_stock_quote(self, symbol: str):

        quote = await self.groww_adapter.get_live_quote(symbol)

        return quote


    async def get_historical_candles(
        self,
        groww_symbol: str,
        start_time: str,
        end_time: str,
        candle_interval: str = "5minute",
    ):
        candles = await self.groww_adapter.get_historical_candles(
            groww_symbol, start_time, end_time, candle_interval
        )

        return candles
