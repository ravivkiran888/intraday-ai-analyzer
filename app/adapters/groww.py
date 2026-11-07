import httpx

from app.schemas.market import LiveQuote


class GrowwMarketDataAdapter:

    def __init__(self, client: httpx.AsyncClient):
        self.client = client

    async def get_live_quote(
        self,
        trading_symbol: str
    ) -> LiveQuote:

        response = await self.client.get(
            "/v1/live-data/quote",
            params={
                "exchange": "NSE",
                "segment": "CASH",
                "trading_symbol": trading_symbol.upper()
            }
        )

        response.raise_for_status()

        data = response.json()

        if data.get("status") != "SUCCESS":
            raise RuntimeError("Groww API request failed")

        payload = data.get("payload")

        if not payload:
            raise RuntimeError("Groww response has no payload")

        return LiveQuote(
            symbol=trading_symbol.upper(),
            last_price=payload["last_price"],
            day_change=payload["day_change"],
            day_change_perc=payload["day_change_perc"],
            volume=payload["volume"]
        )