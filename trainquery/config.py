#!/usr/bin/env python3
#
# Copyright (C) 2016-2017 ShadowMan
#

# Number of retries
RETRIES_TIME = 5

# Passenger is adult
PASSENGER_ADULT = 'ADULT'

# Passenger is student
PASSENGER_STUDENT = '0X00'

QUERY_BASE_URL = 'https://kyfw.12306.cn/otn/'

# Train query address
QUERY_TRAIN_URL = 'https://kyfw.12306.cn/otn/leftTicket/queryX'

# Stack query address
QUERY_STACK_URL = 'https://kyfw.12306.cn/otn/lcxxcx/query'

# Seat price query address
QUERY_PRICE_URL = 'https://kyfw.12306.cn/otn/leftTicket/queryTicketPrice'

# All stations query address
QUERY_ALL_STATIONS = 'https://kyfw.12306.cn/otn/czxx/queryByTrainNo'

# Train is disable
IN_TIME_NOT_BUY = 'IS_TIME_NOT_BUY'