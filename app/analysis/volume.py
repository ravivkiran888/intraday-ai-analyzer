
from collections.abc import Sequence

from app.schemas.market import Candle


# --------------------------------------------------
# 1. Calculate moving average volume
# --------------------------------------------------
def calculate_average_volume(
    volumes: Sequence[int],
    period: int
) -> list[float | None]:

    if period <= 0:
        raise ValueError("Period must be greater than zero")

    if len(volumes) <= period:
        raise ValueError("Not enough previous volume data")

    average_volumes: list[float | None] = [None] * period

    for i in range(period, len(volumes)):

        # Use previous candles only
        window = volumes[i - period:i]

        average = sum(window) / period

        average_volumes.append(average)

    return average_volumes


# --------------------------------------------------
# 2. Calculate Relative Volume
# --------------------------------------------------
def calculate_rvol(
    volumes: Sequence[int],
    average_volumes: Sequence[float | None]
) -> list[float | None]:

    if len(volumes) != len(average_volumes):
        raise ValueError("Both lists must have the same length")

    rvol_values: list[float | None] = []

    for current_volume, average_volume in zip(
        volumes,
        average_volumes
    ):

        if average_volume is None or average_volume <= 0:
            rvol_values.append(None)
            continue

        rvol = current_volume / average_volume

        rvol_values.append(rvol)

    return rvol_values


# --------------------------------------------------
# 3. Classify Volume Strength
# --------------------------------------------------
def classify_volume_strength(
    rvol: float | None
) -> str | None:

    if rvol is None:
        return None

    if rvol < 0.8:
        return "LOW"

    if rvol < 1.5:
        return "NORMAL"

    return "HIGH"


# --------------------------------------------------
# 4. Analyze Volume
# --------------------------------------------------
def analyze_volume(
    volumes: Sequence[int],
    period: int = 20
) -> dict:

    if not volumes:
        raise ValueError("Volume data cannot be empty")

    average_volumes = calculate_average_volume(
        volumes,
        period
    )

    rvol_values = calculate_rvol(
        volumes,
        average_volumes
    )

    volume_strength = [
        classify_volume_strength(rvol)
        for rvol in rvol_values
    ]

    return {
        "current_volume": volumes[-1],
        "average_volume": average_volumes[-1],
        "rvol": rvol_values[-1],
        "volume_strength": volume_strength[-1]
    }


# --------------------------------------------------
# 5. Calculate Previous Average Volume
# --------------------------------------------------
def calculate_previous_average_volume(
    volumes: Sequence[int],
    period: int = 20
) -> float | None:

    if period <= 0:
        raise ValueError("Period must be greater than zero")

    if len(volumes) <= period:
        return None

    previous_volumes = volumes[-(period + 1):-1]

    return sum(previous_volumes) / period


# --------------------------------------------------
# 6. Calculate Time-Slot Average Volume
# --------------------------------------------------
def calculate_time_slot_average_volume(
    historical_candles: Sequence[Candle],
    current_candle: Candle,
    lookback_sessions: int = 5
) -> float | None:

    if lookback_sessions <= 0:
        raise ValueError(
            "Lookback sessions must be positive"
        )

    current_time = current_candle.timestamp.time()
    current_date = current_candle.timestamp.date()

    # Group matching candles by trading date
    matching_by_date = {}

    for candle in historical_candles:

        candle_date = candle.timestamp.date()

        # Exclude current and future dates
        if candle_date >= current_date:
            continue

        # Match the same time slot
        if candle.timestamp.time() != current_time:
            continue

        matching_by_date[candle_date] = candle.volume

    # Select the latest distinct trading sessions
    selected_dates = sorted(matching_by_date.keys())[
        -lookback_sessions:
    ]

    if not selected_dates:
        return None

    matching_volumes = [
        matching_by_date[date]
        for date in selected_dates
    ]

    return sum(matching_volumes) / len(matching_volumes)
