#!/usr/bin/env python3
#
# Copyright (C) 2016-2017 ShadowMan
#
import json
import aiohttp
import asyncio
import logging
from urllib.parse import urljoin
from collections import OrderedDict
from trainquery import config, exceptions

_async_loop = None
_async_client_session = None

def async_startup(async_loop, *task):
    if len(task) == 1 and isinstance(task[0], list):
        logging.warning('task is a single list')
        task = task[0]
    results = async_loop.run_until_complete(asyncio.gather(*task))
    # while asyncio.Task.all_tasks():  # pending
    #     async_loop.run_until_complete(asyncio.gather(*asyncio.Task.all_tasks()))
    async_loop.run_until_complete(clean())
    return results

def async_foreach(foreach_handle, *task, args = None, async_loop = None):
    if not callable(foreach_handle) and not asyncio.iscoroutinefunction(foreach_handle):
        raise TypeError('foreach_handle is not callable')
    if not isinstance(args, (tuple, list)):
        raise TypeError('args must be tuple or list')
    if async_loop is None:
        async_loop = asyncio.get_event_loop()
    results = async_startup(async_loop, *task)
    if asyncio.iscoroutinefunction(foreach_handle):
        async_startup(async_loop, foreach_handle(results, *args))
    elif callable(foreach_handle):
        foreach_handle(results, *args)

async def fetch(loop, *args, **kwargs):
    global _async_loop, _async_client_session
    if loop != _async_loop:
        _async_loop = loop
        if _async_client_session is not None:
            logging.debug('utils.fetch close useless session_client')
            await _async_client_session.close()
        logging.debug('utils.fetch start new session_client')
        _async_client_session = aiohttp.ClientSession(loop = _async_loop, connector = aiohttp.TCPConnector(verify_ssl = False))
    try:
        async with _async_client_session.get(*args, **kwargs) as response:
            if response.status is 200:
                return await response.text()
            else:
                if (response.status == 403):
                    raise exceptions.NetworkForbidden('request error response.status = {}'.format(response.status))
                raise Exception('request error response.status = {}'.format(response.status))
    except Exception as e:
        logging.error('utils.fetch error occurs: {}'.format(e.args[0]))
        raise

async def clean():
    await _async_client_session.close()

# async def fetch(loop, *args, **kwargs):
#     try:
#         async with aiohttp.ClientSession(loop = loop, connector = aiohttp.TCPConnector(verify_ssl = False)) as client_session:
#             async with client_session.get(*args, **kwargs) as response:
#                 if response.status is 200:
#                     return await response.text()
#                 else:
#                     raise Exception('request error', response.status)
#     except Exception as e:
#         logging.error('utils.fetch error occurs: {}'.format(e.args[0]))

async def fetch_json(loop, *args, **kwargs):
    try:
        response = await fetch(loop, *args, **kwargs)
        return json.loads(response)
    except exceptions.NetworkForbidden:
        await asyncio.sleep(1)
        logging.error('utils.fetch_json error occurs: 403 Forbidden')
        return await fetch_json(loop, *args, **kwargs)
    except json.decoder.JSONDecodeError as e:
        if 'BOM' in e.args[0]: # F**K
            response = await fetch(loop, *args, **kwargs)
            return json.loads(response, encoding = 'utf-8-sig')
        else:
            raise
    except Exception:
        raise

async def get_train_information(loop, from_station, to_station, date, passenger_type):
    payload = OrderedDict([
        ('leftTicketDTO.train_date', date),
        ('leftTicketDTO.from_station', from_station),
        ('leftTicketDTO.to_station', to_station),
        ('purpose_codes', passenger_type)
    ])  # -v- Order Params
    response = await fetch_json(loop, url = config.QUERY_TRAIN_URL, params = payload)


    if 'status' in response and response['status'] is False:
        if 'c_url' in response:
            try:
                new_query_url = urljoin(config.QUERY_BASE_URL, response['c_url'])
                return await fetch_json(loop, url = new_query_url, params = payload)
            except Exception as e:
                logging.error('utils.get_train_information error occurs {}'.format(e.args[0]))
                raise
        else:
            raise RuntimeError('utils.get_train_information error occurs: unknown error')
    else:
        return response

async def get_stack_information(loop, from_station, to_station, date, passenger_type, train_id):
    payload = OrderedDict([
        ('purpose_codes', passenger_type),
        ('queryDate', date),
        ('from_station', from_station),
        ('to_station', to_station)
    ])
    response = {}
    try:
        response = await fetch_json(loop, url = config.QUERY_STACK_URL, params = payload)
        if 'status' in response and response['status'] is False:
            if 'c_url' in response:
                try:
                    new_query_url = config.QUERY_BASE_URL + response['c_url']
                    response = await fetch_json(loop, url=new_query_url, params=payload)
                except Exception as e:
                    logging.error('utils.get_train_information error occurs {}'.format(e.args[0]))
                    raise RuntimeError('utils.get_train_information error occurs')
    except exceptions.NetworkForbidden:
        response = await get_train_information(loop, from_station, to_station, date, passenger_type)

        for train in response.get('data', {}):
            if response[train].get('queryLeftNewDTO', {}).get('train_no') == train_id:
                response = response[train].get('queryLeftNewDTO', {})
                return response
    try:
        response = response['data']['datas']
    except KeyError:
        print('TrainSelector::__parseStackInformation error')
    return response

async def get_price_information(loop, train_id, start_station, end_station, seat_type, date):
    payload = OrderedDict([
        ('train_no', train_id),
        ('from_station_no', start_station.pos),
        ('to_station_no', end_station.pos),
        ('seat_types', seat_type),
        ('train_date', date)
    ])
    return await fetch_json(loop, url = config.QUERY_PRICE_URL, params = payload)

def from_dict_get(dic, key):
    if key in dic:
        if dic[key] == '--':
            return None
        if dic[key] == '\u65e0':
            return 0
        return dic[key]
    else:
        return None
