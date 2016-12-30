#!/usr/bin/env python3
#
# Copyright (C) 2016 ShadowMan
#

class ReTryExceed(RuntimeError):
    pass

class NetworkForbidden(RuntimeError):
    pass

class StationError(Exception):
    pass

class InvalidTrain(Exception):
    pass