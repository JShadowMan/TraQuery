# -*- coding: UTF-8 -*-
'''
Created on 2016年6月10日

@author: ShadowMan
'''
import urllib2, re
import ssl

class TraStationList(object):
    '''
    China train Station List
    '''

    def __init__(self):
        self.__stationList = {}
        self.__initTraStationList__()

    def __initTraStationList__(self):
        context = ssl._create_unverified_context()
        handler = urllib2.urlopen('https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.8954',  context = context)

        if handler.getcode() == 200:
            stationList = handler.read()
        else:
            raise Exception("Get Request Error Occurs.")

        self.__parseStation__(stationList)

    def __parseStation__(self, stationList):
        stationList = stationList.decode('utf-8')
        stationList = stationList.replace('  ', '') # f**k 12306
        stationList = re.findall('([^@a-z|,;\'(\d+)_= ]+)', stationList)

        if (len(stationList) % 2) != 0:
            raise Exception("Get Station List Error Occurs")

        index = 0
        while index < len(stationList):
            self.__stationList[stationList[index]] = stationList[index + 1]
            index = index + 2

    def get(self, station):
        if type(station) == type(''):
            station = station.decode('utf-8')
            
        if (station in self.__stationList):
            return self.__stationList[station]
