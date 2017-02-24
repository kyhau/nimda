import json
import logging
import requests_mock

from nimda.bitbucket.bitbucket_helper import BitbucketHelper
from nimda.bitbucket.extra_entrypoints import extra_entrypoints_json


test_logger = logging.getLogger(__file__)
test_logger.addHandler(logging.StreamHandler())


def test_extra_entrypoints_data_ready():
    """Test BitbucketHelper has the extra entrypoints loaded
    """
    data = json.loads(extra_entrypoints_json)
    helper = BitbucketHelper(username=None, userpass=None, useremail=None, logger=test_logger)
    for k, _ in data['_links'].items():
        assert k in helper.relationships()


def test_remove_all_team_repo_access():
    """Test BitbucketHelper remove_all_team_repo_access
    """
    with requests_mock.mock() as mock_adapter:
        helper = BitbucketHelper('username1', 'userpass1', 'useremail1', test_logger)

        # First call should return True for 201
        mock_adapter.delete(
            "https://bitbucket.org/!api/internal/user/team1/access/user1",
            status_code=201
        )
        assert helper.remove_all_team_repo_access("user1", "team1") is True

        # Second calls should return False for 400
        mock_adapter.delete(
            "https://bitbucket.org/!api/internal/user/team2/access/user2",
            status_code=400
        )
        assert helper.remove_all_team_repo_access("user2", "team2") is False


def test_current_team_members():
    """Test BitbucketHelper current_team_members
    """
    with requests_mock.mock() as mock_adapter:
        mock_returned_value = [
            {"username": "mr_bitbuctket",
             "website": None,
             "display_name": "Mr Bitbucket",
             "uuid": "adksjhfshfkf",
             "links": {},
             "created_on": "2015-08-14T07:02:38.814441+00:00",
             "location": None,
             "type": None
             }
        ]

        mock_adapter.get(
            "https://api.bitbucket.org/2.0/teams/team1/members",
            json=mock_returned_value
        )

        helper = BitbucketHelper('username1', 'userpass1', 'useremail1', test_logger)
        ret = helper.current_team_members("team1")

        assert type(ret) is list
        assert ret[0]['username'] == 'mr_bitbuctket'
        assert ret[0]['display_name'] == 'Mr Bitbucket'
        assert ret[0]['created_on'] == '2015-08-14T07:02:38.814441+00:00'
        assert ret[0]['uuid'] == 'adksjhfshfkf'
