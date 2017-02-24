import logging
import requests_mock

from nimda.jenkins.jenkins_helper import JenkinsHelper
import nimda.jenkins.service_defs as DEFS


test_logger = logging.getLogger(__file__)
test_logger.addHandler(logging.StreamHandler())

TEST_SERVER = "https://example.com"
TEST_AUTH_USER = "username1"
TEST_AUTH_PASS = "userpass1"


def test_jenkins_active_users():
    """Test JenkinsHelper active_users
    """
    with requests_mock.mock() as mock_adapter:
        helper = JenkinsHelper(TEST_AUTH_USER, TEST_AUTH_PASS, TEST_SERVER, test_logger)

        user_ids = ['user1', 'user2']

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

        ret = helper.active_users(user_ids)
        assert len(ret) == 1
        assert 'user1' in ret


def test_jenkins_all_users():
    """Test JenkinsHelper all_users
    """
    with requests_mock.mock() as mock_adapter:
        helper = JenkinsHelper(TEST_AUTH_USER, TEST_AUTH_PASS, TEST_SERVER, test_logger)

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
        ret = helper.all_users()
        assert len(ret)==2
        assert 'user1' in ret and 'user2' in ret

        # Mock get_users return 401
        mock_adapter.get(DEFS.get_users(TEST_SERVER).service_url,
             status_code=401,
             json={}
        )
        ret = helper.all_users()
        assert len(ret) == 0


def test_jenkins_is_user_active():
    """Test JenkinsHelper is_user_active
    """
    with requests_mock.mock() as mock_adapter:
        helper = JenkinsHelper(TEST_AUTH_USER, TEST_AUTH_PASS, TEST_SERVER, test_logger)

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
        assert helper.is_user_active('user1') is True

        # Mock get_user return non active user for 200
        mock_adapter.get(DEFS.get_user(TEST_SERVER, 'user2').service_url,
            status_code=200,
            json={
                "absoluteUrl": "{}/user/user2".format(TEST_SERVER),
                "fullName": "user2",
                "id": "user2",
                "property": []
            }
        )
        assert helper.is_user_active('user2') is False


def test_jenkins_helper_remove_user_from_organisation():
    """Test JenkinsHelper remove_user_from_organisation
    """
    with requests_mock.mock() as mock_adapter:
        helper = JenkinsHelper(TEST_AUTH_USER, TEST_AUTH_PASS, TEST_SERVER, test_logger)

        # Mock delete_user_from_organisation return 200
        mock_adapter.post(
            DEFS.post_do_delete_user(TEST_SERVER, 'user1').service_url,
            status_code=200
        )
        assert helper.remove_user('user1') is True

        # Mock post_do_delete_user return 401
        mock_adapter.post(
            DEFS.post_do_delete_user(TEST_SERVER, 'user2').service_url,
            status_code=401
        )
        assert helper.remove_user('user2') is False

