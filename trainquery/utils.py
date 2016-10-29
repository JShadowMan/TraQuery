''' utils.py:

'''
import json
import aiohttp
from collections import OrderedDict

__queryTrainUrl = 'https://kyfw.12306.cn/otn/leftTicket/queryX'
__queryStackUrl = 'https://kyfw.12306.cn/otn/lcxxcx/query'
__queryTrainPrice = 'https://kyfw.12306.cn/otn/leftTicket/queryTicketPrice'

async def fetch(loop, *args, **kwargs):
    try:
        async with aiohttp.ClientSession(loop = loop, connector = aiohttp.TCPConnector(verify_ssl = False)) as client:
            async with client.get(*args, **kwargs) as response:
                if response.status is 200:
                    return await response.text()
                else:
                    raise Exception('request error', response.status)
    except Exception as e:
        print('utils.fetch error', e)

async def getTrainInformation(loop, fromStation, toStation, date, passengerType):
    payload = OrderedDict([
        ('leftTicketDTO.train_date', date),
        ('leftTicketDTO.from_station', fromStation),
        ('leftTicketDTO.to_station', toStation),
        ('purpose_codes', passengerType)
    ])  # **** 1*3*6
    return await fetch(loop, url = __queryTrainUrl, params = payload)

async def getStackInformation(loop, fromStation, toStation, date, passengerType):
    payload = OrderedDict([
        ('purpose_codes', passengerType),
        ('queryDate', date),
        ('from_station', fromStation),
        ('to_station', toStation)
    ])
    return await fetch(loop, url = __queryStackUrl, params = payload)

async def getPriceInformation(loop, trainId, startStation, endStation, seatType, date):
    payload = OrderedDict([
        ('train_no', trainId),
        ('from_station_no', startStation.pos),
        ('to_station_no', endStation.pos),
        ('seat_types', seatType[0]),
        ('train_date', date)
    ])
    return await fetch(loop, url = __queryTrainPrice, params = payload)

def dictGet(dic, key):
    if key in dic:
        if dic[key] == '--':
            return None
        if dic[key] == '\u65e0':
            return 0
        return dic[key]
    else:
        return None