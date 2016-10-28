'''

'''

import json
import asyncio
from collections import namedtuple, OrderedDict
from trainquery import utils

Seat = namedtuple('Seat', 'stack price')

class PriceException(Exception):
    pass

class TrainSelector(object):

    __queryTrainPrice = 'https://kyfw.12306.cn/otn/leftTicket/queryTicketPrice'
    __queryTrainStations = 'https://kyfw.12306.cn/otn/czxx/queryByTrainNo?train_no=%s&from_station_telecode=%s&to_station_telecode=%s&depart_date=%s'

    def __init__(self, trainInformation, date, *, loop = asyncio.get_event_loop()):
        self.__loop = loop

        try:
            self.__profile = trainInformation['train']
            self.__purchase = trainInformation['purchase']
            self.__station = trainInformation['station']
            self.__seatType = trainInformation['seatType']
            self.__time = trainInformation['time']
            self.__stack = trainInformation['stack']
            self.__allStations = {}
            self.__price = {}
            self.__date = date
        except KeyError:
            raise TypeError('train information format error')

    async def seat(self, name, handle = None):
        if not self.__price:
            self.__price = await self.__initPrice()

        if name in self.__stack and name in self.__price:
            if handle is None:
                return Seat(self.__stack[name], self.__price[name])
            elif callable(handle):
                handle(Seat(self.__stack[name], self.__price[name]))
        else:
            if handle is None:
                return Seat(None, None)
            elif callable(handle):
                handle(Seat(None, None))

    async def __initPrice(self):
        payload = OrderedDict([
            ('train_no', self.id),
            ('from_station_no', self.start.pos),
            ('to_station_no', self.end.pos),
            ('seat_types', self.seatType[0]),
            ('train_date', self.date)
        ])
        response = await utils.fetch(self.__loop, url = self.__queryTrainPrice, params = payload)
        try:
            return self.__parsePriceResponse(json.loads(response))
        except TypeError:
            print('__initPrice error')

    def __parsePriceResponse(self, response):
        try:
            contents = response['data']
        except KeyError:
            raise PriceException('response format error')

        return {
            '\u5546\u52a1': utils.dictGet(contents, 'A9'), # 商务
            '\u4e00\u7b49\u5ea7': utils.dictGet(contents, 'M'), # 一等座
            '\u4e8c\u7b49\u5ea7': utils.dictGet(contents, 'O'), # 二等座
            '\u65e0\u5ea7': utils.dictGet(contents, 'WZ'), # 无座
            '\u786c\u5ea7': utils.dictGet(contents, 'A1'), # 硬座
            '\u8f6f\u5ea7': utils.dictGet(contents, 'A2'), # 软座
            '\u786c\u5367': utils.dictGet(contents, 'A3'), # 硬卧
            '\u8f6f\u5367': utils.dictGet(contents, 'A4'), # 软卧
            '\u9ad8\u7ea7\u8f6f\u5367': utils.dictGet(contents, 'A6') # 高级软卧
        }

    @property
    def code(self):
        return self.__profile.code

    @property
    def id(self):
        return self.__profile.id

    @property
    def purchase(self):
        return self.__purchase

    @property
    def start(self):
        return self.__station.start

    @property
    def end(self):
        return self.__station.end

    @property
    def seatType(self):
        return self.__seatType

    @property
    def startTime(self):
        return self.__time.start

    @property
    def arriveTime(self):
        return self.__time.arrive

    @property
    def totalTime(self):
        return self.__time.total

    @property
    def allStations(self):
        return self.__allStations

    @property
    def date(self):
        return self.__date

