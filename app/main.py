
import os
import httpx

from pathlib import Path
from dotenv import load_dotenv
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.adapters.groww import GrowwMarketDataAdapter

from app.api.routes.market import router as market_router
from app.api.routes.market_v2 import router as market_v2_router

from app.services.market_service import MarketService
from app.services.technical_analysis_service import TechnicalAnalysisService
from app.api.routes.analysis import router as analysis_router
from app.analysis.analysis_service import AnalysisService


BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


@asynccontextmanager
async def lifespan(app: FastAPI):

    api_key = os.getenv("GROWW_API_KEY")

    if not api_key:
        raise RuntimeError("GROWW_API_KEY is missing")

    # 1. Configure connection limits
    limits = httpx.Limits(
        max_connections=20,
        max_keepalive_connections=10,
        keepalive_expiry=30
    )

    # 2. Configure HTTP timeouts
    timeout = httpx.Timeout(
        10.0,
        connect=5.0,
        pool=3.0
    )

    # 3. Create reusable HTTP client
    async with httpx.AsyncClient(
        base_url=os.getenv(
            "GROWW_BASE_URL",
            "https://api.groww.in"
        ),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
            "X-API-VERSION": "1.0",
        },
        limits=limits,
        timeout=timeout,
    ) as client:

        # 4. Initialize Groww adapter
        app.state.groww = GrowwMarketDataAdapter(client)

        # 5. Initialize MarketService
        app.state.market_service = MarketService(
            app.state.groww
        )

        # 6. Initialize TechnicalAnalysisService
        app.state.technical_analysis_service = (
            TechnicalAnalysisService()
        )

        # 7. Initialize AnalysisService
        app.state.analysis_service = AnalysisService(
            market_service=app.state.market_service,
            technical_analysis_service=app.state.technical_analysis_service
        )

        yield


app = FastAPI(lifespan=lifespan)


# API routes
app.include_router(
    market_router,
    prefix="/api/v1/market",
    tags=["Market"]
)

app.include_router(
    market_v2_router,
    prefix="/api/v2/market",
    tags=["Market V2"]
)

app.include_router(
    analysis_router,
    prefix="/api/v1/analysis",
    tags=["Technical Analysis"]
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "UP"}
