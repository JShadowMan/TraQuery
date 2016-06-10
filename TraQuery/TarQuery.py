# -*- coding: UTF-8 -*-
'''
Created on 2016年6月10日

@author: ShadowMan
'''
import TraStationList as TSList

class TraQuery(object):
    '''
    China train 
    '''
    traStationList = TSList.TraStationList()
    
    def __init__(self):
        pass


if __name__ == '__main__':
    print TraQuery.traStationList.get("北京")
    print TraQuery.traStationList.get("南京")
    print TraQuery.traStationList.get("上海虹桥")
    print TraQuery.traStationList.get("厦门")
    print TraQuery.traStationList.get("温州")
    
