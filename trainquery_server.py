#!/usr/bin/env python3
#
# Copyright (C) 2016-2017 ShadowMan
#
import os
import json
import logging
import aiohttp
import flask
import flask, flask_socketio
from train_query import *

application = flask.Flask(__name__)
application.secret_key = os.urandom(24)
server = flask_socketio.SocketIO(application)

logging.basicConfig(level=logging.INFO)

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
    server.emit('response.query', { 'status': True, 'message': 'Succeed' })

if __name__ == '__main__':
    server.run(application, debug = True)