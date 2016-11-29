#!/usr/bin/env python
# -*- coding:utf8 -*-
import redis
from werkzeug.local import LocalProxy
import MySQLdb

from etc import config
from base import poolmysql, smartpool

from base.smartsql import *


# #### init mysql using smartpool ######


# from file config
for name, setting in config.db_config.iteritems():
    smartpool.init_pool(
        name, setting, poolmysql.MySQLdbConnection, *config.db_conn_pool_size,
        maxidle=config.db_connection_idle, clean_interval=config.db_pool_clean_interval
    )

db_reader = smartpool.ConnectionProxy("db_reader")
db_writer = smartpool.ConnectionProxy("db_writer")

# #####  init redis  ########

db_redis = redis.StrictRedis(
    connection_pool=redis.ConnectionPool(
        max_connections=config.redis_max_connections, **config.redis_config
    )
)

def get_cursor():
    cursor = MySQLdb.connect(**config.db_config["db_writer"]).cursor()
    cursor.execute("set @@autocommit=1")
    return cursor
