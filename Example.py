# -*- coding: UTF-8 -*-
'''
Created on 2016年6月10日

@author: ShadowMan
'''

import TraQuery.TraQuery as TraQuery

march = TraQuery.adult('福州', '北京', '2016/06/15')

print "Train List", march.trainCodes(), "Total:", march.trainCount()

for trainCode in march.trainCodes():
    print trainCode, march.selectTrainClass(trainCode), march.SelectSeat(trainCode), march.purchaseFlag(trainCode)