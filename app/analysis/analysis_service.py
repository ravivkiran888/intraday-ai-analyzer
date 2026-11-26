
from app.services.market_service import MarketService
from app.services.technical_analysis_service import TechnicalAnalysisService


class AnalysisService:

    def __init__(
        self,
        market_service: MarketService,
        technical_analysis_service: TechnicalAnalysisService
    ):
        self.market_service = market_service
        self.technical_analysis_service = technical_analysis_service

    async def analyze_stock(self, groww_symbol: str) -> dict:

        # Step 1: Fetch historical and today's completed candles
        candle_data = await self.market_service.get_analysis_candles(
            groww_symbol
        )

        historical_candles = candle_data["historical_candles"]
        session_candles = candle_data["today_candles"]

        analysis_mode = "LIVE_SESSION"

        # Step 2: If today's candles are unavailable,
        # select the most recent available trading session.
        if not session_candles:

            if not historical_candles:
                raise ValueError(
                    "No historical candles available for analysis"
                )

            latest_session_date = max(
                candle.timestamp.date()
                for candle in historical_candles
            )

            session_candles = [
                candle
                for candle in historical_candles
                if candle.timestamp.date() == latest_session_date
            ]

            historical_candles = [
                candle
                for candle in historical_candles
                if candle.timestamp.date() < latest_session_date
            ]

            analysis_mode = "LAST_AVAILABLE_SESSION"

        # Step 3: Run technical analysis
        analysis_result = self.technical_analysis_service.analyze(
            historical_candles=historical_candles,
            today_candles=session_candles
        )

        # Step 4: Return analysis with session information
        return {
            "symbol": groww_symbol,
            "analysis_mode": analysis_mode,
            "analysis_session_date": (
                session_candles[-1].timestamp.date().isoformat()
            ),
            "candles_count": len(session_candles),
            "analysis": analysis_result
        }
