# -*- coding: utf-8 -*-
#!/usr/bin/env python3
#
# Copyright (C) 2016-2017 ShadowMan
#
import asyncio
from collections import namedtuple
from trainquery import train_selector, utils, config, exceptions

TrainQueryResult = namedtuple('TrainQueryResult', 'code activate profile endpoint purchase_flag \
    time seat_type price stack all_stations date passenger_type')
TrainProfile = namedtuple('TrainProfile', 'code id')
Station = namedtuple('Station', 'name code pos')
TrainStation = namedtuple('TrainStation', 'start end')
TrainTime = namedtuple('TrainTime', 'start arrive total')

class ResultParser(object):

    def __init__(self, trains, date, passenger_type, *, loop = None):
        self.__date = date
        self.__trains_info = { 'train_count': None, 'trains': {} }
        self.__invalid_trains_info = { 'train_count': None, 'trains': {} }
        self.__passenger_type = passenger_type

        for train in trains.get('data', {}):
            train_info = self.__package_train_info(train)
            if train_info.activate == True:
                self.__trains_info['trains'][train_info.code] = train_info
            else:
                self.__invalid_trains_info['trains'][train_info.code] = train_info
        self.__trains_info['train_count'] = len(self.__trains_info['trains'])
        self.__invalid_trains_info['train_count'] = len(self.__invalid_trains_info['trains'])

        if loop == None:
            loop = asyncio.get_event_loop()
        self.__async_loop = loop

    def select(self, train_code):
        if train_code in self.__trains_info['trains']:
            return train_selector.TrainSelector(self.__trains_info['trains'][train_code], loop = self.__async_loop)
        elif train_code in self.__invalid_trains_info:
            raise exceptions.InvalidTrain('train \'{}\' is invalid'.format(train_code))
        else:
            raise RuntimeError('train code not found in train list')

    def get_trains_code(self):
        return list(self.__trains_info.get('trains', {}).keys())

    def __pick_train_code(self, train):
        if 'code' in train:
            return train.code
        if 'train' in train:
            return train['train'].code

    def __package_invalid_train_info(self, train):
        if 'queryLeftNewDTO' in train:
            train = train['queryLeftNewDTO']
        try:
            return TrainQueryResult(
                # code
                train['station_train_code'],
                # activate
                False,
                # profile,
                None,
                # endpoint
                TrainStation(
                    # start
                    Station(train['from_station_name'], train['from_station_telecode'], train['from_station_no']),
                    # end
                    Station(train['to_station_name'], train['to_station_telecode'], train['to_station_no'])
                ),
                # purchase_flag
                False,
                # time
                None,
                # seat_type
                None,
                # price
                None,
                # stack
                None,
                # all_stations
                None,
                # date
                self.__date,
                # passenger_type
                self.__passenger_type
            )
        except Exception as e:
            raise RuntimeError('ResultParser.__package_invalid_train_info error, the train data invalid')

    def __package_train_info(self, train):
        information = {}

        if train.get('queryLeftNewDTO').get('canWebBuy') == config.IN_TIME_NOT_BUY:
            return self.__package_invalid_train_info(train)

        activate_flag = True if len(train['buttonTextInfo']) == 2 else False
        information['activate'] = True if len(train['buttonTextInfo']) == 2 else False
        if 'queryLeftNewDTO' in train:
            train = train['queryLeftNewDTO']

        return TrainQueryResult(
            # code
            train['station_train_code'],
            # activate
            activate_flag,
            # profile,
            TrainProfile(
                # code id(train_no)
                train['station_train_code'], train['train_no']
            ),
            # endpoint
            TrainStation(
                # start
                Station(train['from_station_name'], train['from_station_telecode'], train['from_station_no']),
                # end
                Station(train['to_station_name'], train['to_station_telecode'], train['to_station_no'])
            ),
            # purchase_flag
            True if train['canWebBuy'] == 'Y' else False,
            # time
            TrainTime(
                # start arrive total
                train['start_time'], train['arrive_time'], train['lishi']
            ),
            # seat_type
            train['seat_types'],
            # price
            None,
            # stack
            self.__pick_stack_information(train),
            # all_stations
            None,
            # date
            self.__date,
            # passenger_type
            self.__passenger_type
        )

    def __pick_stack_information(self, train):
        contents = {
            '\u5546\u52a1': utils.from_dict_get(train, 'swz_num'),  # 商务
            '\u4e00\u7b49\u5ea7': utils.from_dict_get(train, 'zy_num'),  # 一等座
            '\u4e8c\u7b49\u5ea7': utils.from_dict_get(train, 'ze_num'),  # 二等座
            '\u65e0\u5ea7': utils.from_dict_get(train, 'wz_num'),  # 无座
            '\u786c\u5ea7': utils.from_dict_get(train, 'yz_num'),  # 硬座
            '\u8f6f\u5ea7': utils.from_dict_get(train, 'rz_num'),  # 软座
            '\u786c\u5367': utils.from_dict_get(train, 'yw_num'),  # 硬卧
            '\u8f6f\u5367': utils.from_dict_get(train, 'rw_num'),  # 软卧
            '\u9ad8\u7ea7\u8f6f\u5367': utils.from_dict_get(train, 'gr_num')  # 高级软卧
        }

        for key in list(filter(lambda k: contents[k] is None, contents)):
            contents.pop(key)
        return contents
