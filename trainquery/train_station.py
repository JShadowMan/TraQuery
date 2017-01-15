# -*- coding: utf-8 -*-
#!/us/bin/env python3
#
# Copyright (C) 2016-2017 ShadowMan
#
import os
import re
import pickle
import asyncio
import logging
from trainquery import utils

class TrainStation(dict):

    __get_station_version_url = 'https://kyfw.12306.cn/otn/index/init'
    __station_list_url = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js'
    
    def __init__(self, *, loop):
        self.__async_loop = asyncio.get_event_loop()
        self.__station_list = None
        self.__station_version = None

        asyncio.set_event_loop(self.__async_loop)
        self.__async_loop.run_until_complete(self.__get_station_version())
        logging.debug('train_station.__init__ fetch new station_version={}'.format(self.__station_version))

        if os.path.isfile('station_{}.pkl'.format(self.__station_version)):
            logging.debug('train_station.__init__ cache file exists, load cache file')
            super(TrainStation, self).__init__(self.__load_stations())
        else:
            logging.debug('train_station.__init__ cache file non-exists, get new station list')
            self.__async_loop.run_until_complete(self.__init_train_station_list())
            super(TrainStation, self).__init__(self.__station_list)
            self.__dump_station_list(self.__station_list)

        asyncio.set_event_loop(loop)

    async def __init_train_station_list(self):
        response = await self.__get_station_list()
        self.__station_list = self.__parse_response(response)

    async def __get_station_list(self):
        try:
            payload = {
                'station_version': self.__station_version
            }
            return await utils.fetch(loop = self.__async_loop, url = self.__station_list_url, params = payload)
        except Exception as e:
            logging.error('train_station.__get_station_list error {}'.format(e.args[0]))

    async def __get_station_version(self):
        try:
            response = await utils.fetch(loop = self.__async_loop, url = self.__get_station_version_url)
            self.__station_version = re.search(r'station_version=([\d\.]+)', response).groups()[0]
        except Exception as e:
            logging.error('train_station.__get_station_version error {}'.format(e.args[0]))

    def __parse_response(self, response):
        temp = re.findall('([^@a-z|,;\'(\d+)_= ]+)', re.sub('\s*', '', response))

        if (len(temp) % 2) != 0:
            raise Exception('from server getting data error')

        return dict(zip(
            [ temp[i] for i in range(0, len(temp), 2) ],
            [ temp[i + 1] for i in range(0, len(temp), 2) ]
        ))

    def __load_stations(self):
        with open('station_{}.pkl'.format(self.__station_version), 'rb') as fd:
            try:
                return pickle.load(fd)
            except EOFError:
                return self.__init_train_station_list()

    def __dump_station_list(self, data):
        with open('station_{}.pkl'.format(self.__station_version), 'wb') as fd:
            pickle.dump(data, fd, pickle.HIGHEST_PROTOCOL)

__single_instance = None

def init(async_loop):
    global __single_instance
    if __single_instance is None:
        __single_instance = TrainStation(loop = async_loop)

def get(station):
    global __single_instance
    if __single_instance is None:
        raise Exception('muse be run init first')
    return __single_instance.get(station)
