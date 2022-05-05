'''
Created on 25 Apr 2022

@author: jackisback
'''

import logging
import inspect


def log(msg, *args, **kwargs):
    logger = logging.getLogger()
    logger.info(_get_formatted_message(msg), *args, **kwargs)

def log_debug(msg, *args, **kwargs):
    logger = logging.getLogger()
    logger.debug(_get_formatted_message(msg), *args, **kwargs)
    
def log_info(msg, *args, **kwargs):
    logger = logging.getLogger()
    logger.info(_get_formatted_message(msg), *args, **kwargs)
    
def log_warn(msg, *args, **kwargs):
    logger = logging.getLogger()
    logger.warn(_get_formatted_message(msg), *args, **kwargs)
    
def log_error(msg, *args, **kwargs):
    logger = logging.getLogger()
    logger.error(_get_formatted_message(msg), *args, **kwargs)

#===============================================================================
# Adds the name of the caller class to the log message
#===============================================================================
def _get_formatted_message(msg):
    stack = inspect.stack()
    try:
        # stack[2] is the caller of the caller
        the_class = stack[2][0].f_locals["self"].__class__.__name__
    except Exception:
        the_class = "???"
    return "[{name}]> {msg}".format(name=the_class, msg=msg)