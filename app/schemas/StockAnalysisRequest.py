from pydantic import BaseModel, Field


class StockAnalysisRequest(BaseModel):
    symbol: str = Field(
        min_length=1,
        max_length=20
    )

    candle_interval: int = Field(
        gt=0
    )

    period: int = Field(
        gt=0
    )