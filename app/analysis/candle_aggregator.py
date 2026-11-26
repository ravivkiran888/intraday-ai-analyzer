
from collections import defaultdict
from datetime import timedelta

from app.schemas.market import Candle


def aggregate_5min_to_15min(
    candles: list[Candle]
) -> list[Candle]:

    groups = defaultdict(list)

    # 1. Group 5-minute candles into 15-minute buckets
    for candle in candles:

        timestamp = candle.timestamp

        session_start = timestamp.replace(
            hour=9,
            minute=15,
            second=0,
            microsecond=0
        )

        market_close = timestamp.replace(
            hour=15,
            minute=30,
            second=0,
            microsecond=0
        )

        # Ignore candles outside regular NSE market hours
        if timestamp < session_start or timestamp >= market_close:
            continue

        minutes_from_open = int(
            (timestamp - session_start).total_seconds() // 60
        )

        bucket = minutes_from_open // 15

        # Group by trading date and 15-minute bucket
        groups[(timestamp.date(), bucket)].append(candle)

    aggregated_candles = []

    # 2. Process each 15-minute group
    for (session_date, bucket), group in sorted(groups.items()):

        session_start = group[0].timestamp.replace(
            hour=9,
            minute=15,
            second=0,
            microsecond=0
        )

        bucket_start = session_start + timedelta(
            minutes=bucket * 15
        )

        # Expected three 5-minute candle timestamps
        expected_timestamps = [
            bucket_start,
            bucket_start + timedelta(minutes=5),
            bucket_start + timedelta(minutes=10)
        ]

        actual_timestamps = [
            candle.timestamp for candle in group
        ]

        # Ignore incomplete or incorrectly ordered groups
        if actual_timestamps != expected_timestamps:
            continue

        # 3. Calculate aggregated OHLCV
        aggregated_candle = Candle(
            timestamp=bucket_start,
            open=group[0].open,
            high=max(c.high for c in group),
            low=min(c.low for c in group),
            close=group[-1].close,
            volume=sum(c.volume for c in group),
            open_interest=group[-1].open_interest
        )

        aggregated_candles.append(aggregated_candle)

    # 4. Return completed 15-minute candles
    return aggregated_candles
