from app.schemas.market import Candle

raw_candle = ["2025-09-24T10:55:00", 245.54, 245.72, 245.52, 245.60, 122217, None]

candle = Candle.convert_to_candle(raw_candle)

print(candle)
print(candle.close)
