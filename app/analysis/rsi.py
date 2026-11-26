
from collections.abc import Sequence


def calculate_rsi(
    prices: Sequence[float],
    period: int = 14
) -> list[float | None]:

    if period <= 0:
        raise ValueError("Period must be greater than zero")

    if len(prices) <= period:
        raise ValueError("Not enough prices to calculate RSI")

    gains: list[float] = []
    losses: list[float] = []

    # 1. Calculate price changes
    for i in range(1, len(prices)):

        change = prices[i] - prices[i - 1]

        gains.append(max(change, 0))
        losses.append(max(-change, 0))

    # 2. Prepare RSI result list
    rsi_values: list[float | None] = [None] * period

    # 3. Calculate initial average gain and loss
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period

    # 4. Calculate first RSI
    if avg_gain == 0 and avg_loss == 0:
        rsi = 50.0

    elif avg_loss == 0:
        rsi = 100.0

    elif avg_gain == 0:
        rsi = 0.0

    else:
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

    rsi_values.append(rsi)

    # 5. Calculate remaining RSI using Wilder smoothing
    for i in range(period, len(gains)):

        avg_gain = (
            (avg_gain * (period - 1) + gains[i]) / period
        )

        avg_loss = (
            (avg_loss * (period - 1) + losses[i]) / period
        )

        if avg_gain == 0 and avg_loss == 0:
            rsi = 50.0

        elif avg_loss == 0:
            rsi = 100.0

        elif avg_gain == 0:
            rsi = 0.0

        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))

        rsi_values.append(rsi)

    return rsi_values
