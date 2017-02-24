import logging
import requests_mock

from nimda.flowdock.flowdock_helper import FlowdockHelper
import nimda.flowdock.service_defs as DEFS


test_logger = logging.getLogger(__file__)
test_logger.addHandler(logging.StreamHandler())

TEST_SERVER = "https://example.com"
TEST_AUTH_USER = "username1@example.com"
TEST_AUTH_PASS = "userpass1"
TEST_AUTH_ORGANISATION = "example"


def test_flowdock_users():
    """Test FlowdockHelper users
    """
    with requests_mock.mock() as mock_adapter:
        helper = FlowdockHelper(TEST_AUTH_USER, TEST_AUTH_PASS, TEST_AUTH_ORGANISATION, TEST_SERVER, test_logger)

        sample_email_list = ["user2@example.com", "user3@example.com"]

        # Mock get_users return a list of users for 200
        mock_adapter.get(DEFS.get_users(TEST_SERVER).service_url,
            status_code=200,
            json=[
                {"email": "user1@example.com", "id": 1111},
                {"email": "user2@example.com", "id": 2222},
                {"email": "user3@example.com", "id": 3333},
            ]
        )

        # Should return only the users with email addresses in sample_email_list
        ret = helper.users(sample_email_list)
        assert type(ret) is list and len(ret) == 2
        assert ret[0]['email'] == "user2@example.com"
        assert ret[1]['email'] == "user3@example.com"

        # Mock get_users return for 401
        mock_adapter.get(DEFS.get_users(TEST_SERVER).service_url,
            status_code=401
        )

        # Should return an empty list
        ret = helper.users(sample_email_list)
        assert type(ret) is list and len(ret) == 0


def test_flowdock_helper_remove_user_from_organisation():
    """Test FlowdockHelper remove_user_from_organisation
    """
    with requests_mock.mock() as mock_adapter:
        helper = FlowdockHelper(TEST_AUTH_USER, TEST_AUTH_PASS, TEST_AUTH_ORGANISATION, TEST_SERVER, test_logger)

        # Mock delete_user_from_organisation return 200
        mock_adapter.delete(
            DEFS.delete_user_from_organisation(TEST_SERVER, TEST_AUTH_ORGANISATION, 1111).service_url,
            status_code=200
        )
        assert helper.remove_user_from_organisation(1111) is True

        # Mock delete_user_from_organisation return 401
        mock_adapter.delete(
            DEFS.delete_user_from_organisation(TEST_SERVER, TEST_AUTH_ORGANISATION, 2222).service_url,
            status_code=401
        )
        assert helper.remove_user_from_organisation(2222) is False

