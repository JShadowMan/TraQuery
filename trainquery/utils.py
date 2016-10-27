''' utils.py:

'''
import aiohttp

async def fetch(loop, *args, **kwargs):
    try:
        async with aiohttp.ClientSession(loop = loop, connector = aiohttp.TCPConnector(verify_ssl = False)) as client:
            async with client.get(*args, **kwargs) as response:
                if response.status is 200:
                    return await response.text()
                else:
                    raise Exception('request error', response.status)
    except Exception as e:
        print('utils.fetch error', e)
