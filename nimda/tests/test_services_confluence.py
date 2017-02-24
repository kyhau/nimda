"""
Tests butler.services confluence
"""
import requests_mock
from os.path import exists, join

from nimda.services import ConfluenceService
import nimda.confluence.service_defs as DEFS
from nimda.tests.conftest import logger


def test_confluence_service_init(default_testing_config):
    """Test ConfluenceService _init_with_config
    """
    assert ConfluenceService.database_attr_name() == 'confluence'
    service = ConfluenceService(default_testing_config, logger)
    assert service.app is not None
    assert service.username == 'mr_confluence'
    assert service.userpass == 'mr_confluence_pass'
    assert service.server == 'https://example.com'


def test_confluence_service_off_board(default_testing_config, unit_tests_tmp_dir):
    """Test ConfluenceService off_board
    """
    with requests_mock.mock() as mock_adapter:
        service = ConfluenceService(default_testing_config, logger)
        TEST_SERVER = service.server

        #######################################################################
        # Test 1

        # Mock member_groups return value
        mock_adapter.get(DEFS.get_member_groups(TEST_SERVER, "user1").service_url,
            status_code=200,
            json={"results": [{"name": "group1", "type": "group"},], "size": 1}
        )

        # Mock remove_member_from_group return value
        mock_adapter.delete(DEFS.delete_member_from_group(TEST_SERVER, "user1", "group1").service_url\
            + "?username=user1&groupname=group1",
            status_code=204
        )

        # Mock revoke_application_access return value
        mock_adapter.delete(DEFS.delete_app_access(TEST_SERVER, "user1").service_url + "?username=user1",
            status_code=204
        )

        # Mock deactivate_user return value
        mock_adapter.post(DEFS.post_deactivate_user(TEST_SERVER, "user1").service_url + "?username=user1",
            status_code=204
        )

        # First call should return True
        mock_adapter.post(DEFS.post_deactivate_user(TEST_SERVER, "user1").service_url + "?username=user1",
            status_code=204
        )
        assert service.off_board("user1") is True

        #######################################################################
        # Test 2

        # Mock deactivate_user return value
        mock_adapter.post(DEFS.post_deactivate_user(TEST_SERVER, "user1").service_url + "?username=user1",
            status_code=401
        )
        assert service.off_board("user1") is False


def test_confluence_service_summary(default_testing_config, unit_tests_tmp_dir):
    """Test ConfluenceService summary
    """
    service = ConfluenceService(default_testing_config, logger)
    TEST_SERVER = service.server
    db_users_dict = {
        'user1': {'gmail': 'user1', 'status': 'active', 'confluence': 'user1'},
        'user2': {'gmail': 'user1', 'status': 'suspended', 'confluence': 'user2'},
        # 'user3' not in database
    }

    with requests_mock.mock() as mock_adapter:
        # Mock groups return value
        mock_adapter.get(DEFS.get_groups(TEST_SERVER).service_url,
            status_code=200,
            json={
                "results": [{"name": "group1", "type": "group"},{"name": "group2", "type": "group"},],
                "size": 2
            }
        )

        # Mock group_members return value
        mock_adapter.get(DEFS.get_group_members(TEST_SERVER, "group1").service_url,
            status_code=200,
            json={
                "results": [
                    {"username": "user1", "displayName": "User 1", "userKey": "userkey1", "type": "known"},
                    {"username": "user2", "displayName": "User 2", "userKey": "userkey1", "type": "known"},
                ],
                "size": 2
            }
        )
        mock_adapter.get(DEFS.get_group_members(TEST_SERVER, "group2").service_url,
            status_code=200,
            json={
                "results": [
                    {"username": "user1", "displayName": "User 1", "userKey": "userkey1", "type": "known"},
                    {"username": "user3", "displayName": "User 3", "userKey": "userkey3", "type": "known"},
                ],
                "size": 2
            }
        )

        service.summary(db_users_dict)
        assert exists(join(unit_tests_tmp_dir, service.output_file))


def test_confluence_service_report_inactive_users_still_have_access(default_testing_config, unit_tests_tmp_dir):
    """Test ConfluenceService report_inactive_users_still_have_access
    """
    db_users_dict = {
        'user1': {'gmail': 'user1', 'status': 'active', 'confluence': 'user1'},
        'user2': {'gmail': 'user2', 'status': 'suspended', 'confluence': 'user2'},
        'user3': {'gmail': 'user3', 'status': 'transferred', 'confluence': 'user3'},
        'user4': {'gmail': 'user4', 'status': 'deleted', 'confluence': 'user4'},
        'user5': {'gmail': 'user5', 'status': 'deleted'},
        'user6': {'gmail': 'user6', 'status': 'active'},
    }

    # inactive users (i.e. not active or transferred) still have confluence access
    service = ConfluenceService(default_testing_config, logger)
    assert service.report_inactive_users_still_have_access(db_users_dict) == 2
