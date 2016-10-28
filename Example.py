''' example

'''
import time
import asyncio
import cProfile
from trainquery import train_query

async def resultHandler(results, loop):
    for result in results:
        selector = result.select(list(result.getTrainsCode())[0])
        print(selector.code, selector.startTime, selector.arriveTime, selector.totalTime, selector.start, selector.end)
        print(await selector.seat('二等座'))

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

results = loop.run_until_complete(asyncio.gather(*task))

loop.run_until_complete(resultHandler(results, loop))
