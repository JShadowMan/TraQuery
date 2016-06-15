# -*- coding: UTF-8 -*-
# Implemented in Python. Written by ShadowMan(Wang).
# Distributed under the MIT License.
'''This Package Provides Train Query

Object Type:
    TraError ---

    TraQuery ---

    TraSelect ---

    TraResult ---

Functions:

    adult --- 

    student ---

@todo: Document
'''

import time
import urllib2
import json
import re

# Check SSL
try:
    import ssl
except ImportError:
    _have_ssl = False
else:
    _have_ssl = True

# Passenger Type
ERTYPE_ADULT   = 'ADULT'
ERTYPE_STUDENT = '0X00'

# Seat Type
SEAT_SWZ = 'first'              # 商务座
SEAT_YDZ = 'business'           # 一等座
SEAT_EDZ = 'economy'            # 二等座
SEAT_WZ  = 'none'               # 无座
SEAT_RW  = 'cushionedBerth'     # 软卧
SEAT_YW  = 'semiCushionedBerth' # 硬卧 
SEAT_RZ  = 'softSeat'           # 软座
SEAT_YZ  = 'hardSeat'           # 硬座
SEAT_GR  = 'advancedSoft'       # 高级软卧


class QueryError(IOError):
    def __init__(self, reason, code = 0):
        self.reason = reason
        self.code   = code

    def __str__(self):
        return '<TraQuery Exception %s>' % ( self.reason )

# Getting Train Station List From 12306
class TraStationList(object):
    _base_url = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version='

    def __init__(self, stationVersion = '1.8954'):
        self.__stationList = {}
        self.__initTraStationList(stationVersion)

    def __initTraStationList(self, stationVersion):
        try:
            handler = urllib2.urlopen(self._base_url + stationVersion)
        except urllib2.URLError:
            if _have_ssl == True and '_create_unverified_context' in dir(ssl):
                handler = urllib2.urlopen(self._base_url + stationVersion,  context = ssl._create_unverified_context())
            else:
                raise QueryError('Require SSL Module')

        if handler.getcode() == 200:
            self.__parseStation(handler.read())
        else:
            raise QueryError("Get Request Error Occurs.")

    def __parseStation(self, stationList):
        stationList = stationList.decode('utf-8')
        stationList = stationList.replace('  ', '') # f**k 12306
        stationList = re.findall('([^@a-z|,;\'(\d+)_= ]+)', stationList)

        if (len(stationList) % 2) != 0:
            raise QueryError("Get Station List Error Occurs")

        index = 0
        while index < len(stationList):
            self.__stationList[stationList[index]] = stationList[index + 1]
            index = index + 2

    def code(self, station):
        if type(station) == type(''):
            station = station.decode('utf-8')

        if (station in self.__stationList):
            return self.__stationList[station]
        else:
            raise QueryError('Station Not Exists')
traStationList = TraStationList()
class TraQuery(object):
    # Private Members
    __queryTrainUrl = 'https://kyfw.12306.cn/otn/leftTicket/query?leftTicketDTO.train_date=%s&leftTicketDTO.from_station=%s&leftTicketDTO.to_station=%s&purpose_codes=%s'
    __queryStackUrl = 'https://kyfw.12306.cn/otn/lcxxcx/query?purpose_codes=%s&queryDate=%s&from_station=%s&to_station=%s'

    def __init__(self):
        self.__result = { 'trainCount': None, 'trains': {} }

    def letsGo(self, fromStation, toStation, date, erType = ERTYPE_ADULT):
        try:
            fromStation = traStationList.code(fromStation)
            toStation   = traStationList.code(toStation)
            trainDate   = self.__parseDate(date)
            erType      = self.__parseErType(erType)

            self.__query(trainDate, fromStation, toStation, erType)
        except QueryError, e:
            raise e

        return TraResult(self.__result)

    def __parseDate(self, date):
        if date.find(':') and date.count(':') == 2:
            date = time.strptime(date, '%Y:%m:%d')
        elif date.find('-') and date.count('-') == 2:
            date = time.strptime(date, '%Y-%m-%d')
        elif date.find('/') and date.count('/') == 2:
            date = time.strptime(date, '%Y/%m/%d')
        elif date.find('.') and date.count('.') == 2:
            date = time.strptime(date, '%Y.%m.%d')
        else:
            raise QueryError('Date Format Error Occurs')

        if time.mktime(date) < time.time() and time.mktime(date) < time.time() - (time.time() % 86400) - 8 * 3600:
            raise QueryError('Date Error Occurs')

        return time.strftime('%Y-%m-%d', date)

    def __parseErType(self, erType):
        if erType in (ERTYPE_ADULT, ERTYPE_STUDENT):
            return erType
        else:
            return ERTYPE_ADULT

    def __query(self, trainDate, fromStation, toStation, erType):
        contents = self.__sendRequest(self.__queryTrainUrl % ( trainDate, fromStation, toStation, erType ))

        self.__parseResult(contents, trainDate, erType)

    def __sendRequest(self, url):
        try:
            handler = urllib2.urlopen(url)
        except urllib2.URLError:
            if _have_ssl == True and '_create_unverified_context' in dir(ssl):
                handler = urllib2.urlopen(url,  context = ssl._create_unverified_context())
            else:
                raise QueryError('Require SSL Module')

        if handler.getcode() == 200:
            return handler.read().decode('utf8')
        else:
            raise QueryError('Request Error Occurs')

    def __parseResult(self, contents, date, erType):
        contents = json.loads(contents)

        self.__result['trainCount'] = len(contents['data'])
        if len(contents['data']) == 0:
            raise QueryError('Not Train Data')
        self.__result['erType'] = erType
        self.__result['date'] = date

        stackContent = self.__sendRequest(self.__queryStackUrl % ( erType, date, contents['data'][0]['queryLeftNewDTO']['from_station_telecode'], contents['data'][0]['queryLeftNewDTO']['to_station_telecode'] ))
        stackContent = json.loads(stackContent)
        stackContent = stackContent['data']['datas']

        for train in contents['data']:
            trainInfo = train['queryLeftNewDTO']

            self.__result['trains'][ trainInfo['station_train_code'] ] = {
                # Train Information
                'train': { 'code': trainInfo['station_train_code'], 'class': trainInfo['station_train_code'][0], 'no': trainInfo['train_no'] },
                # Station Information
                'station': { 'from': trainInfo['from_station_name'], 'to': trainInfo['end_station_name'], 'fromNo': trainInfo['from_station_no'], 'fromCode': trainInfo['from_station_telecode'], 'toCode': trainInfo['to_station_telecode'], 'toNo': trainInfo['to_station_no'] },
                # Could Purchase Flag
                'purchase': trainInfo['canWebBuy'] == 'Y',
                # Time Information
                'time': { 'start': trainInfo['start_time'], 'end': trainInfo['arrive_time'], 'total': trainInfo['lishi'] },
                # Seat Price
                'price': {},
                # Stack Count
                'stack': self.__getStack(stackContent, trainInfo['train_no']),
                # All Station
                'allStation': {},
                # Seat Type
                'seatType': trainInfo['seat_types']
            }

    def __getStack(self, contents, stationNo):
        train = None
        for trainCode in contents:
            if trainCode['train_no'] == stationNo:
                train = trainCode
                break

        return {'first': self.__fromListGet(train, 'swz_num'), # 商务
                'business': self.__fromListGet(train, 'zy_num'), # 一等座
                'economy': self.__fromListGet(train, 'ze_num'), # 二等座
                'none': self.__fromListGet(train, 'wz_num'), # 无座
                'hardSeat': self.__fromListGet(train, 'yz_num'), # 硬座
                'softSeat': self.__fromListGet(train, 'rz_num'), # 软座
                'semiCushionedBerth': self.__fromListGet(train, 'yw_num'), # 硬卧
                'cushionedBerth': self.__fromListGet(train, 'rw_num'), # 软卧
                'advancedSoft': self.__fromListGet(train, 'gr_num') # 高级软卧
            }

    def __fromListGet(self, lst, key):
        if key in lst:
            if lst[key] == u'--' or lst[key] == u'无':
                return None

            return lst[key]
        else:
            return None

class TraSelect(object):
    # Private: Select URL
    __queryPriceUrl = 'https://kyfw.12306.cn/otn/leftTicket/queryTicketPrice?train_no=%s&from_station_no=%s&to_station_no=%s&seat_types=%s&train_date=%s'
    __queryStations = 'https://kyfw.12306.cn/otn/czxx/queryByTrainNo?train_no=%s&from_station_telecode=%s&to_station_telecode=%s&depart_date=%s'

    def selectPrice(self, trainNo, fromStationNo, toStationNo, seatTypes, date):
        contents = self.__getContents(self.__queryPriceUrl % ( trainNo, fromStationNo, toStationNo, seatTypes, date ))
        contents = contents['data']

        return {'first': self.__fromListGet(contents, 'A9'), # 商务
                'business': self.__fromListGet(contents, 'M'), # 一等座
                'economy': self.__fromListGet(contents, 'O'), # 二等座
                'none': self.__fromListGet(contents, 'WZ'), # 无座
                'hardSeat': self.__fromListGet(contents, 'A1'), # 硬座
                'softSeat': self.__fromListGet(contents, 'A2'), # 软座
                'semiCushionedBerth': self.__fromListGet(contents, 'A3'), # 硬卧
                'cushionedBerth': self.__fromListGet(contents, 'A4'), # 软卧
                'advancedSoft': self.__fromListGet(contents, 'A6') # 高级软卧
            }

    def selectStations(self, stationNo, date, fromStationCode, toStationCode):
        contents = self.__getContents(self.__queryStations % ( stationNo, fromStationCode, toStationCode, date ))
        contents = contents['data']['data']
        result   = []

        for station in contents:
            stopover = re.search('[\d]+', station['stopover_time'])
            result.append({
                'no': station['station_no'],
                'name': station['station_name'],
                'startTime': station['start_time'],
                'arriveTime': None if (station['arrive_time'] == u'----') else station['arrive_time'],
                'stopover': stopover and stopover.group() or None,
                'enable': station['isEnabled']
            })

        return result

    def __getContents(self, url):
        try:
            handler = urllib2.urlopen(url)
        except urllib2.URLError:
            if _have_ssl == True and '_create_unverified_context' in dir(ssl):
                handler = urllib2.urlopen(url,  context = ssl._create_unverified_context())
            else:
                raise QueryError('Require SSL Module')

        if handler.getcode() == 200:
            return json.loads(handler.read().decode('utf-8'))
        else:
            raise QueryError('Request Error Occurs')

    def __fromListGet(self, lst, key):
        if key in lst:
            if lst[key] == u'--' or lst[key] == u'无':
                return None

            return lst[key]
        else:
            return None

traSelect = TraSelect()
class TraResult(object):

    def __init__(self, result):
        self.__result = result

    def trainCount(self):
        return self.__result['trainCount']

    def trainCodes(self):
        codes = []
        for trainCode in self.__result['trains']:
            codes.append(trainCode)

        return codes
    
    def purchaseFlag(self, trainCode):
        if trainCode in self.__result['trains']:
            return self.__result['trains'][trainCode]['purchase']
    
    def selectTrainClass(self, trainCode):
        if trainCode in self.__result['trains']:
            return self.__result['trains'][trainCode]['train']['class']
    
    def SelectSeat(self, trainCode):
        seats = {}
        if trainCode in self.__result['trains']:
            self.__checkPrice(trainCode)

            for seat in self.__result['trains'][trainCode]['stack']:
                seats[seat] = { 'count': self.__result['trains'][trainCode]['stack'][seat], 'price': self.__result['trains'][trainCode]['price'][seat] }
        else:
            raise QueryError('TrainCode Non Exists')

        return self.__seatFilter(seats)

    def selectSeatPrice(self, trainCode, seatType):
        if seatType not in [ SEAT_SWZ, SEAT_YDZ, SEAT_EDZ, SEAT_WZ, SEAT_RW, SEAT_YW, SEAT_RZ, SEAT_YZ, SEAT_GR ]:
            raise QueryError('Seat Type Non Exists')
        if trainCode not in self.__result['trains']:
            raise QueryError('TrainCode Non Exists')

        self.__checkPrice(trainCode)

        return self.__result['trains'][trainCode]['price'][seatType]

    def selectSeatCount(self, trainCode, seatType):
        if seatType not in [ SEAT_SWZ, SEAT_YDZ, SEAT_EDZ, SEAT_WZ, SEAT_RW, SEAT_YW, SEAT_RZ, SEAT_YZ, SEAT_GR ]:
            raise QueryError('Seat Type Non Exists')
        if trainCode not in self.__result['trains']:
            raise QueryError('TrainCode Non Exists')

        return self.__result['trains'][trainCode]['stack'][seatType]

    def selectPassesStation(self, trainCode):
        if trainCode not in self.__result['trains']:
            raise QueryError('TrainCode Non Exists')
        self.__checkAllStations(trainCode)

        startStationNo = int(self.__result['trains'][trainCode]['station']['fromNo']) - 1
        endStationNo   = int(self.__result['trains'][trainCode]['station']['toNo'])
        return self.__result['trains'][trainCode]['allStation'][startStationNo:endStationNo]

    def __checkPrice(self, trainCode):
        if len(self.__result['trains'][trainCode]['price']) == 0:
                self.__result['trains'][trainCode]['price'] = traSelect.selectPrice(
                    self.__result['trains'][trainCode]['train']['no'],
                    self.__result['trains'][trainCode]['station']['fromNo'],
                    self.__result['trains'][trainCode]['station']['toNo'],
                    self.__result['trains'][trainCode]['seatType'],
                    self.__result['date']
                )
    
    def __checkAllStations(self, trainCode):
        if len(self.__result['trains'][trainCode]['allStation']) == 0:
            self.__result['trains'][trainCode]['allStation'] = traSelect.selectStations(
                self.__result['trains'][trainCode]['train']['no'],
                self.__result['date'],
                self.__result['trains'][trainCode]['station']['fromCode'],
                self.__result['trains'][trainCode]['station']['toCode']
            )

    def __seatFilter(self, dic):
        invalidIndex = []

        for index in dic:
            if dic[index]['count'] == None and dic[index]['price'] == None:
                invalidIndex.append(index)

        for index in invalidIndex:
            dic.pop(index)

        return dic



traQuery = TraQuery()
'''Public Function: adult(fromStation, toStation, date)
@param fromStation: Departure Station
@param toStation: Terminal Station
@param date: Departure Date
    Format:
        Year:Month:Day
        Year-Month-Day
        Year/Month/Day
        Year.Month.Day
@return: TraResult
'''
def adult(fromStation, toStation, date):
    return traQuery.letsGo(fromStation, toStation, date, ERTYPE_ADULT)


'''Public Function: student(fromStation, toStation, date)
@param fromStation: Departure Station
@param toStation: Terminal Station
@param date: Departure Date
    Format:
        Year:Month:Day
        Year-Month-Day
        Year/Month/Day
        Year.Month.Day
@return: TraResult
'''
def student(fromStation, toStation, date):
    return traQuery.letsGo(fromStation, toStation, date, ERTYPE_STUDENT)

