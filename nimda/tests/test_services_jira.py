"""
Tests butler.services jira
"""
from mock import Mock

from nimda.services import JiraService
from nimda.tests.conftest import logger


def test_jira_service_init(default_testing_config):
    """Test JiraService database_attr_name and _init_with_config
    """
    assert JiraService.database_attr_name() == 'jira'

    from jira import JIRA
    JIRA.__init__ = Mock(return_value=None)

    service = JiraService(default_testing_config, logger)

    service.app.all_users = Mock(return_value=[
        {'gmail': 'user1', 'bitbucket': 'user1'},
        {'gmail': 'user2', 'bitbucket': 'user2'}
    ])

    assert service.useremail == 'mr_jira@exammple.com'
    assert service.userpass == 'mr_jira_pass'
    assert service.server == 'https://example.com'


def test_jira_service_report_inactive_users_still_have_access(default_testing_config):
    """Test JiraService report_inactive_users_still_have_access
    """
    db_users_dict = {
        'user1': {'gmail': 'user1', 'status': 'active', 'jira': 'user1'},
        'user2': {'gmail': 'user2', 'status': 'suspended', 'jira': 'user2'},
        'user3': {'gmail': 'user3', 'status': 'transferred', 'jira': 'user3'},
        'user4': {'gmail': 'user4', 'status': 'deleted', 'jira': 'user4'},
        'user5': {'gmail': 'user5', 'status': 'deleted'},
        'user6': {'gmail': 'user6', 'status': 'active'},
    }

    # inactive users (i.e. not active or transferred) still have jira access
    service = JiraService(default_testing_config, logger)
    assert service.report_inactive_users_still_have_access(db_users_dict) == 2


def test_report_users_not_in_database(default_testing_config):
    """Test JiraService report_users_not_in_database
    """
    db_jira_users = [
        {'gmail': 'user1', 'status': 'active', 'jira': 'user1'},
        {'gmail': 'user2', 'status': 'suspended', 'jira': 'user2'},
        {'gmail': 'user3', 'status': 'transferred', 'jira': 'user3'},
        {'gmail': 'user4', 'status': 'deleted', 'jira': 'user4'},
    ]
    all_jira_users = {
        'user1': {},
        'user2': {},
        'user5': {},
    }

    service = JiraService(default_testing_config, logger)
    assert service.report_users_not_in_database(db_jira_users, all_jira_users) == 1
