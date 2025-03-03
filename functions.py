import aiohttp

from cfg import API_KEY


async def return_transactions(token_address, per_page=10, timestamp=0):
    params = {
        "timeframe": "all",
        "sortBy": "time",
        "order": "desc",
        "perPage": per_page,
        "from": timestamp,
        "page": 1,
        "unit": token_address
    }

    headers = {
        "x-api-key": API_KEY
    }

    async with aiohttp.ClientSession() as session:
        async with session.get("https://openapi.taptools.io/api/v1/token/trades", headers=headers, params=params) as response:
            return await response.json()


async def return_token_data(token_address):
    params = {
        "unit": token_address
    }

    headers = {
        "x-api-key": API_KEY
    }

    async with aiohttp.ClientSession() as session:
        async with session.get("https://openapi.taptools.io/api/v1/token/mcap", headers=headers, params=params) as response:
            return await response.json()
