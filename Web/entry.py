# -*- coding: UTF-8 -*-
import sys, traceback
import flask, flask_socketio, eventlet

sys.path.append('..')
from TraQuery import TraQuery

eventlet.monkey_patch()

application = flask.Flask(__name__)
application.secret_key = '\x8f\xd4\xb6t8w{>q\xf9g\xd99H\xdfp\xa3\xa3f\x86Q\xb3t\x1e' # os.urandom(24)
socketio = flask_socketio.SocketIO(application)

serverStatus = { 'online': 0, 'active': 0 }

@application.route('/')
@application.route('/index.html')
def index():
    return flask.render_template('index.html', options = { 'title': 'Train Query Helper' })

@socketio.on_error_default
def error_handler(e):
    print('An error has occurred: ' + str(e))

@socketio.on('connect', namespace = '/query')
def connection():
    global serverStatus
    serverStatus['online'] += 1
    flask_socketio.emit('response.server.status', serverStatus)

@socketio.on('disconnect', namespace = '/query')
def disconnection():
    global serverStatus
    serverStatus['online'] -= 1
    serverStatus['active'] -= 1 if serverStatus['active'] > 0 else 0
    flask_socketio.emit('response.server.status', serverStatus, broadcast = True)

@socketio.on('request.station.code', namespace = '/query')
def queryStationCode(message):
    if (message.get('stationName') != None and message.get('element') != None):
        try:
            statioName = eval("'" + message.get('stationName').replace('%', '\\x').lower() + "'")
            flask_socketio.emit('response.station.code', { 'code': TraQuery.TraStationList.code(statioName), 'element': message.get('element') })

        except TraQuery.QueryError, e:
            flask_socketio.emit('response.error', { 'error': e.getMessage(), 'element': message.get('element') })
    else:
        flask_socketio.emit('response.error', { 'error': 'Bad Request' })


@socketio.on('request.train.inforamtion', namespace = '/query')
def queryTraInformation(message):
    if message.get('fromStationCode') == None or message.get('toStationCode') == None or message.get('date') == None:
        flask_socketio.emit('response.error', { 'error': 'Request Bad' })

    # Server Status Changed
    global serverStatus
    serverStatus['active'] += 1

    try:
        # Query Result Instance
        traResult = TraQuery.adult(message.get('fromStationCode'), message.get('toStationCode'), message.get('date'))
        # Send Train Count Information
        flask_socketio.emit('response.train.count', { 'count': traResult.trainCount() })
        # Send All Train Code
        flask_socketio.emit('response.train.codes', { 'trains': traResult.trainCodes() })

        # Send Train Information
        flask_socketio.emit('response.server.status', serverStatus)
        for trainCode in traResult.trainCodes():
            responsed = {}
            responsed['code'] = trainCode
            responsed['class'] = traResult.selectTrainClass(trainCode)

            if traResult.activate(trainCode) == True:
                responsed['seats'] = traResult.SelectSeat(trainCode)
                responsed['time'] = traResult.getTime(trainCode)
            else:
                responsed['activate'] = False

            responsed['buy'] = traResult.purchaseFlag(trainCode)

            flask_socketio.emit('response.train.item', responsed)
    except TraQuery.QueryError, e:
        flask_socketio.emit('response.error.nodata', { 'error': e.getMessage() })
    except Exception:
        print traceback.format_exc()

    serverStatus['active'] -= 1
    flask_socketio.emit('response.server.status', serverStatus)


if __name__ == '__main__':
    socketio.run(application, debug = True)

