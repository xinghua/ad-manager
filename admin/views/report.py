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
from base.get_data import get_data, widget_config


report = Blueprint("report", __name__)


def get_dim_dict(safe_vars):
    dim_dict = {}

    for k,v in sfg.REPORT.DIM_TYPES.items():
        if safe_vars.get(k) is not None:
            dim_dict[v] = safe_vars[k]

    return dim_dict


@report.route("/report/teset/load", methods=["GET"])
@general("report test load")
@admin_required()
def report_test_load():
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


@report.route("/report/test/query", methods=["GET"])
@general("report test query")
@admin_required()
@form_check({
    "beginDate": F_datetime(u"日期", format="%Y-%m-%d") & "strict" & "required",
    "game_id": F_int(u"game id") & "strict" & "required",
    "match_type": F_int(u"match_type") & "strict" & "optional",
    "channel_id": F_int(u"channel id") & "strict" & "optional",
    "media_id": F_int(u"media id") & "strict" & "optional",
    "project_id": F_int(u"project_id") & "strict" & "optional",
})
def report_test_query(safe_vars):
    db = db_reader

    begin_date = safe_vars["beginDate"].date()

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


@report.route("/report/<report_name>/load", methods=["GET"])
@general("report load")
@admin_required()
def report_load(report_name):
    db = db_reader

    games = util.dbresult2dict(QS(db).table(T.game).select(), "id", "name")
    channels = util.dbresult2dict(QS(db).table(T.channel).select(), "id", "name")
    medias = util.dbresult2dict(QS(db).table(T.media).select(), "id", "name")
    match_types = util.dbresult2dict(QS(db).table(T.dim_match_type).select(), "id", "name")

    return TempResponse("common_report.html",
        games = games,         
        channels = channels,
        medias = medias,
        match_types = match_types,
        report_name = report_name,
    )


@report.route("/report/<report_name>/query", methods=["GET"])
@general("report query")
@admin_required()
@form_check({
    "beginDate": F_datetime(u"开始日期", format="%Y-%m-%d") & "strict" & "required",
    "endDate": F_datetime(u"结束日期", format="%Y-%m-%d") & "strict" & "required",
    "game_id": F_int(u"game id") & "strict" & "required",
    "match_type": F_int(u"match_type") & "strict" & "optional",
    "channel_id": F_int(u"channel id") & "strict" & "optional",
    "media_id": F_int(u"media id") & "strict" & "optional",
    "project_id": F_int(u"project_id") & "strict" & "optional",
})
def report_query(safe_vars, report_name):
    db = db_reader

    begin_date, end_date = safe_vars["beginDate"].date(), safe_vars["endDate"].date()
    game_alias = "game%s" % safe_vars["game_id"]
    dim_dict = get_dim_dict(safe_vars)

    result = []
    for widget_id in sfg.REPORT.WIDGET_CONFIG[report_name]["widget"]:
        title, data = get_data(begin_date, end_date, game_alias, dim_dict, widget_id)
        #title, data = ["新增", "注册"], [[1,1], [2,2]]
        result.append({
            "name": widget_config[widget_id]["name"],
            "title": title,
            "data": data,
            "id": widget_id,
        })

    games = util.dbresult2dict(QS(db).table(T.game).select(), "id", "name")
    channels = util.dbresult2dict(QS(db).table(T.channel).select(), "id", "name")
    medias = util.dbresult2dict(QS(db).table(T.media).select(), "id", "name")
    match_types = util.dbresult2dict(QS(db).table(T.dim_match_type).select(), "id", "name")

    return TempResponse("common_report.html",
        games = games,         
        channels = channels,
        medias = medias,
        match_types = match_types,
        result = result,
    )


@report.route("/report/<int:table_id>/download", methods=["GET"])
@general("report query")
@admin_required()
@form_check({
    "beginDate": F_datetime(u"开始日期", format="%Y-%m-%d") & "strict" & "required",
    "endDate": F_datetime(u"结束日期", format="%Y-%m-%d") & "strict" & "required",
    "game_id": F_int(u"game id") & "strict" & "required",
    "match_type": F_int(u"match_type") & "strict" & "optional",
    "channel_id": F_int(u"channel id") & "strict" & "optional",
    "media_id": F_int(u"media id") & "strict" & "optional",
    "project_id": F_int(u"project_id") & "strict" & "optional",
})
def table_download(safe_vars, table_id):
    db = db_reader

    begin_date, end_date = safe_vars["beginDate"].date(), safe_vars["endDate"].date()
    game_alias = "game%s" % safe_vars["game_id"]
    dim_dict = get_dim_dict(safe_vars)

    title, data = get_data(begin_date, end_date, game_alias, dim_dict, table_id)
    file_name = "%s.txt" % widget_config[table_id]["name"]
    file_content = util.dump_data_as_txt(title, data)

    return DumpFileResponse(file_name, file_content)
