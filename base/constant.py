#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    configure constant variables for system
"""

class SESSION(object):
    KEY_USERID = "userid"
    KEY_USERNAME = "username"
    PROJECT_COOKIE_NAME = "ad_manager"


class BOOLEAN(object):
    FALSE = 0
    TRUE = 1

    ALL = (FALSE, TRUE)

    MAP = {
        FALSE: False,
        TRUE: True
    }

    FROM = {
        True: TRUE,
        False: FALSE
    }

    DESC = {
        FALSE: "否",
        TRUE: "是",
    }


class CHANNEL(object):
    PAY_TYPE_SDK = 1
    PAY_TYPE_CPA = 2
    PAY_TYPE_CPS = 3
    PAY_TYPE_CPT = 4
    PAY_TYPE_CPC = 5
    PAY_TYPE_FREE = 6
    PAY_TYPE_OTHER = 7

    PAY_TYPES = {
        PAY_TYPE_SDK: "sdk",
        PAY_TYPE_CPA: "cpa",
        PAY_TYPE_CPS: "cps",
        PAY_TYPE_CPT: "cpt",
        PAY_TYPE_CPC: "cpc",
        PAY_TYPE_FREE: "free",
        PAY_TYPE_OTHER: "other",
    }

    MEDIA_TYPE_SEARCH = 1
    MEDIA_TYPE_UNION = 2
    MEDIA_TYPE_TOOL = 3
    MEDIA_TYPE_APP = 4
    MEDIA_TYPE_VIDEO = 5
    MEDIA_TYPE_CPS = 6
    MEDIA_TYPE_OTHER = 7

    MEDIA_TYPES = {
        MEDIA_TYPE_SEARCH: "搜索",
        MEDIA_TYPE_UNION: "联盟",
        MEDIA_TYPE_TOOL: "工具",
        MEDIA_TYPE_APP: "应用",
        MEDIA_TYPE_VIDEO: "视频",
        MEDIA_TYPE_CPS: "CPS",
        MEDIA_TYPE_OTHER: "其他",
    }


class PLATFORM(object):
    TYPE_IOS = 1
    TYPE_ANDROID = 2
    TYPE_APP = 3
    TYPE_PC = 4

    TYPES = {
        TYPE_IOS: "ios",
        TYPE_ANDROID: "android",
        TYPE_APP: "移动端",
        TYPE_PC: "PC端",
    }


class ROLE(object):
    TYPE_SUPER = 1
    TYPE_PROMOTION = 2
    TYPE_CP = 3

    TYPES = {
        TYPE_SUPER: "超级管理员",
        TYPE_PROMOTION: "营销推广专员",
        TYPE_CP: "CP",
    }


class CODE(object):
    CODE_TYPE_CLICK = 1
