#!/usr/bin/env python
#-*- coding:utf-8 -*-


import os
project_home = os.path.realpath(__file__)
project_home = os.path.split(project_home)[0]
project_home = os.path.split(project_home)[0]

import sys
initialized = (len(sys.path) > 0 and sys.path[0] == project_home)

#print "found initialized, do nothing!" if initialized else "doing initialization!"

if not initialized:
    sys.path.insert(0, project_home)

    from etc import config
    config.project_home = project_home
    config.db_conn_pool_size = (1, 1)

    # init conn
    from base import smartpool

    smartpool.coroutine_mode = True

    # log setting
    from base import logger, poolmysql

    logger.init_log([(n, os.path.join(config.project_home, "logs", p), l) \
        for n, p, l in config.log_config])

    if getattr(config, "pool_log", None) is not None:
        smartpool.pool_logger = logger.get(config.pool_log).info

    if getattr(config, "db_query_log", None) is not None:
        poolmysql.query_logger = logger.get(config.db_query_log).info

    # initialize template engine
    import jinja2
    from base.util import to_unicode, gen_uobj

    jinja_env = jinja2.Environment(**{
        "loader": jinja2.FileSystemLoader(os.path.join(project_home, "tools/templates"), config.encoding),
    })

    from base import tmp_filter
    jinja_env.filters.update(tmp_filter.mapping)

    def render_template(template_name, **context):
        udata = {}
        for k, v in context.iteritems():
            udata[to_unicode(k, config.encoding)] = gen_uobj(v, config.encoding)

        return jinja_env.get_template(template_name).render(udata).encode(config.encoding)
