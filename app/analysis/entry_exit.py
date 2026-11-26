
from app.schemas.market import Candle


# --------------------------------------------------
# 1. Identify Market Bias
# --------------------------------------------------
def identify_market_bias(
    analysis_5min: dict,
    analysis_15min: dict
) -> dict:

    trend_5min = analysis_5min["interpretation"]["trend"]
    trend_15min = analysis_15min["interpretation"]["trend"]

    price_5min = analysis_5min["interpretation"]["price_position"]
    price_15min = analysis_15min["interpretation"]["price_position"]

    momentum_5min = analysis_5min["interpretation"]["momentum"]

    # Bullish conditions
    if (
        trend_5min == "BULLISH"
        and trend_15min == "BULLISH"
        and price_5min == "ABOVE_VWAP"
        and price_15min == "ABOVE_VWAP"
        and momentum_5min == "POSITIVE"
    ):
        return {
            "market_bias": "BULLISH",
            "action": "LOOK_FOR_BUY_SETUP",
            "reason": "Both timeframes show bullish conditions"
        }

    # Bearish conditions
    if (
        trend_5min == "BEARISH"
        and trend_15min == "BEARISH"
        and price_5min == "BELOW_VWAP"
        and price_15min == "BELOW_VWAP"
        and momentum_5min == "NEGATIVE"
    ):
        return {
            "market_bias": "BEARISH",
            "action": "LOOK_FOR_SELL_SETUP",
            "reason": "Both timeframes show bearish conditions"
        }

    return {
        "market_bias": "NEUTRAL",
        "action": "WAIT",
        "reason": "Timeframes or indicators are not sufficiently aligned"
    }


# --------------------------------------------------
# 2. Calculate Entry, Stop Loss and Target
# --------------------------------------------------
def calculate_trade_levels(
    direction: str,
    entry_price: float,
    stop_loss: float,
    risk_reward_ratio: float = 2.0
) -> dict:

    if entry_price <= 0 or stop_loss <= 0:
        raise ValueError("Prices must be greater than zero")

    if risk_reward_ratio <= 0:
        raise ValueError(
            "Risk reward ratio must be greater than zero"
        )

    if direction == "BULLISH":

        if stop_loss >= entry_price:
            raise ValueError(
                "Bullish stop-loss must be below entry"
            )

        risk = entry_price - stop_loss
        target = entry_price + (risk * risk_reward_ratio)

    elif direction == "BEARISH":

        if stop_loss <= entry_price:
            raise ValueError(
                "Bearish stop-loss must be above entry"
            )

        risk = stop_loss - entry_price
        target = entry_price - (risk * risk_reward_ratio)

    else:
        raise ValueError(
            "Direction must be BULLISH or BEARISH"
        )

    return {
        "direction": direction,
        "entry_price": entry_price,
        "stop_loss": stop_loss,
        "target_price": target,
        "risk_per_share": risk,
        "reward_per_share": abs(target - entry_price),
        "risk_reward_ratio": risk_reward_ratio
    }


# --------------------------------------------------
# 3. Generate Trade Setup
# --------------------------------------------------
def generate_trade_setup(
    breakout_analysis: dict,
    current_candle: Candle,
    risk_reward_ratio: float = 2.0
) -> dict:

    if not isinstance(breakout_analysis, dict):
        return {
            "trade_setup": False,
            "reason": "Breakout analysis is unavailable"
        }

    if not breakout_analysis.get("breakout", False):
        return {
            "trade_setup": False,
            "reason": "No breakout detected"
        }

    if not breakout_analysis.get("volume_confirmed", False):
        return {
            "trade_setup": False,
            "reason": "Breakout volume is not confirmed"
        }

    direction = breakout_analysis.get("direction")

    if direction == "BULLISH":

        entry_price = current_candle.close
        stop_loss = current_candle.low

    elif direction == "BEARISH":

        entry_price = current_candle.close
        stop_loss = current_candle.high

    else:
        return {
            "trade_setup": False,
            "reason": "Invalid breakout direction"
        }

    try:

        trade_levels = calculate_trade_levels(
            direction=direction,
            entry_price=entry_price,
            stop_loss=stop_loss,
            risk_reward_ratio=risk_reward_ratio
        )

    except ValueError as exc:

        return {
            "trade_setup": False,
            "reason": str(exc)
        }

    return {
        "trade_setup": True,
        "reason": "Breakout confirmed with volume",
        "trade_levels": trade_levels
    }


# --------------------------------------------------
# 4. Generate Final Trading Decision
# --------------------------------------------------

def generate_final_decision(
    analysis_5min: dict,
    analysis_15min: dict
) -> dict:

    interpretation_5min = analysis_5min["interpretation"]
    interpretation_15min = analysis_15min["interpretation"]

    # 1. Read 5-minute indicators
    trend_5min = interpretation_5min["trend"]
    momentum_5min = interpretation_5min["momentum"]
    price_position_5min = interpretation_5min["price_position"]

    # 2. Read 15-minute indicators
    trend_15min = interpretation_15min["trend"]
    price_position_15min = interpretation_15min["price_position"]

    # 3. Check indicator availability
    if (
        "UNAVAILABLE" in (
            trend_5min,
            momentum_5min,
            price_position_5min,
            trend_15min,
            price_position_15min
        )
    ):
        return {
            "decision": "WAIT",
            "reason": "Required timeframe indicators are unavailable"
        }

    # 4. Get 5-minute breakout and trade setup
    indicators_5min = analysis_5min["indicators"]

    breakout_5min = indicators_5min["breakout_analysis"]
    trade_setup_5min = indicators_5min["trade_setup"]

    if not isinstance(breakout_5min, dict):
        return {
            "decision": "WAIT",
            "reason": "Breakout analysis is unavailable"
        }

    if not isinstance(trade_setup_5min, dict):
        return {
            "decision": "WAIT",
            "reason": "Trade setup is unavailable"
        }

    # 5. Verify fresh breakout
    if not breakout_5min.get("breakout", False):
        return {
            "decision": "WAIT",
            "reason": "No fresh breakout detected"
        }

    # 6. Verify volume confirmation
    if not breakout_5min.get("volume_confirmed", False):
        return {
            "decision": "WAIT",
            "reason": "Breakout volume is not confirmed"
        }

    # 7. Verify trade setup
    if not trade_setup_5min.get("trade_setup", False):
        return {
            "decision": "WAIT",
            "reason": trade_setup_5min.get(
                "reason",
                "No valid trade setup"
            )
        }

    trade_levels = trade_setup_5min.get("trade_levels")

    if not isinstance(trade_levels, dict):
        return {
            "decision": "WAIT",
            "reason": "Trade levels are unavailable"
        }

    direction = breakout_5min.get("direction")

    # 8. Strict bullish confirmation
    if (
        direction == "BULLISH"
        and trend_5min == "BULLISH"
        and momentum_5min == "POSITIVE"
        and price_position_5min == "ABOVE_VWAP"
        and trend_15min == "BULLISH"
        and price_position_15min == "ABOVE_VWAP"
    ):
        return {
            "decision": "BUY_SETUP",
            "reason": "Both timeframes confirm bullish trend, VWAP and momentum with volume-confirmed breakout",
            "trade_levels": trade_levels
        }

    # 9. Strict bearish confirmation
    if (
        direction == "BEARISH"
        and trend_5min == "BEARISH"
        and momentum_5min == "NEGATIVE"
        and price_position_5min == "BELOW_VWAP"
        and trend_15min == "BEARISH"
        and price_position_15min == "BELOW_VWAP"
    ):
        return {
            "decision": "SELL_SETUP",
            "reason": "Both timeframes confirm bearish trend, VWAP and momentum with volume-confirmed breakdown",
            "trade_levels": trade_levels
        }

    # 10. Conditions are not fully aligned
    return {
        "decision": "WAIT",
        "reason": "Strict confirmation failed: trend, momentum, VWAP or timeframe alignment"
    }
