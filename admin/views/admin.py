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


@admin.route("/home/login/load", methods=["GET"])
@general("home login load")
@admin_required(strict_login=False)
def home_login_load(logined):
    if logined:
        return Redirect(url_for("admin.home_main"))
    return TempResponse("home_login.html")


@admin.route("/home/login", methods=["POST"])
@general("home login")
@form_check({
    "username": F_str(u"用户名") & "strict" & "required",
    "password": F_str(u"密码") & "strict" & "required",
})
def home_login(safe_vars):
    db = db_reader

    user_info = QS(db).table(T.admin).where(
        (F.name == safe_vars["username"]) & \
        (F.password == safe_vars["password"])
    ).select_one()
    if user_info is None:
        return ErrorResponse("用户名或密码错误")

    session[cfg.SESSION.KEY_USERID] = user_info["id"]
    session[cfg.SESSION.KEY_USERNAME] = user_info["name"]

    return Redirect(url_for("admin.home_main"))


@admin.route("/home/main", methods=["GET"])
@general("home main")
@admin_required()
def home_main():
    return TempResponse("home_main.html")


@admin.route("/home/welcome", methods=["GET"])
@general("home welcome")
@admin_required()
def home_welcome():
    return "welcome"


@admin.route("/home/logout", methods=["GET"])
@general("home logout")
@admin_required()
def home_exit():
    db = db_reader
    session.clear()
    return Redirect(url_for("admin.home_login_load"))
