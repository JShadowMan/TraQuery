#!/usr/bin/env python3
#
# Copyright (C) 2016-2017 ShadowMan
#
import os
import json
import time
import flask
import logging
import asyncio
import aiohttp
from collections import namedtuple
from functools import partial

from aiohttp import web
from trainquery import train_station, utils, train_query, train_query_result, exceptions

async_loop = asyncio.get_event_loop()
train_station.init(async_loop)

with open('templates/index.html') as html:
    response_text = html.read()

async def index_handler(request):
    return web.Response(text = response_text, content_type = 'text/html', charset = 'utf-8')

WS_Response_Data = namedtuple('WS_Response_Data', 'event data')

def _server_emit(ws, ws_response):
    if ws_response is None:
        raise RuntimeWarning('the event handler must be return a response')
    if isinstance(ws_response, WS_Response_Data):
        if isinstance(ws_response.data, dict):
            response_event = ws_response.event
            ws_response = ws_response.data
            ws_response.update({'event': response_event})
    if isinstance(ws_response, dict):
        ws.send_json(ws_response)
    if isinstance(ws_response, str):
        ws.send_str(ws_response)

def check_train_station(request, emit):
    if (train_station.get(request.get('station_name'))):
        emit(WS_Response_Data(
            # event
            'response.train.station',
            # data
            {
                'status': True, 'message': 'success',
                'key': request.get('key'),
                'station_code': train_station.get(request.get('station_name'))
            }
        ))
    else:
        emit(WS_Response_Data(
            # event
            'response.train.station',
            # data
            {
                'status': False, 'message': 'the station not found',
                'key': request.get('key'),
                'station_code': None
            }
        ))

async def foreach_train(result, emit):
    if isinstance(result, train_query_result.ResultParser):
        # emit response.train.count
        emit(WS_Response_Data(
            # event
            'response.train.count',
            # data
            {
                'status': True,
                'message': 'succeed',
                'count': len(result.get_trains_code())
            }
        ))
        # all train information
        for train_code in result.get_trains_code():
            selector = result.select(train_code)

            emit(WS_Response_Data(
                # event
                'response.train.profile',
                # data
                {
                    'train_code': selector.train_code,
                    'start_time': selector.start_time,
                    'arrive_time': selector.arrive_time,
                    'total_time': selector.total_time,
                    'start_station': selector.start_station,
                    'end_station': selector.end_station
                }
            ))
            # try:
            #     print('\t', selector.train_code, await selector.seat())
            # except exceptions.ReTryExceed as e:
            #     logging.info('query seat retry count exceeded. ignore this train[{}]'.format(selector.train_code))
            # print('\t\t', selector.train_code, await selector.check())

async def query_train_list(request, emit):
    emit(WS_Response_Data(
        # event
        'response.train.list',
        # data
        {
            'status': True,
            'progress': 0,
            'message': 'start'
        }
    ))

    try:
        from_station = request.get('from')
        to_station = request.get('to')
        train_date = request.get('date')
        ts = request.get('ts')
        train_ts = time.mktime(time.strptime(train_date, '%Y-%m-%d'))
        await train_query.TrainQuery().query(
            from_station, to_station,
            train_ts,
            result_handler = foreach_train, args = (emit,)
        )
    except KeyError:
        raise RuntimeWarning('this frame is not true frame')
    except Exception as e:
        raise RuntimeError(e)

    # ending
    emit(WS_Response_Data(
        # event
        'response.query',
        # data
        {
            'status': True,
            'progress': 100,
            'message': 'end'
        }
    ))

global_event_handlers = {
    'request.train.station': check_train_station,
    'request.train.list': query_train_list
}

async def web_socket_handler(request):
    # WebSocket Response Instance
    ws = web.WebSocketResponse()
    # Prepare Request
    await ws.prepare(request)
    # emit methods
    emit = partial(_server_emit, ws)

    async for message in ws:
        if message.type == aiohttp.WSMsgType.ERROR:
            logging.warning('ws connection closed with exception %s'.format(ws.exception()))
        elif message.type == aiohttp.WSMsgType.TEXT:
            try:
                message_data = json.loads(message.data)
            except Exception:
                await ws.close()
                logging.warning('the ws message is not json string')
                raise RuntimeWarning('the ws message is not json string')
            try:
                event = message_data['event']
                message_data.pop('event')

                if event in global_event_handlers and callable(global_event_handlers[event]):
                    if asyncio.iscoroutinefunction(global_event_handlers[event]):
                        await global_event_handlers[event](message_data, emit)
                    else:
                        global_event_handlers.get(event)(message_data, emit)
                else:
                    raise RuntimeWarning('event \'{}\'not found'.format(event))
            except RuntimeWarning:
                raise
            except KeyError:
                raise RuntimeWarning('the ws message must be have event name')
            except Exception:
                raise RuntimeWarning('the ws message handler had error occurs')
    return ws

if __name__ == '__main__':
    app = web.Application()

    app.router.add_get("/", index_handler)
    app.router.add_get('/socket', web_socket_handler)
    app.router.add_static('/static', './static')

    web.run_app(app, host = '127.0.0.1', port = 5000)