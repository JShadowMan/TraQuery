# -*- coding: utf-8 -*-
'''

'''

import asyncio
from collections import namedtuple

TrainProfile = namedtuple('TrainProfile', 'code id')
Station = namedtuple('Station', 'name code pos')
TrainStation = namedtuple('TrainStation', 'start end')
TrainTime = namedtuple('TrainTime', 'start arrive total')


class QueryResult(object):

    def __init__(self, trains, stacks, *, loop = asyncio.get_event_loop()):
        self.__trainsInfo = { 'trainCount': None, 'trains': {} }

        stacks = stacks['data']['datas']
        for train in trains.get('data', {}):
            self.__trainsInfo['trains'][ self.__trainCode(train)  ] = self.__trainInfo(train, stacks)


    def __trainCode(self, train):
        return train.get('queryLeftNewDTO', {}).get('station_train_code', None)

    def __trainInfo(self, train, stacks):
        information = {}

        information['stations'] = {}
        information['activate'] =  True if len(train['buttonTextInfo']) == 2 else False
        if 'queryLeftNewDTO' in train:
            train = train['queryLeftNewDTO']

        # Train main information, code, name
        information['train'] = TrainProfile(
            # code id
            train['station_train_code'], train['train_no']
        )
        # Station Information
        information['station'] = TrainStation(
            # from to
            Station(train['from_station_name'], train['from_station_telecode'], train['from_station_no']),
            Station(train['end_station_name'], train['to_station_telecode'], train['to_station_no'])
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
        information['stack'] = self.__getStackInformation(stacks, train['train_no'])

        print(information)
        return information

    def __getStackInformation(self, stacks, trainId):
        stack = None
        for trainCode in stacks:
            if trainCode['train_no'] == trainId:
                stack = trainCode
                break
        return {
            '\u5546\u52a1': self.__stackGet(stack, 'swz_num'),  # 商务
            '\u4e00\u7b49\u5ea7': self.__stackGet(stack, 'zy_num'),  # 一等座
            '\u4e8c\u7b49\u5ea7': self.__stackGet(stack, 'ze_num'),  # 二等座
            '\u65e0\u5ea7': self.__stackGet(stack, 'wz_num'),  # 无座
            '\u786c\u5ea7': self.__stackGet(stack, 'yz_num'),  # 硬座
            '\u8f6f\u5ea7': self.__stackGet(stack, 'rz_num'),  # 软座
            '\u786c\u5367': self.__stackGet(stack, 'yw_num'),  # 硬卧
            '\u8f6f\u5367': self.__stackGet(stack, 'rw_num'),  # 软卧
            '\u9ad8\u7ea7\u8f6f\u5367': self.__stackGet(stack, 'gr_num')  # 高级软卧
        }

    def __stackGet(self, dic, key):
        if key in dic:
            if dic[key] == '--' or dic[key] == '\u65e0':
                return None
            return dic[key]
        else:
            return None

    def __trainCodes(self, trains):
        codes = []
        for train in trains.get('data', {}):
            codes.append(train['queryLeftNewDTO']['station_train_code'])
        return codes
