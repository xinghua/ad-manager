#!/usr/bin/env python
# -*- coding: utf-8 -*-

# let these at the very first line
from gevent import monkey
monkey.patch_all()
# let these at the very first line



import os
project_home = os.path.realpath(__file__)
project_home = os.path.split(project_home)[0]

import sys
sys.path.insert(0, project_home)

#import umysqldb
#umysqldb.install_as_MySQLdb()

# save project home
from etc import config
config.project_home = project_home

# init connections at first
from base import smartpool

smartpool.coroutine_mode = config.pool_coroutine_mode
import base.connection


#################
#  log setting  #
#################

from base import logger, poolmysql

logger.init_log([(n, os.path.join(config.project_home, "logs", p), l) \
    for n, p, l in config.log_config])

if getattr(config, "pool_log", None) is not None:
    smartpool.pool_logger = logger.get(config.pool_log).info

if getattr(config, "db_query_log", None) is not None:
    poolmysql.query_logger = logger.get(config.db_query_log).info


##################
#   flask basic  #
##################

from flask import Flask, request

app = Flask(__name__.split(".")[0])
app.config.update(config.flask_config)

# session
import redis
from base.session import RedisSessionInterface

app.session_interface = RedisSessionInterface(redis.StrictRedis(
    connection_pool=redis.ConnectionPool(
        max_connections=config.session_redis_max_connections, **config.session_redis_config
    )
))

# hook URL build errors
def external_url_handler(error, endpoint, values):
    return ""

app.url_build_error_handlers.append(external_url_handler)


##################
#     jinja2     #
##################

# do extension
app.jinja_env.add_extension('jinja2.ext.do')

# global var
from etc import setting as sfg
from base import constant as cfg
from base.util import gen_uobj

@app.context_processor
def global_jinja_var():
    return {
        u"cfg": gen_uobj(cfg),
        u"sfg": gen_uobj(sfg),
        u"config": gen_uobj(config),
    }

# reg filters
from base import tmp_filter
for name, func in tmp_filter.mapping.iteritems():
    app.template_filter(name)(func)


#################
#   exception   #
#################

import traceback
from base.util import text2html

@app.errorhandler(404)
def handle_404(error):
    return '404 Not Found', 404

def handle_exception(error):
    error_str = traceback.format_exc()
    logger.get("cgi-log").error(error_str)

    return '500 Internal Server Error', 500


###############
#   routing   #
###############

import views
for name in views.__all__:
    module = __import__("views.%s" % name, fromlist=[name])
    app.register_blueprint(getattr(module, name), url_prefix=config.app_path)


#############
#   debug   #
#############

from werkzeug.debug import DebuggedApplication

if config.debug:
    app.config["DEBUG"] = True
    app.wsgi_app = DebuggedApplication(app.wsgi_app, evalex=True)
else:
    app.errorhandler(500)(handle_exception)
    app.errorhandler(Exception)(handle_exception)
