# -*- coding: utf-8 -*-
#!/usr/bin/env python3
#
# Copyright (C) 2016 ShadowMan
#
import asyncio
from collections import namedtuple
from trainquery import train_selector, utils, config

TrainProfile = namedtuple('TrainProfile', 'code id')
Station = namedtuple('Station', 'name code pos')
TrainStation = namedtuple('TrainStation', 'start end')
TrainTime = namedtuple('TrainTime', 'start arrive total')
InvalidTrain = namedtuple('InvalidTrain', 'code endpoint')

class ResultParser(object):

    def __init__(self, trains, stacks, date, passenger_type, *, loop = None):
        self.__date = date
        self.__trains_info = {'train_count': None, 'trains': {}}
        self.__invalid_trains_info = {}
        self.__passenger_type = passenger_type

        stacks = stacks['data']['datas']
        for train in trains.get('data', {}):
            train_info = self.__package_train_info(train, stacks)
            if isinstance(train_info, dict):
                self.__trains_info['trains'][ self.__pick_train_code(train) ] = train_info
            else:
                self.__invalid_trains_info[ self.__pick_train_code(train) ] = train_info
        self.__trains_info['train_count'] = len(self.__trains_info['trains'])

        if loop == None:
            loop = asyncio.get_event_loop()
        self.__async_loop = loop

    def select(self, train_code):
        if train_code in self.__trains_info['trains']:
            return train_selector.TrainSelector(self.__trains_info['trains'][train_code], loop = self.__async_loop)
        else:
            raise RuntimeError('train code not found in train list')

    def get_trains_code(self):
        return self.__trains_info.get('trains', {}).keys()

    def __pick_train_code(self, train):
        return train.get('queryLeftNewDTO', {}).get('station_train_code')

    def __package_invalid_train_info(self, train):
        if 'queryLeftNewDTO' in train:
            train = train['queryLeftNewDTO']
        return InvalidTrain(
            # code
            train['station_train_code'],
            # endpoint
            TrainStation(
                # start
                Station(train['from_station_name'], train['from_station_telecode'], train['from_station_no']),
                # end
                Station(train['to_station_name'], train['to_station_telecode'], train['to_station_no'])
            )
        )

    def __package_train_info(self, train, stacks):
        information = {}

        if train.get('queryLeftNewDTO').get('canWebBuy') == config.IN_TIME_NOT_BUY:
            return self.__package_invalid_train_info(train)

        information['activate'] = True if len(train['buttonTextInfo']) == 2 else False
        if 'queryLeftNewDTO' in train:
            train = train['queryLeftNewDTO']

        # Train main information, code, name
        information['train'] = TrainProfile(
            # code id
            train['station_train_code'], train['train_no']
        )
        # Station Information
        information['station'] = TrainStation(
            # start end
            Station(train['from_station_name'], train['from_station_telecode'], train['from_station_no']),
            Station(train['to_station_name'], train['to_station_telecode'], train['to_station_no'])
        )
        # Purchase Flag
        information['purchase'] = True if train['canWebBuy'] == 'Y' else False
        # Elapsed Time
        information['time'] = TrainTime(
            # start arrive total
            train['start_time'], train['arrive_time'], train['lishi']
        )
        # Seat Type
        information['seatType'] = train['seat_types'],
        # Price Information
        information['price'] = None
        # Seat Stack Information
        information['stack'] = self.__pick_stack_information(stacks, train['train_no'])
        # all stations
        information['stations'] = None
        # date, passengerType
        information['other'] = (self.__date, self.__passenger_type)

        return information

    def __pick_stack_information(self, stacks, train_id):
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
