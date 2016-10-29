# -*- coding: utf-8 -*-
'''

'''

import asyncio
from collections import namedtuple
from trainquery import train_selector
from trainquery import utils

TrainProfile = namedtuple('TrainProfile', 'code id')
Station = namedtuple('Station', 'name code pos')
TrainStation = namedtuple('TrainStation', 'start end')
TrainTime = namedtuple('TrainTime', 'start arrive total')

class QueryResult(object):

    def __init__(self, trains, stacks, date, passengerType, *, loop = asyncio.get_event_loop()):
        self.__trainsInfo = { 'trainCount': None, 'trains': {} }
        self.__date = date
        self.__passengerType = passengerType

        stacks = stacks['data']['datas']
        for train in trains.get('data', {}):
            self.__trainsInfo['trains'][ self.__trainCode(train) ] = self.__trainInfo(train, stacks)

        self.__trainsInfo['trainCount'] = len(self.__trainsInfo['trains'])

        self.__loop = loop

    def select(self, trainCode):
        if trainCode in self.__trainsInfo['trains']:
            return train_selector.TrainSelector(self.__trainsInfo['trains'][trainCode], loop = self.__loop)
        else:
            raise TypeError('train code not found in train list')

    def getTrainsCode(self):
        return self.__trainsInfo.get('trains').keys()

    def __trainCode(self, train):
        return train.get('queryLeftNewDTO', {}).get('station_train_code', None)

    def __trainInfo(self, train, stacks):
        information = {}

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
            # from end
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
        information['stack'] = self.__getStackInformation(stacks, train['train_no'])
        # all stations
        information['stations'] = None
        # date, passengerType
        information['other'] = (self.__date, self.__passengerType)

        return information

    def __getStackInformation(self, stacks, trainId):
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

    def __trainCodes(self, trains):
        codes = []
        for train in trains.get('data', {}):
            codes.append(train['queryLeftNewDTO']['station_train_code'])
        return codes

