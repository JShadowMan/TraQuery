# -*- coding: UTF-8 -*-
'''
Created on 2016年6月10日

@author: ShadowMan
'''
import TraQuery.TraQuery as TraQuery

march = TraQuery.adult('福鼎', '北京', '2016/06/16')

print "Train List", march.trainCodes(), "Total:", march.trainCount(), '\n'

for trainCode in march.trainCodes():
    passesStation = march.selectPassesStation(trainCode)
    print 'Code', trainCode, '\tClass:', march.selectTrainClass(trainCode), '\n'
    
    for seat in march.SelectSeat(trainCode):
        print 'Seat:', seat, '\t', march.selectSeatCount(trainCode, seat), '\t', march.selectSeatPrice(trainCode, seat)
    print 'Buy:', march.purchaseFlag(trainCode), '\n\nStation List:'
    for station in passesStation:
        print station['name'], '\t', station['arriveTime'], '\t', station['startTime'], '\t', station['stopover']
    print '\n'

