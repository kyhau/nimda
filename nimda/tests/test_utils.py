"""
Tests butler.utils
"""
import logging
import os
import py.test

from nimda.utils import (
    prepare_logger,
    read_config_from_argv,
    read_multi_lines_config,
    write_to_json_file
)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__file__)


def test_prepare_logger(unit_tests_tmp_dir):
    """Test prepare_logger
    """
    expected_log_file = os.path.join(unit_tests_tmp_dir, 'tmp_test_utils.log')
    l = prepare_logger('hello_world', expected_log_file, logging.DEBUG)
    assert l
    assert os.path.exists(expected_log_file)

    # release all handlers
    handlers = l.handlers[:]
    for h in handlers:
        h.close()
        l.removeHandler(h)


def test_read_config_from_argv(default_testing_ini):
    """Test reading config file from argv
    """
    # no config specified
    with py.test.raises(SystemExit):
        read_config_from_argv([__file__])

    # config ini file specified
    configs, args = read_config_from_argv([
        '-c', default_testing_ini,
        '-o', 'user_to_be_offboarded',
        '-t', 'user_to_be_transferred'
    ])
    assert configs.get('bitbucket', 'bitbucket.username')
    assert configs.get('bitbucket', 'bitbucket.password')
    assert configs.get('bitbucket', 'bitbucket.email')
    assert args.offboard == 'user_to_be_offboarded'
    assert args.transfer == 'user_to_be_transferred'


def test_read_multi_lines_config(default_testing_ini):
    """Test multi-lines config (e.g. bitbucket.teams)
    """
    configs, args = read_config_from_argv([
        '-c', default_testing_ini,
        '-o', 'user_to_be_offboarded',
        '-t', 'user_to_be_transferred'
    ])
    ret = read_multi_lines_config(configs, 'bitbucket', 'bitbucket.teams', logger)
    assert len(ret) == 2
    assert ret[0] == 'team1'
    assert ret[1] == 'team2'
    assert args.offboard == 'user_to_be_offboarded'
    assert args.transfer == 'user_to_be_transferred'


def test_json_to_file(unit_tests_tmp_dir):
    """Test writing json data to file
    """
    sample_data = {
        "user1": {
            "acc 1": "acc_name1",
            "acc 2": "acc_name2",
            "acc 3": "acc_name3",
        }
    }
    json_output_filename = os.path.join(unit_tests_tmp_dir, 'test_write_json_output.json')
    write_to_json_file(
        sample_data,
        json_output_filename,
        indent=4
    )
    assert os.path.exists(json_output_filename)
