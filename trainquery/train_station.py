# -*- coding: utf-8 -*-
''' train station list

'''
import os, re
import pickle
import requests

class TrainStation(dict):

    __getStationVersionAddress = 'https://kyfw.12306.cn/otn/index/init'
    __stationListAddress = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version={}'
    
    def __init__(self):
        if os.path.isfile('station.pkl'):
            super(TrainStation, self).__init__(self.__loadStations())
        else:
            stationList = self.__initTrainStationList()
            super(TrainStation, self).__init__(stationList)

            self.__dumpStation(stationList)

    def __initTrainStationList(self):
        response = self.__getStationList()

        return self.__parseResponse(response)

    def __getStationList(self):
        try:
            response = requests.get(self.__stationListAddress.format(self.__getStationVersion()), verify = False)

            if response.status_code is not requests.codes.OK:
                raise Exception
            return response.text

        except Exception as e:
            print(e)

    def __getStationVersion(self):
        try:
            response = requests.get(self.__getStationVersionAddress, verify = False)

            if response.status_code is not requests.codes.OK:
                raise Exception

            return re.search(r'station_version=([\d\.]+)', response.text).groups()[0]
        except Exception as e:
            print(e)

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
        with open('station.pkl', 'rb') as fd:
            try:
                return pickle.load(fd)
            except EOFError:
                return self.__initTrainStationList()

    def __dumpStation(self, data):
        with open('station.pkl', 'wb') as fd:
            pickle.dump(data, fd, pickle.HIGHEST_PROTOCOL)

if __name__ == '__main__':
    pass