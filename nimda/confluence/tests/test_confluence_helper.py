import logging
import requests_mock

from nimda.confluence.confluence_helper import ConfluenceHelper
import nimda.confluence.service_defs as DEFS


test_logger = logging.getLogger(__file__)
test_logger.addHandler(logging.StreamHandler())

TEST_SERVER = "https://example.com"
TEST_AUTH_USER = "username1"
TEST_AUTH_PASS = "userpass1"


def test_confluence_helper_groups():
    """Test ConfluenceHelper groups
    """
    with requests_mock.mock() as mock_adapter:
        helper = ConfluenceHelper(TEST_AUTH_USER, TEST_AUTH_PASS, TEST_SERVER, test_logger)

        # First call should return a list of groups for 201
        mock_returned_value = {
            "results": [
                {"name": "group1", "type": "group"},
                {"name": "group2", "type": "group"},
            ],
            "size": 2
        }
        mock_adapter.get(DEFS.get_groups(TEST_SERVER).service_url,
            json=mock_returned_value,
            status_code=200
        )
        ret = helper.groups()
        assert type(ret) is list and len(ret) == 2
        assert "group1" in ret and "group2" in ret

        # Second call should return an empty list for 401
        mock_adapter.get(DEFS.get_groups(TEST_SERVER).service_url,
            json=mock_returned_value,
            status_code=401
        )
        ret = helper.groups()
        assert type(ret) is list and len(ret) == 0


def test_confluence_helper_group_members():
    """Test ConfluenceHelper group_members
    """
    with requests_mock.mock() as mock_adapter:
        helper = ConfluenceHelper(TEST_AUTH_USER, TEST_AUTH_PASS, TEST_SERVER, test_logger)

        # First call should return a list of users for 201
        mock_returned_value = {
            "results": [
                {"username": "user1", "displayName": "User 1", "userKey": "userkey1", "type": "known"},
                {"username": "user2", "displayName": "User 2", "userKey": "userkey1", "type": "known"},
            ],
            "size": 2
        }
        mock_adapter.get(DEFS.get_group_members(TEST_SERVER, "group1").service_url,
            json=mock_returned_value,
            status_code=200
        )
        ret = helper.group_members("group1")
        assert type(ret) is list and len(ret) == 2
        assert ret[0]["username"] == "user1"
        assert ret[0]["displayName"] == "User 1"
        assert ret[0]["userKey"] == "userkey1"

        # Second call should return an empty list for 401
        mock_adapter.get(DEFS.get_group_members(TEST_SERVER, "group2").service_url,
            json=mock_returned_value,
            status_code=401
        )
        ret = helper.group_members("group2")
        assert type(ret) is list and len(ret) == 0


def test_confluence_helper_member_groups():
    """Test ConfluenceHelper member_groups
    """
    with requests_mock.mock() as mock_adapter:
        helper = ConfluenceHelper(TEST_AUTH_USER, TEST_AUTH_PASS, TEST_SERVER, test_logger)

        # First call should return a list of groups for 201
        mock_returned_value = {
            "results": [
                {"name": "group1", "type": "group"},
                {"name": "group2", "type": "group"},
            ],
            "size": 2
        }
        mock_adapter.get(DEFS.get_member_groups(TEST_SERVER, "user1").service_url,
            json=mock_returned_value,
            status_code=200
        )
        ret = helper.member_groups("user1")
        assert type(ret) is list and len(ret) == 2
        assert ret[0] == "group1"
        assert ret[1] == "group2"

        # Second call should return an empty list for 401
        mock_adapter.get(DEFS.get_member_groups(TEST_SERVER, "user2").service_url,
            json=mock_returned_value,
            status_code=401
        )
        ret = helper.member_groups("user2")
        assert type(ret) is list and len(ret) == 0


def test_confluence_helper_remove_member_from_group():
    """Test ConfluenceHelper remove_member_from_group
    """
    with requests_mock.mock() as mock_adapter:
        helper = ConfluenceHelper(TEST_AUTH_USER, TEST_AUTH_PASS, TEST_SERVER, test_logger)

        # First call should return 204
        mock_adapter.delete(DEFS.delete_member_from_group(TEST_SERVER, "user1", "group1").service_url\
            + "?username=user1&groupname=group1",
            status_code=204
        )
        assert helper.remove_member_from_group("user1", "group1") is True

        # Second call should return for 401
        mock_adapter.delete(DEFS.delete_member_from_group(TEST_SERVER, "user2", "group2").service_url \
            + "?username=user2&groupname=group2",
            status_code=401
        )
        assert helper.remove_member_from_group("user2", "group2") is False


def test_confluence_helper_revoke_application_access():
    """Test ConfluenceHelper revoke_application_access
    """
    with requests_mock.mock() as mock_adapter:
        helper = ConfluenceHelper(TEST_AUTH_USER, TEST_AUTH_PASS, TEST_SERVER, test_logger)

        # First call should return 204
        mock_adapter.delete(DEFS.delete_app_access(TEST_SERVER, "user1").service_url + "?username=user1",
            status_code=204
        )
        assert helper.revoke_application_access("user1") is True

        # Second call should return 401
        mock_adapter.delete(DEFS.delete_app_access(TEST_SERVER, "user2").service_url + "?username=user2",
            status_code=401
        )
        assert helper.revoke_application_access("user2") is False


def test_confluence_helper_deactivate_user():
    """Test ConfluenceHelper deactivate_user
    """
    with requests_mock.mock() as mock_adapter:
        helper = ConfluenceHelper(TEST_AUTH_USER, TEST_AUTH_PASS, TEST_SERVER, test_logger)

        # First call should return 204
        mock_adapter.post(DEFS.post_deactivate_user(TEST_SERVER, "user1").service_url + "?username=user1",
            status_code=204
        )
        assert helper.deactivate_user("user1") is True

        # Second call should return 401
        mock_adapter.post(DEFS.post_deactivate_user(TEST_SERVER, "user2").service_url + "?username=user2",
            status_code=401
        )
        assert helper.deactivate_user("user2") is False


def test_confluence_helper_remove_all_access():
    """Test ConfluenceHelper remove_all_access
    """
    with requests_mock.mock() as mock_adapter:
        helper = ConfluenceHelper(TEST_AUTH_USER, TEST_AUTH_PASS, TEST_SERVER, test_logger)

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
        assert helper.remove_all_access("user1") is True

        #######################################################################
        # Test 2

        # Mock deactivate_user return value
        mock_adapter.post(DEFS.post_deactivate_user(TEST_SERVER, "user1").service_url + "?username=user1",
            status_code=401
        )
        assert helper.remove_all_access("user1") is False


def test_confluence_helper_members_in_all_groups():
    """Test ConfluenceHelper members_in_all_groups
    """
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

        helper = ConfluenceHelper(TEST_AUTH_USER, TEST_AUTH_PASS, TEST_SERVER, test_logger)
        ret = helper.members_in_all_groups()

        assert len(ret.keys()) == 3
        assert ret["user1"] and ret["user2"] and ret["user3"]
        assert len(ret["user1"]["groups"]) == 2 and "group1" in ret["user1"]["groups"] and "group2" in ret["user1"]["groups"]
        assert len(ret["user2"]["groups"]) == 1 and "group1" in ret["user2"]["groups"]
        assert len(ret["user3"]["groups"]) == 1 and "group2" in ret["user3"]["groups"]
