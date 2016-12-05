#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Blueprint, request, session, url_for, abort
import functools
from datetime import datetime, date, timedelta
import time
import random
import hashlib
import mysql.connector
from mysql.connector import errorcode

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
@admin_required()
def system_game_list():
    db = db_reader
    game_list = QS(db).table(T.game).select()
    return TempResponse("system_game_list.html",
        game_list = game_list,         
    )


@system.route("/system/game/add", methods=["POST"])
@general("system game add")
@admin_required()
@form_check({
    "gameName": F_str(u"game name") & "strict" & "required",
})
def system_game_add(safe_vars):
    db = db_writer
    try:
        QS(db).table(T.game).insert({
            "name": safe_vars["gameName"],
            "add_time": datetime.now(),
        })
    except mysql.connector.IntegrityError, ex:
        if ex.errno == errorcode.ER_DUP_ENTRY:
            return ErrorResponse("游戏%s已经存在！" % safe_vars["gameName"])
        raise

    return InfoResponse("游戏创建成功！")


@system.route("/system/game/modify", methods=["POST"])
@general("system game modify")
@admin_required()
@form_check({
    "gameId": F_int(u"game id") & "strict" & "required",
    "gameName": F_str(u"game name") & "strict" & "required",
})
def system_game_modify(safe_vars):
    db = db_writer
    try:
        QS(db).table(T.game).where(
            F.id == safe_vars["gameId"]
        ).update({
            "name": safe_vars["gameName"],
            "add_time": datetime.now(),
        })
    except mysql.connector.IntegrityError, ex:
        if ex.errno == errorcode.ER_DUP_ENTRY:
            return ErrorResponse("游戏%s已经存在！" % safe_vars["gameName"])
        raise

    return InfoResponse("游戏修改成功！")


@system.route("/system/media/list", methods=["GET"])
@general("system media list")
@admin_required()
def system_media_list():
    db = db_reader
    media_list = QS(db).table(T.media).select()
    return TempResponse("system_media_list.html",
        media_list = media_list,
    )


@system.route("/system/media/add", methods=["POST"])
@general("system media add")
@admin_required()
@form_check({
    "typeName": F_str(u"type name") & "strict" & "required",
})
def system_media_add(safe_vars):
    db = db_writer
    try:
        QS(db).table(T.media).insert({
            "name": safe_vars["typeName"],
            "add_time": datetime.now(),
        })
    except mysql.connector.IntegrityError, ex:
        if ex.errno == errorcode.ER_DUP_ENTRY:
            return ErrorResponse("媒体类型%s已经存在！" % safe_vars["typeName"])
        raise

    return InfoResponse("媒体类型创建成功！")


@system.route("/system/pay/list", methods=["GET"])
@general("system pay list")
@admin_required()
def system_pay_list():
    db = db_reader
    pay_list = QS(db).table(T.intermodal).select()
    return TempResponse("system_pay_list.html",
        pay_list = pay_list,
    )


@system.route("/system/pay/add", methods=["POST"])
@general("system pay add")
@admin_required()
@form_check({
    "typeName": F_str(u"type name") & "strict" & "required",
})
def system_pay_add(safe_vars):
    db = db_writer
    try:
        QS(db).table(T.intermodal).insert({
            "name": safe_vars["typeName"],
            "add_time": datetime.now(),
        })
    except mysql.connector.IntegrityError, ex:
        if ex.errno == errorcode.ER_DUP_ENTRY:
            return ErrorResponse("付费类型%s已经存在！" % safe_vars["typeName"])
        raise

    return InfoResponse("付费类型创建成功！")


@system.route("/system/channel/list", methods=["GET"])
@general("system channel list")
@admin_required()
@form_check({
    "channelName": F_str(u"channel name") & "strict" & "optional",
})
def system_channel_list(safe_vars):
    db = db_reader

    tables = (T.channel * T.media).on(F.channel__media_type == F.media__id)
    tables = (tables * T.intermodal).on(F.channel__pay_type == F.intermodal__id)
    qs = QS(db).table(tables)

    if safe_vars["channelName"] is not None:
        qs.wheres &= (F.channel__name % util.get_fuzzy_search_str(safe_vars["channelName"]))

    channel_list = qs.order_by(
            F.channel__add_time, desc=True
        ).select("channel.*, media.name as media_name, intermodal.name as pay_name")

    medias = util.dbresult2dict(QS(db).table(T.media).select(), "id", "name")
    pays = util.dbresult2dict(QS(db).table(T.intermodal).select(), "id", "name")

    return TempResponse("system_channel_list.html",
        channel_list = channel_list,
        medias = medias,
        pays = pays,
    )


@system.route("/system/channel/add", methods=["POST"])
@general("system channel add")
@admin_required()
@form_check({
    "channel_name": F_str(u"channel name") & "strict" & "required",
    "media_type": F_int(u"media type") & "strict" & "required",
    "pay_type": F_int(u"pay type") & "strict" & "required",
})
def system_channel_add(safe_vars):
    db = db_writer
    try:
        QS(db).table(T.channel).insert({
            "name": safe_vars["channel_name"],
            "media_type": safe_vars["media_type"],
            "pay_type": safe_vars["pay_type"],
            "add_time": datetime.now(),
        })
    except mysql.connector.IntegrityError, ex:
        if ex.errno == errorcode.ER_DUP_ENTRY:
            return ErrorResponse("渠道%s已经存在！" % safe_vars["channel_name"])
        raise

    return InfoResponse("渠道创建成功！")


@system.route("/system/channel/modify", methods=["POST"])
@general("system channel modify")
@admin_required()
@form_check({
    "channel_id": F_str(u"channel id") & "strict" & "required",
    "channel_name": F_str(u"channel name") & "strict" & "required",
    "media_type": F_int(u"media type") & "strict" & "required",
    "pay_type": F_int(u"pay type") & "strict" & "required",
})
def system_channel_modify(safe_vars):
    db = db_writer
    try:
        QS(db).table(T.channel).where(
            F.id == safe_vars["channel_id"]
        ).update({
            "name": safe_vars["channel_name"],
            "media_type": safe_vars["media_type"],
            "pay_type": safe_vars["pay_type"],
            "add_time": datetime.now(),
        })
    except mysql.connector.IntegrityError, ex:
        if ex.errno == errorcode.ER_DUP_ENTRY:
            return ErrorResponse("渠道%s已经存在！" % safe_vars["channel_name"])
        raise

    return InfoResponse("渠道修改成功！")
