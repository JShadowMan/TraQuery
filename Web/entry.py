# -*- coding: UTF-8 -*-
import sys
import flask, flask_socketio
from gevent import monkey
import traceback

sys.path.append('..')
monkey.patch_all()

application = flask.Flask(__name__)
application.secret_key = '\x8f\xd4\xb6t8w{>q\xf9g\xd99H\xdfp\xa3\xa3f\x86Q\xb3t\x1e' # os.urandom(24)
socketio = flask_socketio.SocketIO(application, async_mode = 'gevent')

from TraQuery import TraQuery
traQuery = TraQuery.TraQuery()

@application.route('/')
@application.route('/index.html')
def index():
    return flask.render_template('index.html', options = { 'title': 'Train Query Helper' })

@socketio.on_error_default
def error_handler(e):
    print('An error has occurred: ' + str(e))

@socketio.on('connection', namespace = '/query')
def connection():
    socketio.emit('response.station.code', { 'data': u'Welcome to Train Query Helper' })

@socketio.on('request.station.code', namespace = '/query')
def queryStationCode(message):
    if (message.get('stationName') != None and message.get('element') != None):
        try:
            statioName = eval("'" + message.get('stationName').replace('%', '\\x').lower() + "'")
            flask_socketio.emit('response.station.code', { 'code': TraQuery.traStationList.code(statioName), 'element': message.get('element') })

        except TraQuery.QueryError, e:
            flask_socketio.emit('response.error', { 'error': e.getMessage(), 'element': message.get('element') })
    else:
        flask_socketio.emit('response.error', { 'error': 'Bad Request' })


@socketio.on('request.train.inforamtion', namespace = '/query')
def queryTraCount(message):
    if message.get('fromStationCode') == None or message.get('toStationCode') == None or message.get('date') == None:
        flask_socketio.emit('response.error', { 'error': 'Request Bad' })

    try:
        # Query Result Instance
        traResult = TraQuery.adult(message.get('fromStationCode'), message.get('toStationCode'), message.get('date'))
        # Send Train Count Information
        flask_socketio.emit('response.train.count', { 'count': traResult.trainCount() })
        # Send All Train Code
        flask_socketio.emit('response.train.codes', { 'trains': traResult.trainCodes() })
        # Send Train Inforamtion

        for trainCode in traResult.trainCodes():
            responsed = {}
            responsed['code'] = trainCode
            responsed['class'] = traResult.selectTrainClass(trainCode)
            responsed['seats'] = traResult.SelectSeat(trainCode)
            responsed['buy'] = traResult.purchaseFlag(trainCode)
            responsed['passesStations'] = traResult.selectPassesStation(trainCode)

            flask_socketio.emit('response.train.item', responsed)
    except TraQuery.QueryError, e:
        flask_socketio.emit('response.error.nodata', { 'error': e.getMessage() })
    except Exception, exc:
        print traceback.format_exc()


if __name__ == '__main__':
    socketio.run(application, debug = True)
    
