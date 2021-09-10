import logging
import logging.handlers
import pathlib
import sys

def get_project_dir():
    home_dir = pathlib.Path.home()
    project_dir = home_dir.joinpath('.local/share/exposure-alert')
    return project_dir

def make_dir(dir_name):
    """Creates the directory if it doesn't exist.
    
    If the path is a file instead, raise an error.
    """
    project_dir = get_project_dir()
    dir_path = project_dir.joinpath(dir_name)
    try:
        dir_path.mkdir(parents=True)
    except:
        print((sys.exc_info()[0]))

def start_logs(log_name=__name__, backups=7):
    """Start logging."""
    logger_formatter = logging.Formatter('%(asctime)s %(module)s %(funcName)s %(levelname)s %(message)s')
    project_dir = get_project_dir()
    log_dir = project_dir.joinpath('logs')
    if not log_dir.is_dir():
        make_dir('logs')
    log_file = log_dir.joinpath(f'{log_name}.log')
    logger = logging.getLogger(log_name)
    logger.setLevel(logging.DEBUG)
    fhandler = logging.handlers.TimedRotatingFileHandler(log_file, when='midnight', backupCount=backups)
    fhandler.setFormatter(logger_formatter)
    logger.addHandler(fhandler)
    return logger
