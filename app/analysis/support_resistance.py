
from collections.abc import Sequence

from app.schemas.market import Candle


def identify_support_resistance(
    candles: Sequence[Candle],
    lookback: int = 20
) -> dict:

    if lookback < 3:
        raise ValueError("Lookback must be at least 3")

    if len(candles) < lookback:
        raise ValueError("Not enough candles")

    recent_candles = candles[-lookback:]

    support = min(
        candle.low for candle in recent_candles
    )

    resistance = max(
        candle.high for candle in recent_candles
    )

    return {
        "support": support,
        "resistance": resistance
    }
