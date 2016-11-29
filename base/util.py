#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    common utilities
"""

import cPickle as pickle
import os
import socket
import urllib
import urlparse
import struct
import logging
from datetime import datetime, date, timedelta
import errno
import hashlib
import hmac
import base64

from etc import config
from etc import setting as sfg
from base import constant as cfg


def encode_unicode_json(obj, encoding=config.encoding):
    """
    for simplejson loads, it return a obj which all str is unicode, encode it to our encoding
    """

    if isinstance(obj, unicode):
        return obj.encode(encoding)
    elif isinstance(obj, (list, tuple)):
        return [encode_unicode_json(v) for v in obj]
    elif isinstance(obj, dict):
        return dict([(encode_unicode_json(k), encode_unicode_json(v)) for k, v in obj.iteritems()])

    return obj


class Serializer(object):
    """
    A tool for serialize/unserialize object
    """
    @classmethod
    def to_string(cls, obj):
        """
        Serialize a object into string

        >>> from base.util import Serializer
        >>>
        >>> obj = object()
        >>> obj_str = Serializer.to_string(obj)
        """
        return pickle.dumps(obj)

    @classmethod
    def to_object(cls, string):
        """
        Unserialize a string into object

        >>> from base.util import Serializer
        >>>
        >>> obj_str = "xxxxxx"
        >>> obj = Serializer.to_object(obj_string)
        """
        return pickle.loads(string)


class FileLock(object):
    def __init__(self, file_name, path):
        self._file = os.path.join(path, file_name)
        self._fd = None
        self._locked = False

    def lock(self):
        if self._locked:
            return True

        fd = open(self._file, 'a+b')
        try:
            fcntl.flock(fd.fileno(), fcntl.LOCK_NB | fcntl.LOCK_EX)
        except IOError:
            fd.close()
            return False

        self._fd = fd
        self._locked = True
        return True

    def release(self):
        if self._locked:
            fcntl.flock(self._fd.fileno(), fcntl.LOCK_UN)
            self._fd.close()
            self._fd = None
            self._locked = False

    def get_data(self):
        if not self._locked:
            return None

        self._fd.seek(0)
        data = self._fd.read()
        if len(data) < 1:
            return None

        return Serializer.to_object(data)

    def set_data(self, data):
        if not self._locked:
            return

        self._fd.truncate(0)
        self._fd.write(Serializer.to_string(data))
        self._fd.flush()

    def __del__(self):
        self.release()


def text2html(text):
    return '<p>%s</p>' % (text.replace('\r', '')
                          .replace('\n\n', '</p><p>')
                          .replace('\n', '<br/>')
                          .replace(' ', '&nbsp;'))


def to_unicode(data, encoding="utf-8"):
    """convert data from some encoding to unicode
    data could be string, list, tuple or dict
    that contains string as key or value
    """
    if data is None:
        return unicode('')

    if isinstance(data, unicode):
        return data

    if isinstance(data, (list, tuple)):
        u_data = []
        for item in data:
            u_data.append(to_unicode(item, encoding))

    elif isinstance(data, dict):
        u_data = {}
        for key in data:
            u_data[to_unicode(key, encoding)] = to_unicode(data[key], encoding)

    elif isinstance(data, str):
        u_data = unicode(data, encoding, 'ignore')
    else:
        u_data = data

    return unicode(u_data)


class UObj:
    #do not gen UObj when input obj type is in base_types
    base_types = (
        bool, float, int, long, complex, unicode,
    )
    #do not gen UObj when attr name in raw_attrs
    raw_attrs = (
        '__name__', '__coerce__',
    )
    #gen UObj with fake rop when input obj doesn't have the attr and
    #attr is in rops
    rops = (
        '__radd__', '__rdiv__', '__rmod__', '__rmul__', '__rsub__',
        '__rand__', '__rlshift__', '__ror__', '__rrshift__', '__rxor__',
        '__rdivmod__', '__rpow__',
    )

    def __init__(self, obj, encoding, fake_rop):
        self._obj = obj
        self._encoding = encoding
        self._fake_rop = fake_rop

    @classmethod
    def _gen_rop_name(self, name):
        """
        gen fake rop name, just removing the first 'r' in original name
        """
        return name.replace('r', '', 1)

    @classmethod
    def _cvt_arg(self, arg):
        """
        single argument conversion, return internal obj if arg is an UObj instance
        """
        if isinstance(arg, UObj):
            return arg._obj
        return arg

    @classmethod
    def _cvt_args(self, *args):
        """
        sequence argument conversion
        """
        return [UObj._cvt_arg(a) for a in args]

    @classmethod
    def _cvt_kwargs(self, **kwargs):
        """
        keyword argument conversion
        """
        new_kwargs = {}
        for key, value in kwargs.iteritems():
            new_kwargs[UObj._cvt_arg(key)] = UObj._cvt_arg(value)
        return new_kwargs

    def __eq__(self, other):
        return self.__cmp__(other) == 0

    def __ne__(self, other):
        return self.__cmp__(other) != 0

    def __lt__(self, other):
        return self.__cmp__(other) < 0

    def __gt__(self, other):
        return self.__cmp__(other) > 0

    def __le__(self, other):
        return self.__cmp__(other) <= 0

    def __ge__(self, other):
        return self.__cmp__(other) >= 0

    def __cmp__(self, other):
        other = UObj._cvt_arg(other)
        if self._obj == other:
            return 0
        elif self._obj > other:
            return 1
        else:
            return -1

    def __unicode__(self):
        return to_unicode(self._obj, self._encoding)

    def __getattr__(self, name):
        fake_rop = False
        if (not hasattr(self._obj, name)) and (name in UObj.rops):
            new_name = UObj._gen_rop_name(name)
            if hasattr(self._obj, new_name):
                name = new_name
                fake_rop = True
        attr = getattr(self._obj, name)
        if name in UObj.raw_attrs:
            return attr
        return gen_uobj(attr, self._encoding, fake_rop)

    def __call__(self, *args, **kwargs):
        if self._fake_rop:
            return gen_uobj(getattr(args[0], self.__name__)(self._obj.__self__), self._encoding)
        return gen_uobj(self._obj(*(UObj._cvt_args(*args)), **(UObj._cvt_kwargs(**kwargs))),
                        self._encoding)

    def origin(self):
        return self._obj


def gen_uobj(obj, encoding="utf-8", fake_rop=False):
    if isinstance(obj, str):
        return obj.decode(encoding, 'ignore')

    if not obj or isinstance(obj, UObj.base_types):
        return obj

    return UObj(obj, encoding, fake_rop)


def safe_json_default(obj):
    if isinstance(obj, datetime):
        return obj.strftime("%Y-%m-%d %H:%M:%S")
    elif isinstance(obj, date):
        return obj.strftime("%Y-%m-%d")
    elif isinstance(obj, Decimal):
        return float(obj)

    return str(obj)


def safe_json_dumps(obj, encoding=None, silent=True):
    """
    Encode a Python object to JSON formatted string.

    @params object: Python object
    @params encoding: the character encoding for str instances, default is UTF-8.
    @params silent: not raise error, default is True

    @return: a JSON formatted string if dumps success or None

    """
    kwargs = {"default": safe_json_default}
    if encoding is not None:
        kwargs["encoding"] = encoding

    try:
        str = json.dumps(obj, **kwargs)
    except (ValueError, TypeError):
        if silent:
             return None
        raise

    return str


def safe_json_loads(str, encoding=None, silent=True):
    """
    Decode JSON formatted string to a Python object. Can not decode 'null'.

    @params str:  a JSON formatted string
    @params encoding: the character encoding for str instances, default is UTF-8.
    @params silent: not raise error, default is True

    @return: a Python object if loads success or None
    """
    kwargs = {}
    if encoding is not None:
        kwargs["encoding"] = encoding
    try:
        obj = json.loads(str, **kwargs)
    except (ValueError, TypeError):
        if silent:
            return None
        raise

    return obj

def gen_md5(text, salt=None):
    obj = hashlib.md5()
    obj.update(text)
    if salt is not None:
        obj.update(str(salt))

    return obj.hexdigest()


def safe_inet_ntoa(n):
    """
    Convert numerical ip to string ip(like: 2071801890 -> "123.125.48.34"), 
    return None if failed.
    """
    try:
        ip = socket.inet_ntoa(struct.pack(">L", n))
    except (struct.error, socket.error):
        return None

    return ip


def safe_inet_aton(ip):
    """
    Convert string ip to numerical ip(like: "123.125.48.34" -> 2071801890), 
    return None if failed.
    """
    try:
        n = struct.unpack(">L", socket.inet_pton(socket.AF_INET, ip))[0]
    except (struct.error, socket.error):
        return None

    return n


def url_query_update(url, update_query):
    """
    Use update_query update query string of url

    >>> from base.util import url_query_update
    >>>
    >>> url = "http://xxxx?a=aa&b=bb#fragment"
    >>> update_query = {"a": "ab", "rid": "xvfg"}
    >>> updated_url = url_query_update(url, update_query)
    >>> updated_url
    'http://xxxx?a=ab&rid=xvfg&b=bb#fragment'
    """
    scheme, netloc, path, query_string, fragment = urlparse.urlsplit(url)
    query = urlparse.parse_qs(query_string)
    query.update(update_query)
    updated_query_string = urllib.urlencode(query, True)
    return urlparse.urlunsplit((scheme, netloc, path, updated_query_string, fragment))


def url_join(url, paras):
    """
    Join a url and paras string. like:
      url_join("http://xxx/a.py?a=1", "b=2") -> 'http://xxx/a.py?a=1&b=2'
      url_join("http://xxx/a.py", "b=2") -> 'http://xxx/a.py?b=2'
    """
    sep = "?" if urllib.splitquery(url)[1] is None else "&"
    return url + sep + paras


def url_append(url, nodup=True, **kwargs):
    old_params = urlparse.urlparse(url)[4]
    if nodup and old_params:
        buf = urlparse.parse_qs(old_params)
        for k in buf:
            if kwargs.has_key(k):
                kwargs.pop(k)

    if len(kwargs) < 1:
        return url

    params = urllib.urlencode(kwargs)
    if old_params:
        return url + "&" + params
    else:
        return url + "?" + params


def log_format(arg):
    output = "-"

    if isinstance(arg, datetime):
        output = arg.strftime("%Y-%m-%d %H:%M:%S")
    elif isinstance(arg, date):
        output = arg.strftime("%Y-%m-%d")
    elif arg is None:
        output = "-"
    else:
        output = str(arg)

    return output.strip().replace("\n", "")


def log_record(logger, project_id, unique_user_id, client_ip, user_agent, request_args):
    field_list = []
    field_list.append("project_id=%s" % log_format(project_id))
    field_list.append("user_cookie=%s" % log_format(unique_user_id))
    field_list.append("client_ip=%s" % log_format(client_ip))
    field_list.append("user_agent=%s" % log_format(user_agent))
    field_list.append("datetime=%s" % log_format(datetime.now()))

    for k, v in request_args.items():
        if k == "project_id" or k == "code_type" or k == "s":
            continue

        if len(v) == 0:
            continue

        field_list.append("%s=%s" % (k, log_format(v[0])))

    logger.info("\t".join(field_list))


def get_daily_logger(parent_path):
    local_addr = socket.gethostbyname(socket.gethostname())
    log_path = os.path.join(parent_path, "%s/%s.log" % \
            (date.today().strftime("%Y%m%d"), local_addr))

    logger = logging.getLogger(log_path)
    if len(logger.handlers) > 0:
        return logger

    try:
        os.mkdir(os.path.dirname(log_path))
    except OSError, ex:
        if ex.errno != errno.EEXIST:
            raise

    handler = logging.FileHandler(log_path, "a")
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    return logger


def gen_sign_by_hmac(secret_key, data):
    """
    Generate signature by HMAC-SHA1.
    (from: http://www.ietf.org/rfc/rfc2104.txt)
    """
    digest = hmac.new(secret_key, data, hashlib.sha1).digest()
    return base64.standard_b64encode(digest)


def gen_sign(*args):
    data = [str(k) for k in args]
    data.append(sfg.SIGN.DATA_RID)
    return gen_sign_by_hmac(sfg.SIGN.KEY, "\n".join(data))


def check_sign(sign, *args):
    return sign == gen_sign(*args)


def get_fuzzy_search_str(s):
    WILDCARD = "%"
    s = s.replace('\\', r'\\')
    s = s.replace(r'_', r'\_')
    s = s.replace(r'%', r'\%')
    return WILDCARD + s + WILDCARD


def dbresult2dict(dbresult, key, value=None):
    if not isinstance(key, (list, tuple)):
        if value is not None:
            return dict(
                [(k[key], k[value]) for k in dbresult])
        else:
            return dict(
                [(k[key], k) for k in dbresult])
    else:
        if value is not None:
            return dict(
                [(tuple(k[i] for i in key), k[value]) for k in dbresult])
        else:
            return dict(
                [(tuple(k[i] for i in key), k) for k in dbresult])
