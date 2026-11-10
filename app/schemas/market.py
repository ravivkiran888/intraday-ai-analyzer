from pydantic import BaseModel, Field



class LiveQuote(BaseModel):
    symbol: str
    last_price: float
    day_change: float
    day_change_perc: float
    volume: int


class StockRequest(BaseModel):
    trading_symbol: str = Field(
        min_length=1,
        max_length=20
    )

    