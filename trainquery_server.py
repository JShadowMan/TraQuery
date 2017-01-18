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
import flask_socketio
from trainquery import train_station, utils, train_query

async_loop = asyncio.get_event_loop()
train_station.init(async_loop)

application = flask.Flask(__name__)
application.secret_key = os.urandom(24)
server = flask_socketio.SocketIO(application)

logging.basicConfig(level = logging.INFO)

@application.route('/')
@application.route('/index.<extension>')
def route_index(extension = None):
    if extension in [ None, 'html', 'php' ]:
        return flask.render_template('index.html')
    else:
        flask.abort(404)

@server.on('connect')
def on_connect():
    logging.info('Client {} Connected'.format('new client'))

@server.on('request.train.station')
def check_train_station(request):
    if (train_station.get(request.get('station_name'))):
        server.emit('response.train.station', {
            'status': True, 'message': 'success',
            'key': request.get('key'),
            'station_code': train_station.get(request.get('station_name'))
        })
    else:
        server.emit('response.train.station', {
            'status': False, 'message': 'the station not found',
            'key': request.get('key'),
            'station_code': None
        })

def __emit_query_train_list_event(result):
    server.emit('response.query', result)

@server.on('request.train.list')
def query_train_list(request):
    from_station = request.get('from')
    to_station = request.get('to')
    train_date = request.get('date')
    ts = request.get('ts')
    query = train_query.TrainQuery()
    train_ts = time.mktime(time.strptime(train_date, '%Y-%m-%d'))

    utils.async_startup(async_loop, query.query(from_station, to_station, train_ts, result_handler = __emit_query_train_list_event))

if __name__ == '__main__':
    server.run(application, debug = True)