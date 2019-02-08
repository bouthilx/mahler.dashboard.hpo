import datetime

from . import config


def get_model_name(tags):
    for tag in tags:
        if tag in config.model_names:
            return tag

    raise ValueError('Does not contain any model name: {}'.format(tags))


def get_algo_name(tags):
    for tag in tags:
        if tag in config.algo_names:
            return tag

    raise ValueError('Does not contain any algo name: {}'.format(tags))


def get_distrib_name(tags):
    for tag in tags:
        if tag in config.distrib_names:
            return tag

    raise ValueError('Does not contain any distrib name: {}'.format(tags))


def convert_strdatetime(timestamp):
    return datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f")
