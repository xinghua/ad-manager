#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging


_log_config = [
    ['', '', 'debug'],
    ['error-log', '', 'debug'],
]

def init_log(log_config=None):
    formater = logging.Formatter('%(name)-12s %(asctime)s %(levelname)-8s %(message)s',
        '%a, %d %b %Y %H:%M:%S',)

    """
    logging.basicConfig(level=logging.DEBUG,
        format='%(name)-12s %(asctime)s %(levelname)-8s %(message)s',
        datefmt='%a, %d %b %Y %H:%M:%S',
        filename=log_file,
        filemode='a')
    """

    if not log_config:
        log_config = _log_config

    for log in log_config:
        logger = logging.getLogger(log[0])
        if log[1]:
            handler = logging.FileHandler(log[1], 'a')
        else:
            import sys
            handler = logging.StreamHandler(sys.stderr)

        handler.setFormatter(formater)
        logger.addHandler(handler)
        logger.setLevel(getattr(logging, log[2].upper()))
        logger.propagate = False


def get(log_name=''):
    return logging.getLogger(log_name)


def test():
    init_log(_log_config)
    logger1 = logging.getLogger('debug.logger')
    logger2= logging.getLogger('debug.logger2')

    logging.debug('test')
    logging.error('test-error')
    logger1.info('test2')

    logger2.error('test2')

if __name__ == "__main__":
    test()

