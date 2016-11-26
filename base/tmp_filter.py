#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    custom filters for jinja2
"""

import time
import string
import urllib
import random
import datetime
import functools
import urlparse

import util
from etc import config
from base import logic
from connection import db_reader, db_writer


def _force_str(s):
    """
    convert s to <type 'str'>, if s is <type 'unicode'>
    """
    if isinstance(s, unicode):
        s = s.encode(config.encoding)
    return s


def format_datetime(value, format="%Y-%m-%d %H:%M:%S", default=""):
    if value is None:
        return default
    return value.strftime(_force_str(format))


def format_null(value, default=""):
    if value is None:
        return default
    return value


def format_ratio(value, precision=2, is_percent=False, default=""):
    if value is None:
        return default
    if is_percent:
        value = value * 100
    format = "%%.%df" % precision
    return format % value


def fen2yuan(value, default=""):
    if value is None:
        return default
    return "%.2f" % (int(value) / 100.0)


def point2yuan(value, default=""):
    if value is None:
        return default
    return "%.2f" % (int(value) / 10.0)


def inet_ntoa(value, default=""):
    if value is None:
        return default
    return util.safe_inet_ntoa(value)


def mktime(value):
    return time.mktime(value.timetuple())


def urlencode(value):
    if value is None:
        return None
    return urllib.quote(value)


def killcache(value, length):
    _id = ''.join(random.choice(string.lowercase) for i in range(length))
    if value.rfind("?") < 0:
        return "%s?_id=%s" % (value, _id)
    else:
        return "%s&_id=%s" % (value, _id)


def short_url(long_url, user_id=None):
    short_url = logic.get_short_url(
        db_writer, long_url.encode(config.encoding), user_id=user_id)

    return long_url if short_url is None else short_url.decode(config.encoding)


def urlsafe(words, plus=True):
    if plus:
        return urllib.quote_plus(words.encode(config.encoding)).decode(config.encoding)
    return urllib.quote(words.encode(config.encoding)).decode(config.encoding)


def jsafe(words):
    """
    防止js注入
    """
    return "".join(map(_jsesc, words))

def _jsesc(v):
    ascii_min, ascii_max = 33, 126 # ascii可见字符范围

    # 特别对 " ' < \ 转义，防止注入
    if ascii_min <= ord(v) <= ascii_max and v not in ["\"", "'", "<", "\\"]:
        return v

    return (r"\u%04X" % ord(v) if ord(v) > 0xFF else r"\x%02X" % ord(v))


def timedelta(base, d=0, h=0, m=0, s=0):
    return base + datetime.timedelta(days=d, hours=h, minutes=m, seconds=s)

def sliced(value, pieces, fill_with=None):
    n, m = divmod(len(value), pieces)

    if n < 1:
        pieces = m
        n = 1
        m = 0

    offset = 0
    for p in xrange(pieces):
        plen = n if m < 1 else n + 1
        yield value[offset:offset+plen]

        offset += plen
        m -= 1


def strip_tags(v):
    return util.strip_tags(v)


def mask_mobile(mobile):
    if mobile is None:
        return None

    return "".join([mobile[:3], "****", mobile[-4:]])


def mask_urs(urs):
    if urs is None:
        return None

    prefix = urs[:urs.find("@")]
    suffix = urs[urs.find("@"):]

    return "".join([prefix[:3], "****", prefix[-4:], suffix])


def url_split(url):
    result = urlparse.urlsplit(url)
    domain = "://".join([result.scheme, result.netloc])
    path = "?".join([result.path, result.query])
    return (domain, path)

# ###########  mapping ###########


mapping = {
    "fm_time": format_datetime,
    "fm_date": functools.partial(format_datetime, format="%Y-%m-%d"),
    "fm_null": format_null,
    "fm_ratio": format_ratio,
    "fen2yuan": fen2yuan,
    "point2yuan": point2yuan,
    "inet_ntoa": inet_ntoa,
    "mktime": mktime,
    "timedelta": timedelta,
    "urlencode": urlencode,
    "killcache": killcache,
    "short_url": short_url,
    "urlsafe": urlsafe,
    "jsafe": jsafe,
    "sliced": sliced,
    "strip_tags": strip_tags,
    "mask_mobile": mask_mobile,
    "mask_urs": mask_urs,
    "url_split": url_split
}
