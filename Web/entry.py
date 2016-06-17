import sys
import flask
import json

sys.path.append('..')
application = flask.Flask(__name__)
application.secret_key = '\x8f\xd4\xb6t8w{>q\xf9g\xd99H\xdfp\xa3\xa3f\x86Q\xb3t\x1e' # os.urandom(24)

from TraQuery import TraQuery

traQuery = TraQuery.TraQuery()

def post(key):
    return flask.request.form.get(key)

@application.route('/')
@application.route('/index.html')
def index():
    return flask.render_template('index.html', title = 'Train Query Helper')

@application.route('/query/stationCode', methods = [ 'POST' ])
def queryStationCode():
    if post('stationName') != None:
        try:
            code = TraQuery.traStationList.code(post('stationName'))
        except TraQuery.QueryError, e:
            return json.dumps({ 'error': e.getMessage() })
    else:
        return 'No Form Data'

    return json.dumps({ 'code': code})

@application.route('/query/trainCount', methods = [ 'POST' ])
def queryTraCount():
    if post('fromStationCode') == None or post('toStationCode') == None or post('date') == None:
        return json.dumps({ 'error': 'Request Bad' })
    
    return json.dumps({ 'code': post('fromStationCode') + post('toStationCode') + post('date') })


if __name__ == '__main__':
    application.run(host = '0.0.0.0')
