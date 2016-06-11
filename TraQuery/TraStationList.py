# -*- coding: UTF-8 -*-
'''
Created on 06/10/2016

@author: ShadowMan
@license: MIT License
@version: 1.0.0
'''

import urllib2, re

# Check SSL
try:
    import ssl
except ImportError:
    _have_ssl = False
else:
    _have_ssl = True

_base_url = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version='

# Getting Train Station List From 12306
class TraStationList(object):

    def __init__(self, stationVersion = '1.8954'):
        self.__stationList = {}
        self.__initTraStationList(stationVersion)

    def __initTraStationList(self, stationVersion):
        try:
            handler = urllib2.urlopen(_base_url + stationVersion)
        except urllib2.URLError:
            if _have_ssl == True:
                context = ssl._create_unverified_context()
                handler = urllib2.urlopen(_base_url + stationVersion,  context = context)
            else:
                raise Exception('Require SSL Module')

        if handler.getcode() == 200:
            stationList = handler.read()
        else:
            raise Exception("Get Request Error Occurs.")

        self.__parseStation(stationList)

    def __parseStation(self, stationList):
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
