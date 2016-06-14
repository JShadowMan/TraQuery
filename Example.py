# -*- coding: UTF-8 -*-
'''
Created on 2016年6月10日

@author: ShadowMan
'''

import TraQuery.TraQuery as TraQuery

march = TraQuery.adult('南京', '北京', '2016/06/16')

print "Train List", march.trainCodes(), "Total:", march.trainCount()

for trainCode in march.trainCodes():
    passesStation = march.selectPassesStation(trainCode)
    print trainCode, march.selectTrainClass(trainCode), march.SelectSeat(trainCode), march.purchaseFlag(trainCode)
    for station in passesStation:
        print station['name'], station['arriveTime'], station['startTime'], station['stopover']