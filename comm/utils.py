# -*- coding: utf-8 -*-

import re
import os
import sys
import time
import platform
import traceback
import logging
from logging.handlers import RotatingFileHandler


COLOR_CODE = {
    "reset":        "\x1b[0m",
    "bold":         "\x1b[01m",
    "teal":         "\x1b[36;06m",
    "turquoise":    "\x1b[36;01m",
    "fuscia":       "\x1b[35;01m",
    "purple":       "\x1b[35;06m",
    "blue":         "\x1b[34;01m",
    "darkblue":     "\x1b[34;06m",
    "green":        "\x1b[32;01m",
    "darkgreen":    "\x1b[32;06m",
    "yellow":       "\x1b[33;01m",
    "brown":        "\x1b[33;06m",
    "red":          "\x1b[31;01m",
}


class ProjectUtil:
    """
    Utilities for crawlers
    """
    data_dir = None
    log_dir = None
    logger_dict = {}
    patt_digit = re.compile(r'\d+\.?\d*')

    def __init__(self, name):
        self.name = name

    @classmethod
    def get_first_digit(cls, data, default=0):
        digs = re.findall(r'\d+\.?\d*', data)
        if len(digs) > 0:
            return int(digs[0])
        else:
            return default

    @classmethod
    def get_project_data_dir(cls):
        if cls.data_dir is None:
            try:
                # static file save dir
                temp_path = os.path.dirname(os.path.abspath(__file__))
                temp_path = os.path.dirname(temp_path)
                cls.data_dir = os.path.join(temp_path, 'data')
                if not os.path.exists(cls.data_dir):
                    os.mkdir(cls.data_dir)
            except:
                tprint_error("Failed to init data_dir")
                tprint_error(traceback.format_exc())
                sys.exit(1)
            return cls.data_dir
        else:
            return cls.data_dir

    @classmethod
    def get_project_log_dir(cls):
        if cls.log_dir is None:
            try:
                # static file save dir
                temp_path = os.path.dirname(os.path.abspath(__file__))
                temp_path = os.path.dirname(temp_path)
                cls.log_dir = os.path.join(temp_path, 'log')
                if not os.path.exists(cls.log_dir):
                    os.mkdir(cls.log_dir)
            except:
                tprint_error("Failed to init log_dir")
                tprint_error(traceback.format_exc())
                sys.exit(1)
            return cls.log_dir
        else:
            return cls.log_dir

    @classmethod
    def get_project_logger(cls, name='base'):
        logger_name = name
        logfile = '{name}.log'.format(name=name)
        if name in cls.logger_dict:
            return cls.logger_dict[name]
        else:
            try:
                log_path = os.path.join(cls.get_project_log_dir(),
                                        logfile)
                fh = RotatingFileHandler(log_path,
                                         maxBytes=100*1024*1024,
                                         backupCount=20)
                fh.setLevel(logging.INFO)
                formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                fh.setFormatter(formatter)
                my_logger = logging.getLogger(logger_name)
                my_logger.addHandler(fh)
                my_logger.setLevel('INFO')
                # crawler_logger.info('logger init successful!')
                cls.logger_dict[name] = my_logger
            except:
                tprint_error("Failed to init logger")
                tprint_error(traceback.format_exc())
                sys.exit(1)
            return my_logger


def check_contain_chinese(check_str):
    for ch in check_str:
        if u'\u4e00' <= ch <= u'\u9fff':
            return True
    return False


# Utility to detect OS type
def is_windows_os():
    try:
        if platform.system() == 'Windows':
            return True
        else:
            return False
    except:
        print('[ERROR] Exception in Utils::is_windows_os()')
        return False


# cprint utility with color support
def cprint(msg, newline=True, log_fd=None, color=None, flush=False):
    try:
        if (not is_windows_os()) and os.isatty(2) and color:
            sys.stdout.write(color)
        if newline:
            print(msg)
        else:
            print (msg)
        if flush or not newline:
            sys.stdout.flush()

        if log_fd:
            log_fd.write(msg)
            if newline:
                log_fd.write('\n')
            log_fd.flush()
    except:
        print('[ERROR] Exception in Utils::cprint()')


# cprint utility for error message
def cprint_error(msg, log_fd = None):
    try:
        cprint('[ERROR] ' + msg, True, log_fd, COLOR_CODE['red'])
        if (not is_windows_os()) and os.isatty(2):
            sys.stdout.write(COLOR_CODE['reset'])
    except:
        print('[ERROR] Exception in Utils::cprint_error()')


# cprint utility for verbose message
def cprint_verbose(msg, verbose=True, log_fd=None):
    try:
        if verbose:
            cprint('[INFO] ' + msg, True, log_fd, COLOR_CODE['reset'])
    except:
        print('[ERROR] Exception in Utils::cprint_verbose()')


# cprint utility for warning message
def cprint_warning(msg, log_fd = None):
    try:
        cprint('[WARNING] ' + msg, True, log_fd, COLOR_CODE['yellow'])
        if (not is_windows_os()) and os.isatty(2):
            sys.stdout.write(COLOR_CODE['reset'])
    except:
        print('[ERROR] Exception in Utils::cprint_warning()')


# cprint utility with timestamp and color support
def tprint(msg, newline = True, log_fd = None, color = None, flush = False):
    try:
        msg = '[' + time.ctime() + '] ' + msg
        cprint(msg, newline, log_fd, color, flush)
    except:
        print('[ERROR] Exception in Utils::tprint()')


# cprint utility for succ message with timestamp support
def tprint_succ(msg, log_fd = None):
    try:
        msg = '[' + time.ctime() + '] [SUCC] ' + msg
        cprint(msg, True, log_fd, COLOR_CODE['green'])
        if (not is_windows_os()) and os.isatty(2):
            sys.stdout.write(COLOR_CODE['reset'])
    except:
        print('[ERROR] Exception in Utils::tprint_succ()')


# cprint utility for error message with timestamp support
def tprint_error(msg, log_fd = None):
    try:
        msg = '[' + time.ctime() + '] [ERROR] ' + msg
        cprint(msg, True, log_fd, COLOR_CODE['red'])
        if (not is_windows_os()) and os.isatty(2):
            sys.stdout.write(COLOR_CODE['reset'])
    except:
        print('[ERROR] Exception in Utils::tprint_error()')


# cprint utility for verbose message and timestamp support
def tprint_verbose(msg, verbose=True, log_fd=None):
    try:
        if verbose:
            msg = '[' + time.ctime() + '] [INFO] ' + msg
            cprint(msg, True, log_fd, COLOR_CODE['reset'])
    except:
        print('[ERROR] Exception in Utils::tprint_verbose()')


# cprint utility for warning message with timestamp support
def tprint_warning(msg, log_fd = None):
    try:
        msg = '[' + time.ctime() + '] [WARNING] ' + msg
        cprint(msg, True, log_fd, COLOR_CODE['yellow'])
        if (not is_windows_os()) and os.isatty(2):
            sys.stdout.write(COLOR_CODE['reset'])
    except:
        print('[ERROR] Exception in Utils::tprint_warning()')

