from collections.abc import Sequence

def calculate_ema(
    prices: Sequence[float],
    period: int
) -> list[float | None]:

    if period <= 0:
        raise ValueError("Period must be greater than zero")

    if len(prices) < period:
        raise ValueError("Not enough prices to calculate EMA")

    multiplier = 2 / (period + 1)

    # Initialize EMA list
    ema_values: list[float | None] = [None] * (period - 1)

    # Calculate initial EMA using Simple Moving Average
    initial_ema = sum(prices[:period]) / period

    ema_values.append(initial_ema)

    # Calculate remaining EMA values
    for price in prices[period:]:

        previous_ema = ema_values[-1]

        if previous_ema is None:
            raise ValueError("Previous EMA cannot be None")

        current_ema = (
            price * multiplier
            + previous_ema * (1 - multiplier)
        )

        ema_values.append(current_ema)

    return ema_values
