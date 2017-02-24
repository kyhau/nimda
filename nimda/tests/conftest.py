"""
conftest.py
"""
import logging
import pytest
from os.path import exists, join
from six.moves.configparser import RawConfigParser
from shutil import rmtree
from tempfile import mkdtemp


logger = logging.getLogger(__file__)
logger.addHandler(logging.StreamHandler())


@pytest.fixture(scope='session')
def unit_tests_tmp_dir(request):
    t = mkdtemp(prefix='butler_')
    logger.debug('Created tmp test dir {}.'.format(t))

    def teardown():
        # delete sample files created for the unit tests
        if exists(t):
            rmtree(t)
            logger.debug('Deleted tmp test dir {}.'.format(t))

    request.addfinalizer(teardown)
    return t


@pytest.fixture(scope='session')
def default_testing_config(unit_tests_tmp_dir):
    config = RawConfigParser()

    # Section default
    config.add_section('app')
    config.set('app', 'app.output_dir', unit_tests_tmp_dir)
    config.set('app', 'app.logfile', 'test_log.txt')

    # Section bitbucket
    config.add_section('bitbucket')
    config.set('bitbucket', 'bitbucket.teams', 'team1 \n team2 \n')
    config.set('bitbucket', 'bitbucket.username', 'mr_bitbucket')
    config.set('bitbucket', 'bitbucket.password', 'mr_bitbucket_pass')
    config.set('bitbucket', 'bitbucket.email', 'mr_bitbucket@example.com')

    # Section confluence
    config.add_section('confluence')
    config.set('confluence', 'confluence.username', 'mr_confluence')
    config.set('confluence', 'confluence.password', 'mr_confluence_pass')
    config.set('confluence', 'confluence.server', 'https://example.com')

    # Section dynamodb
    config.add_section('dynamodb')
    config.set('dynamodb', 'dynamodb.aws_profile_name', 'mr_aws_profile')

    # Section flowdock
    config.add_section('flowdock')
    config.set('flowdock', 'flowdock.email', 'mr_flowdock@example.com')
    config.set('flowdock', 'flowdock.password', 'mr_flowdock_pass')
    config.set('flowdock', 'flowdock.server', 'https://example.com')
    config.set('flowdock', 'flowdock.organisation', 'example')

    # Section jenkins
    config.add_section('jenkins')
    config.set('jenkins', 'jenkins.username', 'mr_jenkins')
    config.set('jenkins', 'jenkins.password', 'mr_jenkins_pass')
    config.set('jenkins', 'jenkins.server', 'https://example.com')

    # Section jira
    config.add_section('jira')
    config.set('jira', 'jira.email', 'mr_jira@exammple.com')
    config.set('jira', 'jira.password', 'mr_jira_pass')
    config.set('jira', 'jira.server', 'https://example.com')

    return config


@pytest.fixture(scope='session')
def default_testing_ini(unit_tests_tmp_dir, default_testing_config):

    testing_ini_file = join(unit_tests_tmp_dir, 'testing.ini')

    with open(testing_ini_file, 'w') as configfile:  # save
        default_testing_config.write(configfile)

    return testing_ini_file