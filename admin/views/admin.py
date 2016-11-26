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


admin = Blueprint("admin", __name__)


@admin.route("/home/login", methods=["GET"])
@general("home login")
def home_login():
    return TempResponse("home_login.html")

@admin.route("/home/main", methods=["GET"])
@general("home main")
def home_main():
    return TempResponse("home_main.html")

@admin.route("/home/welcome", methods=["GET"])
@general("home welcome")
def home_welcome():
    return "welcome"

@admin.route("/home/report", methods=["GET"])
@general("home report")
def home_report():
    return "report"

