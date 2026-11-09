from app.services.market_service import MarketService
from fastapi import Request


def get_market_service(request: Request) -> MarketService:
    return request.app.state.market_service