''' example

'''
import time
import random
import asyncio
import logging
import cProfile
from trainquery import train_query, utils

# logging.basicConfig(level = logging.DEBUG)

async def resultHandler(results, loop):
    for result in results:
        for sel in result.get_trains_code():
            selector = result.select(sel)
            print(selector.code, selector.start_time, selector.arrive_time, selector.total_time, selector.start_station, selector.end_station)
            print('\t', await selector.seat(all = True))
            print('\t\t', await selector.check())
            print()
        break

loop = asyncio.get_event_loop()
loop.set_debug(True)

query = train_query.TrainQuery()

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

# results = loop.run_until_complete(asyncio.gather(*task))
#
# loop.run_until_complete(resultHandler(results, loop))
# loop.run_until_complete(utils.clean())
# cProfile.run('loop.run_until_complete(resultHandler(results, loop))')

utils.async_startup(loop, *task)
