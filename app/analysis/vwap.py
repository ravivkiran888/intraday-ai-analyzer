
from collections.abc import Sequence


def calculate_vwap(
    highs: Sequence[float],
    lows: Sequence[float],
    closes: Sequence[float],
    volumes: Sequence[int | float]
) -> list[float | None]:

    if not (
        len(highs) == len(lows)
        == len(closes) == len(volumes)
    ):
        raise ValueError("All input lists must have equal length")

    cumulative_price_volume = 0.0
    cumulative_volume = 0.0

    vwap_values: list[float | None] = []

    for high, low, close, volume in zip(
        highs, lows, closes, volumes
    ):

        typical_price = (high + low + close) / 3

        cumulative_price_volume += typical_price * volume
        cumulative_volume += volume

        if cumulative_volume == 0:
            vwap_values.append(None)
        else:
            vwap = cumulative_price_volume / cumulative_volume
            vwap_values.append(vwap)

    return vwap_values
