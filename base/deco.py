#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import functools
import traceback
from datetime import datetime

import mysql.connector
from mysql.connector import errorcode

from flask import request, session, url_for

from base import constant as cfg
from etc import setting as sfg, config

from base import util, logic
from base import logger
from base.nform import FormChecker
from base.connection import db_reader, db_writer

from base.poolmysql import *
from base.smartsql import *
from base.framework import *


__all__ = [
    "general",
    "form_check",
    "admin_required",
]

def general(desc):
    def deco(old_handler):
        @functools.wraps(old_handler)
        def new_handler(*args, **kwargs):
            resp = old_handler(*args, **kwargs)

            if isinstance(resp, TempResponse):
                resp.context_default(**kwargs)

            if isinstance(resp, Response):
                return resp.output()
            return resp

        new_handler.desc = desc
        new_handler.is_handler = True
        return new_handler

    return deco


def form_check(settings, var_name="safe_vars", strict_error=True, error_handler=None, error_var="form_errors", encoding=None):
    if error_handler is None:
        error_handler = ErrorResponse

    def new_deco(old_handler):
        @functools.wraps(old_handler)
        def new_handler(*args, **kwargs):
            if encoding is not None:
                request.charset = encoding

            req_data = {}
            for k, v in settings.iteritems():
                if v.multiple:
                    req_data[k] = request.values.getlist(k)
                else:
                    req_data[k] = request.values.get(k, None)

            checker = FormChecker(req_data, settings, err_msg_encoding=config.encoding)
            if not checker.is_valid():
                if strict_error:
                    error_msg = [v for v in checker.get_error_messages().values() if v is not None]
                    return error_handler(error_msg)
                else:
                    kwargs[error_var] = checker.get_error_messages()
                    return old_handler(*args, **kwargs)

            valid_data = util.encode_unicode_json(checker.get_valid_data(), config.encoding)
            kwargs[var_name] = valid_data

            response = old_handler(*args, **kwargs)
            if isinstance(response, TempResponse):
                response.context_default(**{var_name: valid_data})

            return response
        return new_handler
    return new_deco


def admin_required(strict_login=True):
    def new_deco(old_handler):
        @functools.wraps(old_handler)
        def new_handler(*args, **kwargs):
            db = db_reader

            logined = False
            if session.get(cfg.SESSION.KEY_USERID) and session.get(cfg.SESSION.KEY_USERNAME):
                logined = True

            if not strict_login:
                kwargs.update({
                    "logined": logined,
                })
                return old_handler(*args, **kwargs)

            if not logined:
                return Redirect(url_for("admin.home_login_load"))

            resp = old_handler(*args, **kwargs)
            return resp
        return new_handler
    return new_deco
