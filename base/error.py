#!/usr/bin/env python
# -*- coding: gb2312 -*-
"""
    exception definations
"""

class CODE(object):
    # interface
    IF_INVALID_URL = 10000
    IF_INVALID_PARAM = 10001
    IF_SOCKET_ERROR = 10002
    IF_PARSE_ERROR = 10003
    IF_OTHER_ERROR = 19999

    # base
    PROGRAM_ERROR = 20000
    DATA_ERROR = 20001


class Error(Exception):
    def __init__(self, code, desc=""):
        super(Error, self).__init__()
        self._code = code
        self._desc = desc


    def __str__(self):
        return "[%d]%s" % (self._code, self._desc)


    def code(self):
        return self._code


class InterfaceError(Error):
    def __init__(self, code, desc=None):
        super(InterfaceError, self).__init__(code, desc)



