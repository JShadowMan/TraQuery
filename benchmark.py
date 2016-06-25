# -*- coding: UTF-8 -*-
from TraQuery import TraQuery
import time, random, threading

print 'Import Module Time In %.9f' % time.clock()

TraQuery.TraStationList.code('北京')
print 'Initialize Station List Takes %.9f sec\n' % time.clock()

stationLists = TraQuery.TraStationList.stationNames()
time.clock()

# 1,000 Times
for index in range(1000):
    TraQuery.TraStationList.code('广州')
print 'Getting Station Code 1,000 Times To Spend %.9f sec' % time.clock()

# Random 1,000 Times
for index in range(1000):
    TraQuery.TraStationList.code(random.choice(stationLists))
print 'Getting Random Station Code 1,000 Times To Spend %.9f sec\n' % time.clock()

# 10,000 Times
for index in range(10000):
    TraQuery.TraStationList.code('广州')
print 'Getting Station Code 10,000 Times To Spend %.9f sec' % time.clock()

# Random 10,000 Times
for index in range(10000):
    TraQuery.TraStationList.code(random.choice(stationLists))
print 'Getting Station Code 10,000 Times To Spend %.9f sec\n' % time.clock()

# 100,000 Times
for index in range(100000):
    TraQuery.TraStationList.code('广州')
print 'Getting Station Code 100,000 Times To Spend %.9f sec' % time.clock()

# Random 100,000 Times
for index in range(100000):
    TraQuery.TraStationList.code(random.choice(stationLists))
print 'Getting Station Code 100,000 Times To Spend %.9f sec\n' % time.clock()

# Thread Target
def getStation(threadIndex, times):
    global gettingTime

    print 'Thread %d Start in %s' % (threadIndex, time.ctime())
    for index in range(times):
        TraQuery.TraStationList.code('广州')

# Thread Target
def randomGetStation(threadIndex, times):
    print 'Thread %d Start in %s' % (threadIndex, time.ctime())
    for index in range(times):
        TraQuery.TraStationList.code(random.choice(stationLists))

# Multi User(10) Get Station 1000 Times
threads = []
for index in range(10):
    threads.append(threading.Thread( target=getStation, args=(index, 100000) ))
time.clock()
for thread in threads:
    thread.setDaemon(True)
    thread.start()
thread.join()
print 'Multi User(10) Getting Station Code 1,000 Times To Spend %.9f sec\n' % ( time.clock() )

# Multi User(100) Get Station 10000 Times
threads = []
for index in range(100):
    threads.append(threading.Thread( target=getStation, args=(index, 10000) ))
time.clock()
for thread in threads:
    thread.setDaemon(True)
    thread.start()
thread.join()
print 'Multi User(100) Getting Station Code 10,000 Times To Spend %.9f sec\n' % time.clock()

