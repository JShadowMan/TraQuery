''' example

'''
import time
import random
import asyncio
import logging
import cProfile
from trainquery import train_query, utils, train_selector, train_query_result, exceptions

logging.basicConfig(level = logging.INFO)

async def foreach_train(result):
    if isinstance(result, train_query_result.ResultParser):
        for train_code in result.get_trains_code():
            selector = result.select(train_code)

            print(selector.train_code, selector.start_time, selector.arrive_time, selector.total_time, selector.start_station, selector.end_station)
            try:
                print('\t', selector.train_code, await selector.seat())
            except exceptions.ReTryExceed as e:
                logging.info('query seat retry count exceeded. ignore this train[{}]'.format(selector.train_code))
            # print('\t\t', selector.train_code, await selector.check())

loop = asyncio.get_event_loop()
loop.set_debug(True)

query = train_query.TrainQuery()

task = [
    asyncio.ensure_future(query.query('北京', '南京', int(time.time()) + 3600 * 24, result_handler= foreach_train), loop = loop),
    # asyncio.ensure_future(query.query('北京', '南京', int(time.time()) + 3600 * 24, result_handle = foreach_results), loop = loop),
    # asyncio.ensure_future(query.query('北京', '南京', int(time.time()) + 3600 * 24, result_handle = foreach_results), loop = loop)
]

# results = loop.run_until_complete(asyncio.gather(*task))
#
# loop.run_until_complete(foreach_results(results, loop))
# loop.run_until_complete(utils.clean())

utils.async_startup(loop, *task)
# utils.async_foreach(foreach_results, *task, args = (loop,))
