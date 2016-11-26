#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
from time import time
from contextlib import contextmanager
import simplejson
import uuid

import flask
from flask import Flask, make_response
from flask import request, redirect, url_for

from jinja2 import FileSystemLoader, BytecodeCache

from base import smartpool
from base import constant as cfg
from base.connection import *
from base.util import to_unicode, gen_uobj, url_query_update
from base.util import safe_json_dumps, url_append
from etc import config
from etc import setting as sfg


__all__ = [
    "is_xhr",
    "client_ip",
    "render_template",
    "render_template_string",

    "Response",
    "TempResponse",
    "JsonResponse",
    "InfoResponse",
    "ErrorResponse",
    "Redirect",
    "JsonInterfaceResponse",
    "DumpFileResponse",
    "InterfaceResponse",
    "ImageFileResponse"
]


def client_ip():
    return request.access_route[0]

def render_template(name, **data):
    udata = {}
    for k, v in data.iteritems():
        udata[to_unicode(k, config.encoding)] = gen_uobj(v, config.encoding)

    return flask.render_template(name, **udata).encode(config.encoding)

def render_template_string(template, **data):
    utemplate = template
    if not isinstance(utemplate, unicode):
        utemplate = template.decode(config.encoding)

    udata = {}
    for k, v in data.iteritems():
        udata[to_unicode(k, config.encoding)] = gen_uobj(v, config.encoding)

    return flask.render_template_string(utemplate, **udata).encode(config.encoding)

def is_xhr():
    return request.is_xhr or request.values.get("_xhr") is not None

#############  response obj #############



class Response(object):
    def __init__(self):
        self._ext_header = {}
        self._set_cookie_params = []
        self._del_cookie_params = []

    def set_header(self, key, value):
        self._ext_header[key] = value

    def set_cookie(self, *args, **kwargs):
        """
        valid params and defaults:
            key, value='', max_age=None, expires=None,
            path='/', domain=None, secure=None, httponly=False
        """
        self._set_cookie_params.append((args, kwargs))

    def delete_cookie(self, *args, **kwargs):
        """
        valid params and defaults:
            key, path='/', domain=None
        """
        self._del_cookie_params.append((args, kwargs))

    def output(self):
        resp = make_response(self._output())
        for k, v in self._ext_header.iteritems():
            resp.headers[k] = v

        for args, kwargs in self._set_cookie_params:
            resp.set_cookie(*args, **kwargs)

        for args, kwargs in self._del_cookie_params:
            resp.delete_cookie(*args, **kwargs)

        return resp

    def _output(self):
        return "", 404


class TempResponse(Response):
    def __init__(self, template_name, **context):
        Response.__init__(self)
        self._template_name = template_name
        self._context = context

    def context_update(self, **kwargs):
        self._context.update(kwargs)
        return self

    def context_default(self, **kwargs):
        for k, v in kwargs.iteritems():
            self._context.setdefault(k, v)
        return self

    def _output(self):
        self.set_header("Content-Type", "text/html")
        return render_template(self._template_name, **self._context)


class JsonResponse(Response):
    def __init__(self, data=None):
        Response.__init__(self)
        self._json = {} if data is None else {"data": data}

    def _output(self):
        self.set_header("Content-Type", "application/json")
        return safe_json_dumps(self._json)


class InfoResponse(TempResponse, JsonResponse):
    __output_pat__ = "info.html"
    __output_var__ = "info"

    def __init__(self, msg, url=None, top=False, extra=None):
        TempResponse.__init__(self, self.__output_pat__)
        JsonResponse.__init__(self)

        resp = { self.__output_var__: msg, "top": top }
        if url is not None:
            resp["url"] = url

        if extra is not None:
            resp["extra"] = extra

        self._json = resp
        self._context = resp.copy()

    def _output(self):
        TEMP_TIME = 600

        if is_xhr():
            return JsonResponse._output(self)

        if request.method == "POST":
            try:
                redirect_id = uuid.uuid4().hex
                db_redis.setex("temp_resp_%s" % redirect_id, TEMP_TIME, simplejson.dumps(self._json))
                redirect_url = url_query_update(url_for("common.redirect_render"), {
                    "redirect_id": redirect_id,
                    "pat": self.__output_pat__
                })
                return redirect(redirect_url, 302)
            except:
                pass

        return TempResponse._output(self)


class ErrorResponse(InfoResponse):
    __output_pat__ = "error.html"
    __output_var__ = "error"


class Response404(Response):
    def __init__(self, msg=None):
        Response.__init__(self)
        self._code = 404


class Redirect(JsonResponse):
    def __init__(self, url, code=302):
        JsonResponse.__init__(self)

        self._url = url
        self._code = code

    def _output(self):
        if request.cookies.get("_shopuuyd_") is not None:
            x = int(time())
            self._url = url_append(self._url, _x=x)

        if is_xhr():
            self._json = { "url": self._url }
            return JsonResponse._output(self)

        return redirect(self._url, self._code)


class JsonInterfaceResponse(JsonResponse):
    def __init__(self, code, msg=None, **kwargs):
        super(JsonInterfaceResponse, self).__init__()
        self._json = {"code": code}
        if msg is not None:
            self._json.update({"msg": msg})
        self._json.update(kwargs)


class DumpFileResponse(Response):
    def __init__(self, file_name, content, encoding=config.encoding):
        super(DumpFileResponse, self).__init__()
        self._file_name = file_name
        self._content = content
        self._encoding = encoding

    def _output(self):
        self.set_header("Content-Type", "application/octet-stream")
        self.set_header("Content-Disposition", "attachment; filename=%s" % (self._file_name,))
        self.set_header("Content-Length", str(len(self._content)))
        return self._content


class InterfaceResponse(Response):
    """
    A wrapper for output response of general response.
    """
    def __init__(self, data_lines, code, code_only=False, code_desc=None):
        """
        Initialization.

        @param data_lines: a list of lines, will be outputed after return code.
        @param code: return code will be in first line.
        @param code_only: if True, only output code and ignore data_lines.
        @param code_desc: str, describe the code, as second line if given.
        """
        super(InterfaceResponse, self).__init__()
        self._lines = data_lines
        self._code = code
        self._code_only = code_only
        self._code_desc = code_desc
        self.set_header("content-type", "text/plain")


    def _output(self):
        result = str(self._code)
        if self._code_desc is not None:
            result = "%s\n%s" % (result, self._code_desc)

        if not self._code_only and len(self._lines) > 0:
            result += ("\n" + "\n".join(map(str, self._lines)))

        return result


class ImageFileResponse(Response):
    def __init__(self, content):
        super(ImageFileResponse, self).__init__()

        self.set_header("content-type", "image/jpeg")
        self.set_header("content-length", str(len(content)))

        self._content = content

    def _output(self):
        return self._content


class RedisTemplateBytecodeCache(BytecodeCache):
    CACHE_TTL = 600

    def __init__(self, redis_client):
        self.client = redis_client

    def key(self, k):
        return '%s_%s' % ("jinjia_temp", k)

    def load_bytecode(self, bucket):
        bc = self.client.get(self.key(bucket.key))
        if bc:
            bucket.bytecode_from_string(bc)

    def dump_bytecode(self, bucket):
        self.client.setex(
            self.key(bucket.key),
            RedisTemplateBytecodeCache.CACHE_TTL,
            bucket.bytecode_to_string()
        )

    def clear(self):
        pass
