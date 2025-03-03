import aiohttp
import asyncio


async def fetch_data():
    params = {
        "timeframe": "all",
        "sortBy": "time",
        "order": "desc",
        "perPage": 10,
        "from": 0,
        "page": 1,
        "unit": "c86a0832a19bdf2485ae43502e5c9e054d86dd5896abe8bea1918cd743617264616e6f2042757920426f74"
    }

    headers = {
        "x-api-key": "YOUR_API_KEY"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get("https://openapi.taptools.io/api/v1/token/trades", headers=headers, params=params) as response:
            print(await response.text())


asyncio.run(fetch_data())
