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

from base.framework import *
from base.deco import *
from base.nform import *
from base.smartsql import *
from base.poolmysql import *


project = Blueprint("project", __name__)


@project.route("/project/list", methods=["GET"])
@general("project list")
def project_list():
    return TempResponse("project_list.html")
