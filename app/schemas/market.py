from datetime import datetime
from pydantic import BaseModel, Field


class LiveQuote(BaseModel):
    symbol: str
    last_price: float
    day_change: float
    day_change_perc: float
    volume: int


class StockRequest(BaseModel):
    trading_symbol: str = Field(min_length=1, max_length=20)


class Candle(BaseModel):
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    open_interest: int | None = None

    @staticmethod
    def convert_to_candle(raw_candle: list) -> "Candle":
        return Candle(
            timestamp=raw_candle[0],
            open=raw_candle[1],
            high=raw_candle[2],
            low=raw_candle[3],
            close=raw_candle[4],
            volume=raw_candle[5],
            open_interest=raw_candle[6],
        )
