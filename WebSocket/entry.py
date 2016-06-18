import time
import flask
from flask_socketio import SocketIO, emit

asyncMode = None
if asyncMode is None:
    try:
        from gevent import monkey

        asyncMode = 'gevent'
    except ImportError:
        pass
if asyncMode == 'gevent':
    monkey.patch_all()

application = flask.Flask(__name__)
application.secret_key = '\x8f\xd4\xb6t8w{>q\xf9g\xd99H\xdfp\xa3\xa3f\x86Q\xb3t\x1e'

socketio = SocketIO(application, async_mode = asyncMode)

@application.route('/')
@application.route('/index.html')
def index():
    return flask.render_template('index.html')

@socketio.on('query.train', namespace = '/query')
def queryTrain(message):
    print message
    for index in range(10):
        emit('responsed', { 'data': 'Hello World', 'count': index })
        time.sleep(1)

if __name__ == '__main__':
    socketio.run(application)

