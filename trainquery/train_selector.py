#!/usr/bin/env python3
#
# Copyright (C) 2016 ShadowMan
#
import copy
import json
import asyncio
import logging
from collections import namedtuple, OrderedDict
from trainquery import train_query_result, train_station, utils, config

Seat = namedtuple('Seat', 'name stack price')

class PriceException(Exception):
    pass

class TrainSelector(object):

    def __init__(self, train_information, *, loop = None):
        if loop is None:
            loop = asyncio.get_event_loop()
        self.__async_loop = loop

        try:
            self.__seats_price = {}
            self.__pass_all_stations = []
            self.__train_profile = train_information['train']
            self.__purchase_flag = train_information['purchase']
            self.__endpoint_station = train_information['station']
            self.__seat_type = train_information['seatType']
            self.__time_information = train_information['time']
            self.__stack_information = train_information['stack']
            self.__start_date = train_information['other'][0]
            self.__passenger = train_information['other'][1]
        except KeyError:
            logging.error('TrainSelector constructor parameter invalid')
            raise TypeError('train information format error')

    async def seat(self, *, name = None, handle = None, all = False, filter = True):
        while not self.__seats_price:
            self.__seats_price = await self.__init__seat_price()

        if name is None or all is True:
            results = []
            try:
                for name in self.__stack_information:
                    results.append(Seat(name, self.__stack_information[name], self.__seats_price[name]))
                return results
            except KeyError:
                logging.error('seat error {} {}'.format(self.__stack_information, self.__seats_price))
                raise
        if name is not None and name in self.__stack_information and name in self.__seats_price:
            if handle is None:
                return Seat(name, self.__stack_information[name], self.__seats_price[name])
            elif callable(handle):
                if asyncio.iscoroutine(handle):
                    await handle(Seat(name, self.__stack_information[name], self.__seats_price[name]))
                else:
                    handle(Seat(name, self.__stack_information[name], self.__seats_price[name]))
            else:
                raise TypeError('seat handle invalid')
        else:
            if handle is None:
                return Seat(None, None, None)
            elif callable(handle):
                if asyncio.iscoroutine(handle):
                    await handle(Seat(name, self.__stack_information[name], self.__seats_price[name]))
                else:
                    handle(Seat(name, self.__stack_information[name], self.__seats_price[name]))

    async def check(self):
        if self.purchase_flag is True:
            return train_query_result.TrainStation(self.start_station, self.end_station)

        if not self.__pass_all_stations:
            try:
                response = await self.__init_pass_all_stations()

                for station in response['data']['data']:
                    self.__pass_all_stations.append(train_query_result.Station(
                        station['station_name'], train_station.get(station['station_name']), station['station_no'])
                    )
            except KeyError:
                logging.error('TrainSelector.check error')
                raise RuntimeError('TrainSelector.check internal error occurs')

        if len(self.__station_range(self.start_station, self.end_station)) == 0:
            # Not an appropriate solution
            return train_query_result.TrainStation(None, None)

        for end in self.__station_range(self.start_station, self.end_station):
            if await self.__check_purchase(self.start_station.code, end.code, self.train_code) is True:
                stack = await self.__pick_stack_information(self.start_station.code, end.code, self.train_id)
                price = self.__parse_seat_price(
                    await utils.get_price_information(self.__async_loop, self.train_id,
                                                      self.start_station, end,
                                                      self.__seat_type, self.__start_date)
                )

                # Queries to the right programme
                result = [ Seat(name, stack[name], price[name]) for name in stack ]
                return train_query_result.TrainStation(self.start_station, end), result
        # raise Exception('check error, not query range {}'.format(self.__station_range(self.start_station, self.end_station)))
        logging.info('not query range {}'.format(self.__station_range(self.start_station, self.end_station)))
        return train_query_result.TrainStation(None, None)

    async def __init__seat_price(self):
        response = await utils.get_price_information(self.__async_loop,self.train_id,
                                                     self.start_station, self.end_station,
                                                     self.seat_type, self.start_date)
        return self.__parse_seat_price(response)

    def __parse_seat_price(self, response):
        response = response['data']

        contents = {
            '\u5546\u52a1': utils.from_dict_get(response, 'A9'), # 商务
            '\u4e00\u7b49\u5ea7': utils.from_dict_get(response, 'M'), # 一等座
            '\u4e8c\u7b49\u5ea7': utils.from_dict_get(response, 'O'), # 二等座
            '\u65e0\u5ea7': utils.from_dict_get(response, 'WZ'), # 无座
            '\u786c\u5ea7': utils.from_dict_get(response, 'A1'), # 硬座
            '\u8f6f\u5ea7': utils.from_dict_get(response, 'A2'), # 软座
            '\u786c\u5367': utils.from_dict_get(response, 'A3'), # 硬卧
            '\u8f6f\u5367': utils.from_dict_get(response, 'A4'), # 软卧
            '\u9ad8\u7ea7\u8f6f\u5367': utils.from_dict_get(response, 'A6') # 高级软卧
        }

        for key in list(filter(lambda k: contents[k] is None, contents)):
            contents.pop(key)
        return contents

    async def __init_pass_all_stations(self):
        payload = OrderedDict([
            ('train_no', self.train_id),
            ('from_station_telecode', self.start_station.code),
            ('to_station_telecode', self.end_station.code),
            ('depart_date', self.start_date)
        ])
        return await utils.fetch_json(self.__async_loop, url = config.QUERY_ALL_STATIONS, params = payload)

    async def __check_purchase(self, from_station, to_station, train_code):
        response = None
        while response is None:
            response = await utils.get_train_information(self.__async_loop, from_station, to_station,
                                                         self.__start_date, self.__passenger)

        for train in response['data']:
            if train['queryLeftNewDTO']['station_train_code'] == train_code:
                return train['queryLeftNewDTO']['canWebBuy'] == 'Y'
        else:
            logging.error('fatal error: train_code not found {} {} {} {}'.format(response, from_station, to_station, train_code))
            raise TypeError('fatal error: train_code not found')

    # TODO. Station-wide seems to have problems
    def __station_range(self, start, end):
        available = copy.copy(self.__pass_all_stations)

        for station in self.__pass_all_stations:
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

    async def __pick_stack_information(self, from_station, to_station, train_id):
        stacks = await utils.get_stack_information(self.__async_loop, from_station, to_station, self.__start_date, self.__passenger)
        try:
            stacks = stacks['data']['datas']
        except KeyError:
            print('TrainSelector::__parseStackInformation error')

        stack = None
        for current_stack in stacks:
            if current_stack['train_no'] == train_id:
                stack = current_stack
                break
        contents = {
            '\u5546\u52a1': utils.from_dict_get(stack, 'swz_num'),  # 商务
            '\u4e00\u7b49\u5ea7': utils.from_dict_get(stack, 'zy_num'),  # 一等座
            '\u4e8c\u7b49\u5ea7': utils.from_dict_get(stack, 'ze_num'),  # 二等座
            '\u65e0\u5ea7': utils.from_dict_get(stack, 'wz_num'),  # 无座
            '\u786c\u5ea7': utils.from_dict_get(stack, 'yz_num'),  # 硬座
            '\u8f6f\u5ea7': utils.from_dict_get(stack, 'rz_num'),  # 软座
            '\u786c\u5367': utils.from_dict_get(stack, 'yw_num'),  # 硬卧
            '\u8f6f\u5367': utils.from_dict_get(stack, 'rw_num'),  # 软卧
            '\u9ad8\u7ea7\u8f6f\u5367': utils.from_dict_get(stack, 'gr_num')  # 高级软卧
        }

        for key in list(filter(lambda k: contents[k] is None, contents)):
            contents.pop(key)
        return contents

    @property
    def train_code(self):
        return self.__train_profile.code

    @property
    def train_id(self):
        return self.__train_profile.id

    @property
    def purchase_flag(self):
        return self.__purchase_flag

    @property
    def start_station(self):
        return self.__endpoint_station.start

    @property
    def end_station(self):
        return self.__endpoint_station.end

    @property
    def seat_type(self):
        return self.__seat_type

    @property
    def start_time(self):
        return self.__time_information.start

    @property
    def arrive_time(self):
        return self.__time_information.arrive

    @property
    def total_time(self):
        return self.__time_information.total

    @property
    def all_stations(self):
        return self.__pass_all_stations

    @property
    def start_date(self):
        return self.__start_date

    @property
    def is_student(self):
        return self.__passenger == config.PASSENGER_STUDENT
