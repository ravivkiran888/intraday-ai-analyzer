
from app.schemas.market import Candle


def detect_breakout(
    previous_candle: Candle,
    current_candle: Candle,
    support: float,
    resistance: float,
    average_volume: float,
    min_rvol: float = 1.5
) -> dict:

    # 1. Validate inputs
    if average_volume <= 0:
        raise ValueError(
            "Average volume must be greater than zero"
        )

    if support <= 0 or resistance <= 0:
        raise ValueError(
            "Support and resistance must be greater than zero"
        )

    if support >= resistance:
        raise ValueError(
            "Support must be below resistance"
        )

    if min_rvol <= 0:
        raise ValueError(
            "Minimum RVOL must be greater than zero"
        )

    # 2. Calculate relative volume
    current_rvol = current_candle.volume / average_volume

    # 3. Fresh bullish breakout
    if (
        previous_candle.close <= resistance
        and current_candle.close > resistance
    ):

        volume_confirmed = current_rvol >= min_rvol

        return {
            "breakout": True,
            "direction": "BULLISH",
            "volume_confirmed": volume_confirmed,
            "rvol": current_rvol,
            "action": (
                "LOOK_FOR_BUY_SETUP"
                if volume_confirmed
                else "WAIT_FOR_CONFIRMATION"
            ),
            "reason": "Price crossed above resistance"
        }

    # 4. Fresh bearish breakdown
    if (
        previous_candle.close >= support
        and current_candle.close < support
    ):

        volume_confirmed = current_rvol >= min_rvol

        return {
            "breakout": True,
            "direction": "BEARISH",
            "volume_confirmed": volume_confirmed,
            "rvol": current_rvol,
            "action": (
                "LOOK_FOR_SELL_SETUP"
                if volume_confirmed
                else "WAIT_FOR_CONFIRMATION"
            ),
            "reason": "Price crossed below support"
        }

    # 5. No fresh breakout
    return {
        "breakout": False,
        "direction": "NONE",
        "volume_confirmed": False,
        "rvol": current_rvol,
        "action": "WAIT",
        "reason": "No fresh breakout detected"
    }
