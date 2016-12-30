''' train query

'''

import time
import json
import asyncio
import logging
from trainquery import train_station, train_query_result, config, utils, exceptions

class TrainQuery(object):
    __query_train_url = 'https://kyfw.12306.cn/otn/leftTicket/queryX'
    __queryStackUrl = 'https://kyfw.12306.cn/otn/lcxxcx/query'

    def __init__(self, *, loop = None):
        if loop == None:
            loop = asyncio.get_event_loop()
        self.__async_loop = loop

        train_station.init(self.__async_loop)

    async def query(self, from_station, to_station, date, is_student = False, *, result_handler = None):
        if not isinstance(date, (int, float)):
            raise TypeError('date must be unix time stamp, not %s' % type(date).__name__)

        if not isinstance(from_station, str) or not isinstance(to_station, str):
            raise TypeError('station must be str, not', type(date))

        if len(from_station) is 3 and len(to_station) is 3 and \
                from_station.isalpha() and to_station.isalpha():
            to_station = to_station.upper()
            from_station = from_station.upper()
        else:
            to_station = train_station.get(to_station)
            from_station = train_station.get(from_station)

            if not from_station or not to_station:
                raise exceptions.StationError('station name invalid')

        if not isinstance(date, (int, float)):
            raise TypeError('data must be unix timestamp')
        date = time.localtime(date)
        date = time.strftime('%Y-%m-%d', date)

        passenger_type = config.PASSENGER_ADULT
        if is_student is True:
            passenger_type = config.PASSENGER_STUDENT

        if result_handler is None:
            return await self.__query_train(from_station, to_station, date, passenger_type)
        elif asyncio.iscoroutinefunction(result_handler):
            await result_handler(await self.__query_train(from_station, to_station, date, passenger_type))
        elif callable(result_handler):
            result_handler(await self.__query_train(from_station, to_station, date, passenger_type))
        else:
            raise TypeError('result_handler must be callable')

    async def __query_train(self, from_station, to_station, date, passenger_type):
        train_information = None
        while train_information is None:
            train_information = await utils.get_train_information(self.__async_loop,
                                                                  from_station, to_station,
                                                                  date, passenger_type)
        try:
            return train_query_result.ResultParser(train_information, date, passenger_type)
        except Exception as e:
            logging.error('TrainQuery.__query_train error occurs {}'.format(e.args[0]))
            raise
