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


report = Blueprint("report", __name__)


@report.route("/report/1/load", methods=["GET"])
@general("report1 load")
def report_1_load():
    db = db_reader

    games = util.dbresult2dict(QS(db).table(T.game).select(), "id", "name")
    channels = util.dbresult2dict(QS(db).table(T.channel).select(), "id", "name")
    medias = util.dbresult2dict(QS(db).table(T.media).select(), "id", "name")
    match_types = util.dbresult2dict(QS(db).table(T.dim_match_type).select(), "id", "name")

    return TempResponse("report_1.html",
        games = games,         
        channels = channels,
        medias = medias,
        match_types = match_types,
    )


@report.route("/report/1/query", methods=["GET"])
@general("report1 query")
@form_check({
    "beginDate": F_datetime(u"begin date", format="%Y-%m-%d") & "strict" & "required",
    "game_id": F_int(u"game id") & "strict" & "required",
    "match_type": F_int(u"match_type") & "strict" & "optional",
    "channel_id": F_int(u"channel id") & "strict" & "optional",
    "media_id": F_int(u"media id") & "strict" & "optional",
    "project_id": F_int(u"project_id") & "strict" & "optional",
})
def report_1_query(safe_vars):
    db = db_reader

    games = util.dbresult2dict(QS(db).table(T.game).select(), "id", "name")
    channels = util.dbresult2dict(QS(db).table(T.channel).select(), "id", "name")
    medias = util.dbresult2dict(QS(db).table(T.media).select(), "id", "name")
    match_types = util.dbresult2dict(QS(db).table(T.dim_match_type).select(), "id", "name")
    result = []

    return TempResponse("report_1.html",
        games = games,         
        channels = channels,
        medias = medias,
        match_types = match_types,
        result = result,
    )


@report.route("/report/2/load", methods=["GET"])
@general("report2 load")
def report_2_load():
    db = db_reader

    games = util.dbresult2dict(QS(db).table(T.game).select(), "id", "name")
    channels = util.dbresult2dict(QS(db).table(T.channel).select(), "id", "name")
    medias = util.dbresult2dict(QS(db).table(T.media).select(), "id", "name")
    match_types = util.dbresult2dict(QS(db).table(T.dim_match_type).select(), "id", "name")

    return TempResponse("report_2.html",
        games = games,         
        channels = channels,
        medias = medias,
        match_types = match_types,
    )


@report.route("/report/2/query", methods=["GET"])
@general("report1 query")
@form_check({
    "beginDate": F_datetime(u"begin date", format="%Y-%m-%d") & "strict" & "required",
    "endDate": F_datetime(u"end date", format="%Y-%m-%d") & "strict" & "required",
    "game_id": F_int(u"game id") & "strict" & "required",
    "match_type": F_int(u"match_type") & "strict" & "optional",
    "channel_id": F_int(u"channel id") & "strict" & "optional",
    "media_id": F_int(u"media id") & "strict" & "optional",
    "project_id": F_int(u"project_id") & "strict" & "optional",
})
def report_2_query(safe_vars):
    db = db_reader

    games = util.dbresult2dict(QS(db).table(T.game).select(), "id", "name")
    channels = util.dbresult2dict(QS(db).table(T.channel).select(), "id", "name")
    medias = util.dbresult2dict(QS(db).table(T.media).select(), "id", "name")
    match_types = util.dbresult2dict(QS(db).table(T.dim_match_type).select(), "id", "name")
    result = []

    return TempResponse("report_2.html",
        games = games,         
        channels = channels,
        medias = medias,
        match_types = match_types,
        result = result,
    )
