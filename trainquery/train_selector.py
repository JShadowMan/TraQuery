'''

'''

import copy
import json
import asyncio
from collections import namedtuple, OrderedDict
from trainquery import utils
from trainquery import train_query_result, train_station

Seat = namedtuple('Seat', 'name stack price')

class PriceException(Exception):
    pass

class TrainSelector(object):
    __queryStackUrl = 'https://kyfw.12306.cn/otn/lcxxcx/query'
    __queryTrainPrice = 'https://kyfw.12306.cn/otn/leftTicket/queryTicketPrice'
    __queryAllStations = 'https://kyfw.12306.cn/otn/czxx/queryByTrainNo'

    def __init__(self, trainInformation, *, loop = asyncio.get_event_loop()):
        self.__loop = loop

        try:
            self.__profile = trainInformation['train']
            self.__purchase = trainInformation['purchase']
            self.__station = trainInformation['station']
            self.__seatType = trainInformation['seatType']
            self.__time = trainInformation['time']
            self.__stack = trainInformation['stack']
            self.__allStations = []
            self.__price = {}
            self.__date = trainInformation['other'][0]
            self.__passenger = trainInformation['other'][1]
        except KeyError:
            raise TypeError('train information format error')

    async def seat(self, *, name = None, handle = None, all = False, filter = True):
        if not self.__price:
            self.__price = await self.__initPrice()

        if all is True:
            results = []
            for name in self.__stack:
                results.append(Seat(name, self.__stack[name], self.__price[name]))
            return results

        if name is not None and name in self.__stack and name in self.__price:
            if handle is None:
                return Seat(name, self.__stack[name], self.__price[name])
            elif callable(handle):
                handle(Seat(name, self.__stack[name], self.__price[name]))
        else:
            if handle is None:
                return Seat(None, None, None)
            elif callable(handle):
                handle(Seat(None, None, None))

    async def check(self):
        if self.purchase is True:
            return train_query_result.TrainStation(self.start, self.end)

        if int(self.end.pos) - 1 == int(self.start.pos):
            return train_query_result.TrainStation(None, None)

        if not self.__allStations:
            try:
                response = json.loads(await self.__initAllStations())

                for station in response['data']['data']:
                    self.__allStations.append(train_query_result.Station(
                        station['station_name'], train_station.get(station['station_name']), station['station_no'])
                    )
            except KeyError:
                print('TrainSelector::check error')

        for end in self.__stationRange(self.start, self.end):
            if await self.__isPurchase(self.start.code, end.code, self.code) is True:
                stack = await self.__getStackInformation(self.start.code, end.code, self.id)
                price = self.__parsePriceResponse(
                    await utils.getPriceInformation(self.__loop, self.id, self.start, end, self.__seatType, self.__date)
                )
                result = [ Seat(name, stack[name], price[name]) for name in stack ]

                return train_query_result.TrainStation(self.start, end), result

    async def __initPrice(self):
        response = await utils.getPriceInformation(self.__loop, self.id, self.start, self.end, self.seatType, self.date)
        try:
            return self.__parsePriceResponse(response)
        except TypeError:
            print('__initPrice error')

    def __parsePriceResponse(self, response):
        try:
            contents = json.loads(response)['data']
        except KeyError:
            raise PriceException('response format error')

        contents = {
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

        for key in list(filter(lambda k: contents[k] is None, contents)):
            contents.pop(key)
        return contents

    async def __initAllStations(self):
        payload = OrderedDict([
            ('train_no', self.id),
            ('from_station_telecode', self.start.code),
            ('to_station_telecode', self.end.code),
            ('depart_date', self.date)
        ])
        return await utils.fetch(self.__loop, url = self.__queryAllStations, params = payload)

    async def __isPurchase(self, fromStation, toStation, trainCode):
        response = await utils.getTrainInformation(self.__loop, fromStation, toStation, self.__date, self.__passenger)

        for train in json.loads(response)['data']:
            if train['queryLeftNewDTO']['station_train_code'] == trainCode:
                return train['queryLeftNewDTO']['canWebBuy'] == 'Y'
        else:
            raise TypeError('trainCode not found, fatal error')

    def __stationRange(self, start, end):
        available = copy.copy(self.__allStations)

        for station in self.__allStations:
            if station.code == start.code:
                break
            available.pop(0)
        available.pop(0) # pop start station

        available.reverse()
        for station in available:
            if station.code == end.code:
                break
            available.pop(0)
        available.pop(0) # pop end station

        return available

    async def __getStackInformation(self, fromStation, toStation, trainId):
        stacks = await utils.getStackInformation(self.__loop, fromStation, toStation, self.__date, self.__passenger)
        try:
            stacks = json.loads(stacks)['data']['datas']
        except KeyError:
            print('TrainSelector::__parseStackInformation error')

        stack = None
        for trainCode in stacks:
            if trainCode['train_no'] == trainId:
                stack = trainCode
                break
        contents = {
            '\u5546\u52a1': utils.dictGet(stack, 'swz_num'),  # 商务
            '\u4e00\u7b49\u5ea7': utils.dictGet(stack, 'zy_num'),  # 一等座
            '\u4e8c\u7b49\u5ea7': utils.dictGet(stack, 'ze_num'),  # 二等座
            '\u65e0\u5ea7': utils.dictGet(stack, 'wz_num'),  # 无座
            '\u786c\u5ea7': utils.dictGet(stack, 'yz_num'),  # 硬座
            '\u8f6f\u5ea7': utils.dictGet(stack, 'rz_num'),  # 软座
            '\u786c\u5367': utils.dictGet(stack, 'yw_num'),  # 硬卧
            '\u8f6f\u5367': utils.dictGet(stack, 'rw_num'),  # 软卧
            '\u9ad8\u7ea7\u8f6f\u5367': utils.dictGet(stack, 'gr_num')  # 高级软卧
        }

        for key in list(filter(lambda k: contents[k] is None, contents)):
            contents.pop(key)
        return contents

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

    @property
    def isStudent(self):
        return not self.__passenger == 'ADULT'
