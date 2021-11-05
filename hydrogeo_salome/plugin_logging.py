# Copyright (C) 2017-2020 JCT
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
#
# Author : Jonathan Teixeira (jonathan.teixeira@ufpe.br)
#

"""
This file contains the initialization of the logger that is used in the macros.
I.e. it configures the "logging" module of python
"""

# python imports
from .utilities import GetAbsPathInModule
from . import IsExecutedInSalome
import os
import sys
import traceback
import logging
from logging.handlers import RotatingFileHandler
logger = logging.getLogger("HYDROGEOLOGY SALOME")


# salome-hydrogeology imports


class _AnsiColorStreamHandler(logging.StreamHandler):
    """This handler colorizes the log-level (e.g. INFO or DEBUG)
    It supports ansi color codes
    adapted from https://gist.github.com/mooware/a1ed40987b6cc9ab9c65
    """
    DEFAULT = '\x1b[0m'
    RED = '\x1b[1;31m'
    RED_UDL = '\x1b[1;4m\x1b[1;31m'
    GREEN = '\x1b[1;32m'
    YELLOW = '\x1b[1;33m'
    BLUE = '\x1b[1;34m'
    CYAN = '\x1b[1;36m'

    CRITICAL = RED_UDL
    ERROR = RED
    WARNING = YELLOW
    INFO = GREEN
    DEBUG = CYAN

    @classmethod
    def __GetColor(cls, level):
        if level == logging.CRITICAL:
            return cls.CRITICAL
        elif level == logging.ERROR:
            return cls.ERROR
        elif level == logging.WARNING:
            return cls.WARNING
        elif level == logging.INFO:
            return cls.INFO
        elif level == logging.DEBUG:
            return cls.DEBUG
        else:
            return cls.DEFAULT

    @classmethod
    def __ColorLevel(cls, record):
        return cls.__GetColor(record.levelno) + record.levelname + cls.DEFAULT

    def format(self, record):
        text = super().format(record)
        return text.replace(record.levelname, self.__ColorLevel(record))


def _HandleUnhandledException(exc_type, exc_value, exc_traceback):
    """Handler for unhandled exceptions that will write to the logs
    taken from: https://www.scrygroup.com/tutorial/2018-02-06/python-excepthook-logging/
    TODO: check if this also works properly in GUI
    """
    if issubclass(exc_type, KeyboardInterrupt):
        # call the default excepthook saved at __excepthook__
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    # log exception
    logger.exception("Unhandled exception", exc_info=(
        exc_type, exc_value, exc_traceback))


def InitializeLogging(logging_level=logging.INFO):
    """Initialize and configure the logging of the plugin"""
    # CONFIG logging level
    # TODO switch the default in the future
    # TODO this should come from the config file
    # logger_level = 2 # default value: 0
    # logger_levels = { 0 : logging.WARNING,
    #                 1 : logging.INFO,
    #                 2 : logging.DEBUG }

    # configuring the root logger, same configurInitializeLoggingation will be automatically used for other loggers
    root_logger = logging.getLogger()

    # this is particularily helpful for testing to reduce the output
    disable_logging = bool(
        int(os.getenv("HYDROGEOLOGY_SALOME_DISABLE_LOGGING", False)))

    if disable_logging:
        # this is intended for disabling the logger during testing, because some tests would generate output
        root_logger.disabled = True
        # setting a level higher than "critical" (which is level 50)
        root_logger.setLevel(100)
    else:
        root_logger.setLevel(logging_level)
        # has to be cleared, otherwise more and more handlers are added if the plugin is reopened
        root_logger.handlers.clear()

        # logging to console - without timestamp
        if "NO_COLOR" in os.environ:  # maybe also check if isatty!
            # see https://no-color.org/
            ch = logging.StreamHandler()
        elif IsExecutedInSalome():
            # Salome terminal supports colors both in Win and Linux
            # ch = _AnsiColorStreamHandler()
            ch = logging.StreamHandler()
        else:
            if os.name == "nt":
                # handler that supports color in Win is not yet implemented
                # see https://gist.github.com/mooware/a1ed40987b6cc9ab9c65
                # see https://plumberjack.blogspot.com/2010/12/colorizing-logging-output-in-terminals.html
                ch = logging.StreamHandler()
            else:
                ch = _AnsiColorStreamHandler()

        ch_formatter = logging.Formatter(
            "HGSP [%(levelname)-8s] %(name)s : %(message)s")
        ch.setFormatter(ch_formatter)
        root_logger.addHandler(ch)

        # logging to file - with timestamp
        log_file_path = os.getenv("HYDROGEOLOGY_SALOME_LOG_FILE_PATH", GetAbsPathInModule(
            os.pardir))  # unless otherwise specified log in root-dir
        fh = RotatingFileHandler(os.path.join(
            log_file_path, "hydrogeosalome.log"), maxBytes=5*1024*1024, backupCount=1)  # 5 MB
        fh_formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)-8s] %(name)s : %(message)s", "%Y-%m-%d %H:%M:%S")
        fh.setFormatter(fh_formatter)
        root_logger.addHandler(fh)

        sys.excepthook = _HandleUnhandledException
