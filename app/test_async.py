import asyncio

async def get_stock_price():
    print("1. Request started")

    await asyncio.sleep(3)

    print("2. Response received")


asyncio.run(get_stock_price())

print("3. Program completed")