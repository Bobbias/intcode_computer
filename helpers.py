import logging
import sys
from itertools import chain, repeat, islice
import re

import enums


def pad_infinite(iterable, padding=None):
    return chain(iterable, repeat(padding))


def pad(iterable, size, padding=None):
    return list(islice(pad_infinite(iterable, padding), size))


formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')


def setup_logger(name, log_file, level=logging.INFO):
    """To setup as many loggers as you want"""

    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger


def is_relevant(item):
    if re.match(r'_(?!.*di|.*log|_).*', item[0]):
        return True
    else:
        return False


def process_intcode_exception(logger, pc, program, err):
    logger.exception(err)
    logger.error(f'Exception occurred at {pc}')
    window_size = 7
    start = pc - window_size
    end = pc + window_size if len(program) > pc + window_size else len(program)
    logger.error(f'{start}:{end}')
    logger.error(f'{program[start:end]}')
    sys.exit(-1)
