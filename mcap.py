import aiohttp
import asyncio


async def fetch_data():
    params = {
        "unit": "a2944573e99d2ed3055b808eaa264f0bf119e01fc6b18863067c63e44d454c44"
    }

    headers = {
        "x-api-key": "YOUR_API_KEY"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get("https://openapi.taptools.io/api/v1/token/mcap", headers=headers, params=params) as response:
            print(await response.text())


asyncio.run(fetch_data())
