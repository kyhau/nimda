"""
Tests butler.services flowdock
"""
import requests_mock
from os.path import exists, join

from nimda.services import FlowdockService
import nimda.flowdock.service_defs as DEFS
from nimda.tests.conftest import logger


def test_flowdock_service_init(default_testing_config):
    """Test FlowdockService _init_with_config
    """
    assert FlowdockService.database_attr_name() == 'flowdock'
    service = FlowdockService(default_testing_config, logger)
    assert service.app is not None
    assert service.email == 'mr_flowdock@example.com'
    assert service.userpass == 'mr_flowdock_pass'
    assert service.server == 'https://example.com'
    assert service.organisation == 'example'


def test_flowdock_service_off_board(default_testing_config, unit_tests_tmp_dir):
    """Test FlowdockService off_board
    """
    with requests_mock.mock() as mock_adapter:
        service = FlowdockService(default_testing_config, logger)
        TEST_SERVER = service.server
        TEST_ORGANISATION = service.organisation

        #######################################################################
        # Test 1

        # Mock delete_user_from_organisation return 200
        mock_adapter.delete(
            DEFS.delete_user_from_organisation(TEST_SERVER, TEST_ORGANISATION, 1111).service_url,
            status_code=200
        )
        assert service.off_board(1111) is True

        #######################################################################
        # Test 2

        # Mock delete_user_from_organisation return 401
        mock_adapter.delete(
            DEFS.delete_user_from_organisation(TEST_SERVER, TEST_ORGANISATION, 2222).service_url,
            status_code=401
        )
        assert service.off_board(2222) is False


def test_flowdock_service_summary(default_testing_config, unit_tests_tmp_dir):
    """Test FlowdockService summary
    """
    service = FlowdockService(default_testing_config, logger)
    TEST_SERVER = service.server

    db_users_dict = {
        'user1': {'gmail': 'user1', 'status': 'active', 'flowdock': 1111},
        'user2': {'gmail': 'user2', 'status': 'suspended', 'flowdock': 2222},
        # 'user3' not in database
    }

    with requests_mock.mock() as mock_adapter:
        # Mock get_users return a list of users for 200
        mock_adapter.get(DEFS.get_users(TEST_SERVER).service_url,
            status_code=200,
            json=[
                {"email": "user1@example.com", "id": 1111},
                {"email": "user2@example.com", "id": 2222},
                {"email": "user3@example.com", "id": 3333},
            ]
        )

        service.summary(db_users_dict)
        assert exists(join(unit_tests_tmp_dir, service.output_file))


def test_flowdock_service_report_inactive_users_still_have_access(default_testing_config, unit_tests_tmp_dir):
    """Test FlowdockService report_inactive_users_still_have_access
    """
    db_users_dict = {
        'user1': {'gmail': 'user1', 'status': 'active', 'flowdock': 1111},
        'user2': {'gmail': 'user2', 'status': 'suspended', 'flowdock': 2222},
        'user3': {'gmail': 'user3', 'status': 'transferred', 'flowdock': 3333},
        'user4': {'gmail': 'user4', 'status': 'deleted', 'flowdock': 4444},
        'user5': {'gmail': 'user5', 'status': 'deleted'},
        'user6': {'gmail': 'user6', 'status': 'active'},
    }

    # inactive users (i.e. not active or transferred) still have flowdock access
    service = FlowdockService(default_testing_config, logger)
    assert service.report_inactive_users_still_have_access(db_users_dict) == 2
