''' example

'''
import time
import asyncio
import cProfile
from trainquery import train_query

loop = asyncio.get_event_loop()

# loop.set_debug(True)
query = train_query.Query()
task = [
    asyncio.ensure_future(query.query('北京', '南京', int(time.time()) + 3600 * 24), loop = loop),
    asyncio.ensure_future(query.query('北京', '南京', int(time.time()) + 3600 * 24), loop = loop),
    asyncio.ensure_future(query.query('北京', '南京', int(time.time()) + 3600 * 24), loop = loop),
    asyncio.ensure_future(query.query('北京', '南京', int(time.time()) + 3600 * 24), loop = loop),
    asyncio.ensure_future(query.query('北京', '南京', int(time.time()) + 3600 * 24), loop = loop),
    asyncio.ensure_future(query.query('北京', '南京', int(time.time()) + 3600 * 24), loop = loop),
    asyncio.ensure_future(query.query('北京', '南京', int(time.time()) + 3600 * 24), loop = loop),
    asyncio.ensure_future(query.query('北京', '南京', int(time.time()) + 3600 * 24), loop = loop),
    asyncio.ensure_future(query.query('北京', '南京', int(time.time()) + 3600 * 24), loop = loop),
    asyncio.ensure_future(query.query('北京', '南京', int(time.time()) + 3600 * 24), loop = loop),
    asyncio.ensure_future(query.query('北京', '南京', int(time.time()) + 3600 * 24), loop = loop),
    asyncio.ensure_future(query.query('北京', '南京', int(time.time()) + 3600 * 24), loop = loop)
]

loop.run_until_complete(asyncio.gather(*task))
