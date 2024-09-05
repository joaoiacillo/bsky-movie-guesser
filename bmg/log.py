""" log.py

    Logging is really important, specially for a bmg that keeps on running
    without anyone looking at the console. This file contains methods for
    easily handling with log outputs in the console, and in files.

    I recommend using files, rather than console print, since you'll be able
    to retrieve information from older runtimes.
    
    Author: João Iacillo <john@iacillo.dev.br>
"""

import logging
import sys

from datetime import datetime
from os import path, mkdir
from .consts import ROOT_DIR


def open_log_file():
    now = int(round(datetime.now().timestamp()))
    logs_dir_path = path.join(ROOT_DIR, '.logs')
    if not path.exists(logs_dir_path):
        mkdir(logs_dir_path)
    return open(path.join(logs_dir_path, f'{now}.log'), 'w+')


def create_default_logger(is_debug: bool = False):
    logger = logging.getLogger('bsky.bmg')
    logger.setLevel(logging.DEBUG if is_debug else logging.INFO)

    handler = logging.StreamHandler(sys.stdout if is_debug else open_log_file())
    formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(module)s: %(message)s')

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
