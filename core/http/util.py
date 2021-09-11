import aiohttp

async def async_post(url, headers = {}, data = {}) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as response:
            return await response.text()


async def async_post_url_form(url, headers = {}, data = {}) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=data) as response:
            return await response.text()

async def async_get(url, headers = {})->str:
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            return await response.text()


async def async_put(url, headers = {}, data = {})->str:
    async with aiohttp.ClientSession() as session:
        async with session.put(url, headers=headers, json=data) as response:
            return await response.text()
