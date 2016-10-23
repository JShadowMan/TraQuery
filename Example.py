''' example

'''
import time
import asyncio
from trainquery import train_station
from trainquery import train_query

loop = asyncio.get_event_loop()

loop.run_until_complete(train_query.Query().query('北京', '南京', int(time.time()) + 3600 * 24))
