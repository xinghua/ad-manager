#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Blueprint, request, session, url_for, abort
import functools
from datetime import datetime, date, timedelta
import time
import random
import hashlib

from base import util
from base.connection import db_reader, db_writer, db_redis
from etc import setting as sfg
from base import constant as cfg

from base.framework import *
from base.deco import *
from base.nform import *
from base.smartsql import *
from base.poolmysql import *


system = Blueprint("system", __name__)


@system.route("/system/game/list", methods=["GET"])
@general("system game list")
def system_game_list():
    return TempResponse("system_game_list.html")


@system.route("/system/media/list", methods=["GET"])
@general("system media list")
def system_media_list():
    return TempResponse("system_media_list.html")


@system.route("/system/pay/list", methods=["GET"])
@general("system pay list")
def system_pay_list():
    return TempResponse("system_pay_list.html")


@system.route("/system/channel/list", methods=["GET"])
@general("system channel list")
def system_channel_list():
    return TempResponse("system_channel_list.html")
