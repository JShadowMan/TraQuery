''' train query

'''

import re
import time
import json
import asyncio
from collections import OrderedDict
from trainquery import train_station
from trainquery import train_query_result
from trainquery import utils

class StationError(Exception):
    pass

class Query(object):
    __queryTrainUrl = 'https://kyfw.12306.cn/otn/leftTicket/queryC'
    __queryStackUrl = 'https://kyfw.12306.cn/otn/lcxxcx/query'

    def __init__(self, *, loop = asyncio.get_event_loop()):
        self.__loop = loop
        self.__loop.set_debug(True)

        train_station.init(self.__loop)

    async def query(self, fromStation, toStation, date, isStudent = False):
        if not isinstance(date, (int, float)):
            raise TypeError('date must be unix stamp, not %s' % type(date).__name__)

        if not isinstance(fromStation, str) or not isinstance(toStation, str):
            raise TypeError('station must be str, not', type(date))

        if len(fromStation) is 3 and len(toStation) is 3:
            if fromStation.isalpha() and toStation.isalpha():
                toStation = toStation.upper()
                fromStation = fromStation.upper()
        else:
            toStation = train_station.get(toStation)
            fromStation = train_station.get(fromStation)

            if not fromStation or not toStation:
                raise StationError('station name invalid, or not found')

        date = time.localtime(date)
        date = time.strftime('%Y-%m-%d', date)

        passengerType = 'ADULT'
        if isStudent is True:
            passengerType = '0X00'

        return await self.__query(fromStation, toStation, date, passengerType)

    async def __query(self, fromStation, toStation, date, passengerType):
        payload = OrderedDict([
            ('leftTicketDTO.train_date', date),
            ('leftTicketDTO.from_station', fromStation),
            ('leftTicketDTO.to_station', toStation),
            ('purpose_codes', passengerType)
        ]) # **** 1*3*6
        trainInformation = await utils.fetch(self.__loop, url = self.__queryTrainUrl, params = payload)

        payload = OrderedDict([
            ('purpose_codes', passengerType),
            ('queryDate', date),
            ('from_station', fromStation),
            ('to_station', toStation)
        ])
        stackInformation = await utils.fetch(self.__loop, url = self.__queryStackUrl, params = payload)

        return train_query_result.QueryResult(json.loads(trainInformation),
                                              json.loads(stackInformation), loop = self.__loop)

