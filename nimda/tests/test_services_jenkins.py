"""
Tests butler.services jenkins
"""
import requests_mock
from os.path import exists, join

from nimda.services import JenkinsService
import nimda.jenkins.service_defs as DEFS
from nimda.tests.conftest import logger


def test_jenkins_service_init(default_testing_config):
    """Test JenkinsService _init_with_config
    """
    assert JenkinsService.database_attr_name() == 'jenkins'
    service = JenkinsService(default_testing_config, logger)
    assert service.app is not None
    assert service.username == 'mr_jenkins'
    assert service.userpass == 'mr_jenkins_pass'
    assert service.server == 'https://example.com'


def test_jenkins_service_off_board(default_testing_config, unit_tests_tmp_dir):
    """Test JenkinsService off_board
    """
    with requests_mock.mock() as mock_adapter:
        service = JenkinsService(default_testing_config, logger)
        TEST_SERVER = service.server

        #######################################################################
        # Test 1

        # Mock post_do_delete_user return 200
        mock_adapter.post(
            DEFS.post_do_delete_user(TEST_SERVER, 'user1').service_url,
            status_code=200
        )
        assert service.off_board('user1') is True

        #######################################################################
        # Test 2

        # Mock post_do_delete_user return 401
        mock_adapter.post(
            DEFS.post_do_delete_user(TEST_SERVER, 'user2').service_url,
            status_code=401
        )
        assert service.off_board('user2') is False


def test_jenkins_service_summary(default_testing_config, unit_tests_tmp_dir):
    """Test JenkinsService summary
    """
    service = JenkinsService(default_testing_config, logger)
    TEST_SERVER = service.server

    with requests_mock.mock() as mock_adapter:

        db_users_dict = {
            'user1': {'gmail': 'user1', 'status': 'active', 'jenkins': "user1"},
            'user2': {'gmail': 'user2', 'status': 'suspended', 'jenkins': "user2"},
            # 'user3' not in database
        }

        # Mock get_users return users for 200
        mock_adapter.get(DEFS.get_users(TEST_SERVER).service_url,
            status_code=200,
            json={
                "users": [
                    {'user': {'absoluteUrl': '{}/user/user1'.format(TEST_SERVER)}},
                    {'user': {'absoluteUrl': '{}/user/user2'.format(TEST_SERVER)}},
                ]
            }
        )
        # Mock get_user return a active user for 200
        mock_adapter.get(DEFS.get_user(TEST_SERVER, 'user1').service_url,
            status_code=200,
            json={
                "absoluteUrl": "{}/user/user1".format(TEST_SERVER),
                "fullName": "user1",
                "id": "user1",
                "property": [
                    {"_class": "hudson.security.HudsonPrivateSecurityRealm$Details"}
                ]
            }
        )
        # Mock get_user return a non active user for 200
        mock_adapter.get(DEFS.get_user(TEST_SERVER, 'user2').service_url,
            status_code=200,
            json={
                "absoluteUrl": "{}/user/user2".format(TEST_SERVER),
                "fullName": "user2",
                "id": "user2",
                "property": []
            }
        )

        service.summary(db_users_dict)
        assert exists(join(unit_tests_tmp_dir, service.output_file))


def test_jenkins_service_report_inactive_users_still_have_access(default_testing_config, unit_tests_tmp_dir):
    """Test JenkinsService report_inactive_users_still_have_access
    """
    db_users_dict = {
        'user1': {'gmail': 'user1', 'status': 'active', 'jenkins': 'user1'},
        'user2': {'gmail': 'user2', 'status': 'suspended', 'jenkins': 'user2'},
        'user3': {'gmail': 'user3', 'status': 'transferred', 'jenkins': 'user3'},
        'user4': {'gmail': 'user4', 'status': 'deleted', 'jenkins': 'user4'},
        'user5': {'gmail': 'user5', 'status': 'deleted'},
        'user6': {'gmail': 'user6', 'status': 'active'},
    }

    # inactive users (i.e. not active or transferred) still have jenkins access
    service = JenkinsService(default_testing_config, logger)
    assert service.report_inactive_users_still_have_access(db_users_dict) == 2
