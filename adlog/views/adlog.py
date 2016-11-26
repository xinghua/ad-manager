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

from base.framework import client_ip, Redirect, Response404
from base.deco import *
from base.nform import *
from base.smartsql import *
from base.poolmysql import *


adlog = Blueprint("adlog", __name__)


def gen_unique_user_id():
    m = hashlib.md5()
    m.update(client_ip() or "") 
    m.update(str(time.time()))
    m.update(str(random.random()))
    return m.hexdigest()

def mark_unique_user_id(response):
    unique_user_id = request.cookies.get(cfg.SESSION.PROJECT_COOKIE_NAME)
    if unique_user_id is None:
        unique_user_id = gen_unique_user_id()
        response.set_cookie(
            cfg.SESSION.PROJECT_COOKIE_NAME,
            unique_user_id, 
            max_age=10*365*24*3600,
            expires=datetime.now()+timedelta(days=365*10)
        )

    response.set_header("P3P", 'CP="NOI DSP COR CURa ADMa DEVa PSAa PSDa OUR IND UNI PUR NAV"')
    return unique_user_id



##################### cgi handler #############################


@adlog.route("/click", methods=["GET"])
@general("click log")
@form_check({
    "project_id": F_int(u"project id") & "required" & "strict",
    "code_type": F_int(u"code type") & "required" & "strict",
    "s": F_str(u"sign") & "required" & "strict",
}, error_handler=\
    functools.partial(Response404))
def click(safe_vars):
    db = db_reader

    #if not util.check_sign(safe_vars["s"], safe_vars["project_id"], safe_vars["code_type"]):
    #    abort(404)

    project_info = QS(db).table(T.project).where(F.id == safe_vars["project_id"]).select_one()
    if project_info is None:
        abort(404)
    resp = Redirect(project_info["url"])
    unique_user_id = mark_unique_user_id(resp)

    util.log_record(
        util.get_daily_logger(sfg.DAILY_LOG.CLICK_LOG_PATH), 
        safe_vars["project_id"],
        unique_user_id,
        client_ip(),
        request.user_agent.string,
        request.args
    )

    return resp
