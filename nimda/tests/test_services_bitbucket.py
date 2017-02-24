"""
Tests butler.services bitbucket
"""
import requests_mock
from os.path import exists, join

from nimda.services import BitbucketService
from nimda.tests.conftest import logger


def test_bitbucket_service_init(default_testing_config):
    """Test BitbucketService _init_with_config
    """
    assert BitbucketService.database_attr_name() == 'bitbucket'
    service = BitbucketService(default_testing_config, logger)
    assert service.app is not None
    assert service.username == 'mr_bitbucket'
    assert service.userpass == 'mr_bitbucket_pass'
    assert service.useremail == 'mr_bitbucket@example.com'
    assert 'team1' in service.bitbucket_teams and 'team2' in service.bitbucket_teams


def test_bitbucket_service_off_board(default_testing_config, unit_tests_tmp_dir):
    """Test BitbucketService off_board
    """
    with requests_mock.mock() as mock_adapter:
        mock_adapter.delete(
            "https://bitbucket.org/!api/internal/user/team1/access/user1",
            status_code=201
        )
        mock_adapter.delete(
            "https://bitbucket.org/!api/internal/user/team2/access/user1",
            status_code=201
        )
        service = BitbucketService(default_testing_config, logger)
        assert service.off_board(
            user_data='user1'
        ) is True


def test_bitbucket_service_all_users(default_testing_config, unit_tests_tmp_dir):
    """Test BitbucketService summary
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
        mock_adapter.get(
            "https://api.bitbucket.org/2.0/teams/team2/members",
            json=mock_returned_value
        )

        service = BitbucketService(default_testing_config, logger)
        service.summary()

        assert exists(join(unit_tests_tmp_dir, 'BitbucketUsers-team1.csv'))
        assert exists(join(unit_tests_tmp_dir, 'BitbucketUsers-team2.csv'))
