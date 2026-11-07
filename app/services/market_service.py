from app.adapters.groww import GrowwMarketDataAdapter


  class MarketService:

    def __init__(self, groww_adapter: GrowwMarketDataAdapter):
        self.groww_adapter = groww_adapter

    async def get_stock_quote(self, symbol: str):

        quote = await self.groww_adapter.get_live_quote(symbol)

        return quote