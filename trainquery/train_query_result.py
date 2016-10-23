'''

'''

import asyncio

class QueryResult(object):

    def __init__(self, trains, stacks, *, loop = asyncio.get_event_loop()):
        self.__trainsInfo = { 'trainCount': None, 'trains': {} }