from __future__ import print_function
import argparse
from decimal import Decimal
import json
import logging
from logging.handlers import RotatingFileHandler
import os
import re
from six.moves import configparser


def prepare_logger(app_name, log_file=None, log_level=logging.DEBUG):
    """Prepare logger for the given app name
    """
    logger = logging.getLogger(app_name)
    logger.setLevel(log_level)
    formatter = logging.Formatter('%(levelname)s %(message)s')

    # Create console handler and set formatter
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # Create file handler and set formatter
    if log_file is not None:
        fh = RotatingFileHandler(log_file, mode='a', maxBytes=5*1024*1024, backupCount=2)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger


def read_config_from_argv(argv):
    """Retrieve config from config file passed in from argv
    """
    parser = argparse.ArgumentParser(description='Butler-Alpha')
    parser.add_argument('-c', '--config', metavar='CONFIG_INI',
                        help='config.ini file', required=True)
    parser.add_argument('-o', '--offboard', metavar='USER_NAME', default=None,
                        help='User to be off-boarded for all services')
    parser.add_argument('-t', '--transfer', metavar='USER_NAME', default=None,
                        help='User (transferring to other business group) to be off-boarded for a sub set of the services')
    args = parser.parse_args(argv)

    # read from config
    if not os.path.exists(args.config):
        print('Config file {} not found'.format(args.config))
        return None, None

    configs = configparser.ConfigParser()
    configs.read(args.config)
    return configs, args


def read_multi_lines_config(config, section_name, param_name, logger):
    """Return list of values of multi-lines config
    """
    try:
        values = config.get(section_name, param_name)
        return [
            n.strip() for n in re.split(';| |, |\*|\n', values) \
            #ignore commented line
            if n.strip() and not n.strip().startswith('#')
        ]
    except Exception as e:
        print(e.message) if logger is None else logger.error(e)
    return []


def write_to_json_file(data, filename, indent=2):
    """Write given json data to file with indent
    """
    def default_encoder(obj):
        if isinstance(obj, Decimal):
            return str(obj)
        raise TypeError

    with open(filename, "w") as outfile:
        json.dump(data, outfile, sort_keys=True, indent=indent, default=default_encoder)
