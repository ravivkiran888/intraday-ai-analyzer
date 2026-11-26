
import asyncio
import os
import httpx

from pathlib import Path
from dotenv import load_dotenv

from app.adapters.groww import GrowwMarketDataAdapter
from app.services.market_service import MarketService
from app.services.technical_analysis_service import TechnicalAnalysisService


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


async def main():

    api_key = os.getenv("GROWW_API_KEY")

    if not api_key:
        raise RuntimeError("GROWW_API_KEY is missing")

    async with httpx.AsyncClient(
        base_url=os.getenv("GROWW_BASE_URL", "https://api.groww.in"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
            "X-API-VERSION": "1.0"
        },
        timeout=20.0
    ) as client:

        groww_adapter = GrowwMarketDataAdapter(client)
        market_service = MarketService(groww_adapter)

        candles = await market_service.get_historical_candles(
            "NSE-RELIANCE",
            "2025-09-24 09:15:00",
            "2025-09-24 15:30:00",
            "5minute"
        )

        print("Total candles:", len(candles))

        analysis_service = TechnicalAnalysisService()

        result = analysis_service.analyze(candles)

        print("Technical Analysis Result:")
        print(result)


if __name__ == "__main__":
    asyncio.run(main())
