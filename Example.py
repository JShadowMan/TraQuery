''' example

'''
import time
import random
import asyncio
import cProfile
from trainquery import train_query

async def resultHandler(results, loop):
    for result in results:
        selector = result.select(random.choice(list(result.getTrainsCode())))
        print(selector.code, selector.startTime, selector.arriveTime, selector.totalTime, selector.start, selector.end)
        print('\t', await selector.seat(all = True))
        print('\t\t', await selector.check())
        print()

loop = asyncio.get_event_loop()

loop.set_debug(True)
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
