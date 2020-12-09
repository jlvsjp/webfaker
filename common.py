#!/usr/bin/env python3

import sys
import pdb
import time
import inspect
import logging
from logging import handlers


class MyStreamHandler(logging.Handler):
    terminator = '\n'

    def __init__(self):
        logging.Handler.__init__(self)
        self.out_stream = sys.stdout
        self.err_stream = sys.stderr

    def flush(self):
        self.acquire()
        self.out_stream.flush()
        self.err_stream.flush()
        self.release()

    def emit(self, record):
        try:
            msg = self.format(record)
            for stack in inspect.stack():
                # pdb.set_trace()
                filename = stack.filename if sys.version.startswith("3") else stack[1]
                function = stack.function if sys.version.startswith("3") else stack[3]
                if "logging" in filename and "info" in function:
                    msg = "\033[0;32;m[+] " + msg + '\033[0m'       # Green
                    stream = self.out_stream
                    stream.write(msg + self.terminator)
                    break

                if "logging" in filename and "warn" in function:
                    msg = "\033[0;33;m[-] " + msg + '\033[0m'       # Yellow
                    stream = self.err_stream
                    stream.write(msg + self.terminator)
                    break

                if "logging" in filename and "error" in function:
                    msg = "\033[0;31;m[!] " + msg + '\033[0m'       # Red
                    stream = self.err_stream
                    stream.write(msg + self.terminator)
                    break

                if "logging" in filename and "debug" in function:
                    stream = self.out_stream
                    stream.write(msg)
                    break

            self.flush()

        except Exception:
            self.handleError(record)


def init_logger(log_file=None, debug=False):
    log_file = log_file if log_file else "run.log"
    log_fmt = logging.Formatter('%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s')
    logger = logging.getLogger()
    logger.setLevel(logging.INFO if not debug else logging.DEBUG)

    file_handler = handlers.TimedRotatingFileHandler(filename=log_file, when='D', backupCount=3)
    file_handler.setFormatter(log_fmt)
    file_handler.setLevel(logging.INFO)
    logger.addHandler(file_handler)

    msh = MyStreamHandler()
    msh.setLevel(logging.INFO if not debug else logging.DEBUG)
    logger.addHandler(msh)


def get_timestamp_from_strftime(timestr):
    fmt = "%Y-%m-%dT%H:%M:%S"
    return int(time.mktime(time.strptime(timestr, fmt)))
