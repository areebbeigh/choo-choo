import os
import sys
import logging

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, 'logs')

if not os.path.isdir(LOG_DIR):
    os.mkdir(LOG_DIR)

def get_logger(name, level=logging.DEBUG, console=True):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    fhandler = logging.FileHandler(os.path.join(LOG_DIR, name + '.log'))
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fhandler.setFormatter(formatter)
    fhandler.setLevel(level)
    logger.addHandler(fhandler)
    if console:
        chandler = logging.StreamHandler(stream=sys.stdout)
        chandler.setFormatter(formatter)
        chandler.setLevel(level)
        logger.addHandler(chandler)
    return logger