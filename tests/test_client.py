from app.schemas.market import StockRequest

stock = StockRequest(trading_symbol="")

print(stock)
print(stock.trading_symbol)