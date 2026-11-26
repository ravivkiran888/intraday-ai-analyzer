
import asyncio

from datetime import datetime, timedelta

from app.adapters.groww import GrowwMarketDataAdapter
from app.schemas.market import Candle, SectorQuote


class MarketService:

    def __init__(
        self,
        groww_adapter: GrowwMarketDataAdapter
    ):
        self.groww_adapter = groww_adapter

    # --------------------------------------------------
    # 1. Get single stock quote
    # --------------------------------------------------
    async def get_stock_quote(self, symbol: str):

        quote = await self.groww_adapter.get_live_quote(symbol)

        return quote

    # --------------------------------------------------
    # 2. Get multiple stock quotes
    # --------------------------------------------------
    async def get_multiple_quotes(self, symbols: list[str]):

        tasks = [
            self.get_stock_quote(symbol)
            for symbol in symbols
        ]

        results = await asyncio.gather(
            *tasks,
            return_exceptions=True
        )

        successful_quotes = []
        failed_quotes = []

        for symbol, result in zip(symbols, results):

            if isinstance(result, Exception):

                failed_quotes.append({
                    "symbol": symbol,
                    "error": str(result)
                })

            else:
                successful_quotes.append(result)

        return {
            "successful_quotes": successful_quotes,
            "failed_quotes": failed_quotes
        }

    # --------------------------------------------------
    # 3. Get historical candles
    # --------------------------------------------------
    async def get_historical_candles(
        self,
        groww_symbol: str,
        start_time: str,
        end_time: str,
        candle_interval: str = "5minute"
    ) -> list[Candle]:

        response = await self.groww_adapter.get_historical_candles(
            groww_symbol=groww_symbol,
            start_time=start_time,
            end_time=end_time,
            candle_interval=candle_interval
        )

        if response.get("status") != "SUCCESS":
            raise ValueError(
                "Unable to fetch historical candles from Groww"
            )

        raw_candles = response.get(
            "payload", {}
        ).get("candles", [])

        candles = []

        for raw_candle in raw_candles:

            # Skip candles with missing OHLC values
            if any(value is None for value in raw_candle[1:5]):
                continue

            candles.append(
                Candle.convert_to_candle(raw_candle)
            )

        return candles

    # --------------------------------------------------
    # 4. Get sector quote
    # --------------------------------------------------
    async def get_sector_quote(
        self,
        sector_symbol: str
    ) -> SectorQuote:

        response = await self.groww_adapter.get_sector_quote(
            sector_symbol
        )

        payload = response.get("payload", {})

        ohlc = payload.get("ohlc") or {}

        return SectorQuote(
            symbol=sector_symbol,
            last_price=payload.get("last_price"),
            day_change=payload.get("day_change"),
            day_change_perc=payload.get("day_change_perc"),
            open=ohlc.get("open"),
            high=ohlc.get("high"),
            low=ohlc.get("low"),
            close=ohlc.get("close"),
            week_52_high=payload.get("week_52_high"),
            week_52_low=payload.get("week_52_low")
        )

    # --------------------------------------------------
    # 5. Get historical warm-up candles
    # --------------------------------------------------
    async def get_warmup_candles(
        self,
        groww_symbol: str
    ) -> list[Candle]:

        # 1. Define historical date range
        today = datetime.now().date()

        end_date = today - timedelta(days=1)
        start_date = today - timedelta(days=15)

        start_time = datetime.combine(
            start_date,
            datetime.min.time()
        ).replace(
            hour=9,
            minute=15
        )

        end_time = datetime.combine(
            end_date,
            datetime.min.time()
        ).replace(
            hour=15,
            minute=30
        )

        # 2. Fetch historical candles
        candles = await self.get_historical_candles(
            groww_symbol=groww_symbol,
            start_time=start_time.strftime("%Y-%m-%d %H:%M:%S"),
            end_time=end_time.strftime("%Y-%m-%d %H:%M:%S"),
            candle_interval="5minute"
        )

        if not candles:
            raise ValueError(
                "No historical candles available for warm-up"
            )

        # 3. Identify available trading dates
        trading_dates = sorted({
            candle.timestamp.date()
            for candle in candles
            if candle.timestamp.date() < today
        })

        # 4. Select latest five trading sessions
        selected_dates = set(trading_dates[-5:])

        # 5. Keep all candles from selected sessions
        warmup_candles = [
            candle
            for candle in candles
            if candle.timestamp.date() in selected_dates
        ]

        if not warmup_candles:
            raise ValueError(
                "Unable to find historical trading sessions"
            )

        return warmup_candles

    # --------------------------------------------------
    # 6. Get today's completed 5-minute candles
    # --------------------------------------------------
    async def get_today_candles(
        self,
        groww_symbol: str
    ) -> list[Candle]:

        now = datetime.now()
        today = now.date()

        market_open = datetime.combine(
            today,
            datetime.min.time()
        ).replace(
            hour=9,
            minute=15
        )

        market_close = datetime.combine(
            today,
            datetime.min.time()
        ).replace(
            hour=15,
            minute=30
        )

        if now <= market_open:
            return []

        end_time = min(now, market_close)

        candles = await self.get_historical_candles(
            groww_symbol=groww_symbol,
            start_time=market_open.strftime("%Y-%m-%d %H:%M:%S"),
            end_time=end_time.strftime("%Y-%m-%d %H:%M:%S"),
            candle_interval="5minute"
        )

        # Include only completed 5-minute candles
        completed_until = end_time - timedelta(minutes=5)

        completed_candles = [
            candle
            for candle in candles
            if market_open <= candle.timestamp <= completed_until
        ]

        return completed_candles

    # --------------------------------------------------
    # 7. Get candles required for technical analysis
    # --------------------------------------------------
    async def get_analysis_candles(
        self,
        groww_symbol: str
    ) -> dict:

        # Convert trading symbol into Groww historical symbol
        if not groww_symbol.startswith("NSE-"):
            groww_symbol = f"NSE-{groww_symbol}"

        # Fetch historical and today's candles concurrently
        historical_candles, today_candles = await asyncio.gather(
            self.get_warmup_candles(groww_symbol),
            self.get_today_candles(groww_symbol)
        )

        # Return both datasets separately
        return {
            "historical_candles": historical_candles,
            "today_candles": today_candles
        }

    # --------------------------------------------------
    # 8. Separate historical and today's candles
    # --------------------------------------------------
    def separate_today_candles(
        self,
        candles: list[Candle]
    ):

        today = datetime.now().date()

        historical_candles = [
            candle
            for candle in candles
            if candle.timestamp.date() < today
        ]

        today_candles = [
            candle
            for candle in candles
            if candle.timestamp.date() == today
        ]

        return historical_candles, today_candles
