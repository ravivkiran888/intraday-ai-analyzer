from app.analysis.ema import calculate_ema

prices = [100, 102, 104, 106, 108]

result = calculate_ema(prices, 3)

print("EMA Result:", result)