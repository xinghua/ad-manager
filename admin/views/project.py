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


project = Blueprint("project", __name__)


@project.route("/project/list", methods=["GET"])
@general("project list")
@form_check({
    "game_id": F_str(u"game id") & "strict" & "optional",
    "channel_id": F_int(u"channel id") & "strict" & "optional",
})
def project_list(safe_vars):
    db = db_reader

    tables = (T.project * T.game).on(F.project__game_id == F.game__id)
    tables = (tables * T.channel).on(F.project__channel_id == F.channel__id)
    tables = (tables * T.media).on(F.channel__media_type == F.media__id)
    tables = (tables * T.intermodal).on(F.channel__pay_type == F.intermodal__id)
    qs = QS(db).table(tables)

    if safe_vars["game_id"] is not None:
        qs.wheres &= (F.game__id == safe_vars["game_id"])

    if safe_vars["channel_id"] is not None:
        qs.wheres &= (F.channel__id == safe_vars["channel_id"])

    project_list = qs.order_by(F.project__add_time, desc=True).select(
        "project.*, game.name as game_name, channel.name as channel_name, \
         media.name as media_name, intermodal.name as pay_name"
    )

    games = util.dbresult2dict(QS(db).table(T.game).select(), "id", "name")
    channels = util.dbresult2dict(QS(db).table(T.channel).select(), "id", "name")

    return TempResponse("project_list.html",
        games = games,         
        channels = channels,
        platforms = cfg.PLATFORM.TYPES,
        project_list = project_list,
    )


@project.route("/project/add", methods=["POST"])
@general("project add")
@form_check({
    "project_name": F_str(u"project name") & "strict" & "required",
    "platform_id": F_int(u"platform id") & "strict" & "required",
    "channel_id": F_int(u"channel id") & "strict" & "required",
    "game_id": F_int(u"game id") & "strict" & "required",
    "url": F_str(u"url") & "strict" & "required",
})
def project_add(safe_vars):
    db = db_writer
    try:
        QS(db).table(T.project).insert({
            "name": safe_vars["project_name"],
            "url": safe_vars["url"],
            "platform_id": safe_vars["platform_id"],
            "channel_id": safe_vars["channel_id"],
            "game_id": safe_vars["game_id"],
            "add_time": datetime.now(),
        })
    except mysql.connector.IntegrityError, ex:
        if ex.errno == errorcode.ER_DUP_ENTRY:
            return ErrorResponse("广告%s已经存在！" % safe_vars["project_name"])
        raise

    return InfoResponse("广告创建成功！")


@project.route("/project/modify", methods=["POST"])
@general("project modify")
@form_check({
    "project_id": F_int(u"project id") & "strict" & "required",
    "project_name": F_str(u"project name") & "strict" & "required",
    "platform_id": F_int(u"platform id") & "strict" & "required",
    "channel_id": F_int(u"channel id") & "strict" & "required",
    "game_id": F_int(u"game id") & "strict" & "required",
    "url": F_str(u"url") & "strict" & "required",
})
def project_modify(safe_vars):
    db = db_writer
    try:
        QS(db).table(T.project).where(
            F.id == safe_vars["project_id"]
        ).update({
            "name": safe_vars["project_name"],
            "url": safe_vars["url"],
            "platform_id": safe_vars["platform_id"],
            "channel_id": safe_vars["channel_id"],
            "game_id": safe_vars["game_id"],
            "add_time": datetime.now(),
        })
    except mysql.connector.IntegrityError, ex:
        if ex.errno == errorcode.ER_DUP_ENTRY:
            return ErrorResponse("广告%s已经存在！" % safe_vars["project_name"])
        raise

    return InfoResponse("广告修改成功！")
