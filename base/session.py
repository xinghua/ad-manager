#!/usr/bin/env python
#-*- coding:utf-8 -*-


import os
import string
import pickle
from datetime import timedelta
from uuid import uuid4

from redis import Redis
from werkzeug.datastructures import CallbackDict
from flask.sessions import SessionInterface, SessionMixin


def total_seconds(td):
    return td.days * 60 * 60 * 24 + td.seconds


class RedisSession(CallbackDict, SessionMixin):
    def __init__(self, initial=None, sid=None, new=False):
        def on_update(self):
            self.modified = True
        CallbackDict.__init__(self, initial, on_update)
        self.sid = sid
        self.new = new
        self.modified = False


class RedisSessionInterface(SessionInterface):
    serializer = pickle
    session_class = RedisSession

    def __init__(self, redis=None, prefix='session:'):
        if redis is None:
            redis = Redis()

        self.redis = redis
        self.prefix = prefix

    def _del_cookie_on_domain_or_list(self, response, name, domain_or_list):
        if isinstance(domain_or_list, list):
            for one in domain_or_list:
                response.delete_cookie(name, domain=one)
            return

        response.delete_cookie(name, domain=domain_or_list)

    def _set_cookie_on_domain_or_list(self, response, name, value, domain_or_list, **kwargs):
        if isinstance(domain_or_list, list):
            for one in domain_or_list:
                response.set_cookie(name, value, domain=one, **kwargs)
            return

        response.set_cookie(name, value, domain=domain_or_list, **kwargs)

    def generate_sid(self):
        #return str(uuid4())
        chars = string.letters + string.digits + "_-"
        return "".join([chars[ord(i) % len(chars)] for i in os.urandom(40)])

    def get_redis_expiration_time(self, app, session):
        if session.permanent:
            return app.permanent_session_lifetime
        return timedelta(hours=1)

    def open_session(self, app, request):
        sid = request.cookies.get(app.session_cookie_name)
        if not sid:
            sid = self.generate_sid()
            return self.session_class(sid=sid, new=True)
        val = self.redis.get(self.prefix + sid)
        if val is not None:
            data = self.serializer.loads(val)
            return self.session_class(data, sid=sid)
        return self.session_class(sid=sid, new=True)

    def save_session(self, app, session, response):
        domain = self.get_cookie_domain(app)
        if not session:
            self.redis.delete(self.prefix + session.sid)
            if session.modified:
                self._del_cookie_on_domain_or_list(response, app.session_cookie_name, domain)
            return

        redis_exp = self.get_redis_expiration_time(app, session)
        if isinstance(redis_exp, timedelta):
            redis_exp = total_seconds(redis_exp)

        val = self.serializer.dumps(dict(session))
        self.redis.setex(self.prefix + session.sid, redis_exp, val)

        httponly = self.get_cookie_httponly(app)
        cookie_exp = self.get_expiration_time(app, session)

        self._set_cookie_on_domain_or_list(
            response, app.session_cookie_name, session.sid, domain,
            expires=cookie_exp, httponly=httponly)
