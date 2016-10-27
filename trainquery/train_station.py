# -*- coding: utf-8 -*-
''' train station list

'''
import os, re
import pickle
import asyncio
from trainquery import utils

class TrainStation(dict):

    __getStationVersionAddress = 'https://kyfw.12306.cn/otn/index/init'
    __stationListAddress = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js'
    
    def __init__(self, *, loop):
        self.__loop = asyncio.get_event_loop()
        self.__stationList = None
        self.__stationVersion = None

        asyncio.set_event_loop(self.__loop)

        self.__loop.run_until_complete(self.__getStationVersion())

        if os.path.isfile('station_{}.pkl'.format(self.__stationVersion)):
            super(TrainStation, self).__init__(self.__loadStations())
        else:
            self.__loop.run_until_complete(self.__initTrainStationList())

            super(TrainStation, self).__init__(self.__stationList)
            self.__dumpStation(self.__stationList)

        asyncio.set_event_loop(loop)

    async def __initTrainStationList(self):
        response = await self.__getStationList()

        self.__stationList = self.__parseResponse(response)

    async def __getStationList(self):
        try:
            payload = { 'station_version': self.__stationVersion }
            return await utils.fetch(loop = self.__loop, url = self.__stationListAddress, params = payload)
        except Exception as e:
            print('__getStationList error')

    async def __getStationVersion(self):
        try:
            response = await utils.fetch(loop = self.__loop, url = self.__getStationVersionAddress)
            self.__stationVersion = re.search(r'station_version=([\d\.]+)', response).groups()[0]
        except Exception as e:
            print('__getStationVersion error')

    def __parseResponse(self, response):
        temp = re.findall('([^@a-z|,;\'(\d+)_= ]+)', response.replace('  ', ''))

        if (len(temp) % 2) != 0:
            raise Exception
        stationList = {}

        index = 0
        while index < len(temp):
            stationList[temp[index]] = temp[index + 1]
            index += 2

        return stationList

    def __loadStations(self):
        with open('station_{}.pkl'.format(self.__stationVersion), 'rb') as fd:
            try:
                return pickle.load(fd)
            except EOFError:
                return self.__initTrainStationList()

    def __dumpStation(self, data):
        with open('station_{}.pkl'.format(self.__stationVersion), 'wb') as fd:
            pickle.dump(data, fd, pickle.HIGHEST_PROTOCOL)

__singleInstance = None

def init(loop):
    global __singleInstance
    __singleInstance = TrainStation(loop = loop)

def get(station):
    global __singleInstance
    if __singleInstance is None:
        raise Exception('muse be run init first')
    return __singleInstance.get(station, None)

