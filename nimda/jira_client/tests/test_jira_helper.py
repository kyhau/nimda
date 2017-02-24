import logging
import requests_mock
from jira import JIRA
from mock import Mock

from nimda.jira_client.jira_helper import JiraHelper


test_logger = logging.getLogger(__file__)
test_logger.addHandler(logging.StreamHandler())


def test_jira_helper():
    """Test JiraHelper remove_all_access and members_in_all_groups
    """
    with requests_mock.mock() as mock_adapter:
        JIRA.__init__ = Mock(return_value=None)

        helper = JiraHelper('user@example.com', 'userpass', 'https://example.com', test_logger)
        helper._options = {'server': 'https://example.com'}

        helper.groups = Mock(return_value=['group1', 'group2'])
        helper.group_members = Mock(side_effect=
            [
                {'username1': {'active': True, 'fullname': 'User1 Hello', 'email': 'user1@example.com'}},
                {'username2': {'active': True, 'fullname': 'User2 Hello', 'email': 'user2@example.com'}},
                {'username3': {'active': True, 'fullname': 'User3 Hello', 'email': 'user3@example.com'}},
                {'username4': {'active': True, 'fullname': 'User4 Hello', 'email': 'user4@example.com'}},
                {'username5': {'active': True, 'fullname': 'User5 Hello', 'email': 'user5@example.com'}},
                {'username6': {'active': True, 'fullname': 'User6 Hello', 'email': 'user6@example.com'}},
            ])
        helper.remove_user_from_group = Mock(return_value=True)
        helper.deactivate_user = Mock(return_value=True)
        helper.revoke_application_access = Mock(side_effect=[True, False])

        # Test members_in_all_groups
        ret = helper.members_in_all_groups()
        assert type(ret) is dict
        assert 'username1' in ret.keys() and 'username2' in ret.keys()

        # Second calls should return True
        assert helper.remove_all_access("user1") is True

        # Second calls should return False
        assert helper.remove_all_access("user2") is False
