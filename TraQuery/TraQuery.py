# -*- coding: UTF-8 -*-
'''
Created on 2016年6月10日

@author: ShadowMan
'''
import time, urllib2, json
import TraStationList as TSList

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

class TraQuery(object):
    traStationList = TSList.TraStationList()

    # Private
    __queryTrainUrl = 'https://kyfw.12306.cn/otn/leftTicket/query?leftTicketDTO.train_date=%s&leftTicketDTO.from_station=%s&leftTicketDTO.to_station=%s&purpose_codes=%s'
    __queryPriceUrl = 'https://kyfw.12306.cn/otn/leftTicket/queryTicketPrice?train_no=%s&from_station_no=%s&to_station_no=%s&seat_types=%s&train_date=%s'
    __queryStackUrl = 'https://kyfw.12306.cn/otn/lcxxcx/query?purpose_codes=%s&queryDate=%s&from_station=%s&to_station=%s'


    def __init__(self):
        self.__result = { 'http': None, 'train': None, 'trainCount': None }

    def adult(self, fromStation, toStation, date):
        self.__go(fromStation, toStation, date, ERTYPE_ADULT)

    def student(self, fromStation, toStation, date):
        self.__go(fromStation, toStation, date, ERTYPE_STUDENT)

    def __go(self, fromStation, toStation, date, erType = ERTYPE_ADULT):
        fromStation = self.traStationList.get(fromStation)
        toStation   = self.traStationList.get(toStation)
        trainDate   = self.__parseDate(date)
        erType      = self.__parseErType(erType)

        self.__query(trainDate, fromStation, toStation, erType)

    '''
    Format:
        Year:Month:Day
        Year-Month-Day
        Year/Month/Day
        Year.Month.Day
    Require:
        Year: Full Format
    '''
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
            raise Exception('Date Format Error Occurs')

        if int(time.mktime(date)) < time.time():
            raise Exception('Date Error Occurs')

        return time.strftime('%Y-%m-%d', date)

    def __query(self, trainDate, fromStation, toStation, erType):
        contents = self.__sendRequest(self.__queryTrainUrl % ( trainDate, fromStation, toStation, erType ))

        self.__parseResult(contents, trainDate, erType)

    def __parseErType(self, erType):
        if erType in (ERTYPE_ADULT, ERTYPE_STUDENT):
            return erType
        else:
            return ERTYPE_ADULT
    
    def __sendRequest(self, url):
        try:
            handler = urllib2.urlopen(url)
        except urllib2.URLError:
            if _have_ssl == True:
                context = ssl._create_unverified_context()
                handler = urllib2.urlopen(url,  context = context)
            else:
                raise Exception('Require SSL Module')

            if handler.getcode() == 200:
                return (handler.read()).decode('utf-8')
            else:
                raise Exception('Request Error Occurs')

    def __parseResult(self, contents, date, erType):
        contents = json.loads(contents)

        stackCnt = self.__sendRequest(self.__queryStackUrl % ( erType, date, contents['data'][0]['queryLeftNewDTO']['from_station_telecode'], contents['data'][0]['queryLeftNewDTO']['end_station_telecode'] ))
        stackCnt = json.loads(stackCnt)
        stackCnt = stackCnt['data']['datas']

        self.__result['trainCount'] = len(contents['data'])
        self.__result['train'] = []

        for train in contents['data']:
            trainInfo = train['queryLeftNewDTO']
            self.__result['train'].append({
                'train': { 'code': trainInfo['station_train_code'], 'class': trainInfo['train_class_name'], 'no': trainInfo['train_no'] },
                'station': { 'from': trainInfo['from_station_name'], 'to': trainInfo['end_station_name'], 'fromNo': trainInfo['from_station_no'], 'toNo': trainInfo['to_station_no'] },
                'purchase': trainInfo['canWebBuy'] == 'Y',
                'time': { 'start': trainInfo['start_time'], 'end': trainInfo['arrive_time'], 'total': trainInfo['lishi'] },
                'price': self.__getPrice(trainInfo['train_no'], trainInfo['from_station_no'], trainInfo['to_station_no'], trainInfo['seat_types'], date),
                'stack': self.__getStack(stackCnt)
            })
        print self.__result

    def __getPrice(self, no, fromStationNo, toStationNo, seatTypes, date):
        contents = self.__sendRequest(self.__queryPriceUrl % ( no, fromStationNo, toStationNo, seatTypes, date ))
        contents = json.loads(contents)
        contents = contents['data']

        return {'first': self.__fromListGet(contents, 'A9'), # 商务
                'business': self.__fromListGet(contents, 'M'), # 一等座
                'economy': self.__fromListGet(contents, 'O'), # 二等座
                'none': self.__fromListGet(contents, 'WZ'), # 无座
                'hardSeat': self.__fromListGet(contents, 'A1'), # 硬座
                'softSeat': self.__fromListGet(contents, 'A2'), # 软座
                'semiCushionedBerth': self.__fromListGet(contents, 'A3'), # 硬卧
                'cushionedBerth': self.__fromListGet(contents, 'A4'), # 硬卧
            }

    def __getStack(self, contents):
        return {'first': self.__fromListGet(contents, 'swz_num'), # 商务
                'business': self.__fromListGet(contents, 'zy_num'), # 一等座
                'economy': self.__fromListGet(contents, 'ze_num'), # 二等座
                'none': self.__fromListGet(contents, 'wz_num'), # 无座
                'hardSeat': self.__fromListGet(contents, 'yz_num'), # 硬座
                'softSeat': self.__fromListGet(contents, 'rz_num'), # 软座
                'semiCushionedBerth': self.__fromListGet(contents, 'yw_num'), # 硬卧
                'cushionedBerth': self.__fromListGet(contents, 'rw_num'), # 软卧
            }


    def __fromListGet(self, lst, key):
        if key in lst:
            return lst[key]
        else:
            return None


class TraResult(object):
    
    def __init__(self):
        pass



if __name__ == '__main__':
    train = TraQuery()
    
    train.adult('福鼎', '上海虹桥', '2016:06:12')
    
