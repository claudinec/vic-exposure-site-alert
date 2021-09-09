"""Utilities."""

import logging
import logging.handlers

def start_logs(log_name=__name__, backups=7):
    """Start logging."""
    logger_formatter = logging.Formatter('%(asctime)s %(module)s %(funcName)s %(levelname)s %(message)s')

    log_file = f'logs/{log_name}.log'
    logger = logging.getLogger(log_name)
    logger.setLevel(logging.DEBUG)
    fhandler = logging.handlers.TimedRotatingFileHandler(log_file, when='midnight', backupCount=backups)
    fhandler.setFormatter(logger_formatter)
    logger.addHandler(fhandler)
    return logger
