''' utils.py:

'''
import asyncio
import aiohttp
import async_timeout

GLOBAL_HTTP_TIMEOUT = 5

async def fetch(loop, *args, **kwargs):
    try:
        with async_timeout.timeout(GLOBAL_HTTP_TIMEOUT):
            async with aiohttp.ClientSession(loop = loop, connector = aiohttp.TCPConnector(verify_ssl = False)) as client:
                async with client.get(*args, **kwargs) as response:
                    if response.status is 200:
                        return await response.text()
                    else:
                        raise Exception('request error', response.status)
    except asyncio.TimeoutError as e:
        print(e)
