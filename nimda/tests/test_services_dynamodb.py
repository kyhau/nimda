"""
Tests butler.services useraccounts (dynamodb)
"""
import boto3
from mock import Mock
from os.path import exists, join

from nimda.services import (
    UserAccountService,
    DynamoDBHelper,
)
from nimda.dynamodb.tests.test_dynamodb_helper import (
    SAMPLE_QUERY_OK,
    SAMPLE_SCAN_OK,
    SAMPLE_UPDATE_STATUS_OK
)
from nimda.tests.conftest import logger


def test_dynamodb_service_init(default_testing_config):
    """Test UserAccountService database_attr_name and _init_with_config
    """
    assert UserAccountService.database_attr_name() == 'gmail'

    DynamoDBHelper.create_client = Mock(
        return_value=boto3.resource('dynamodb', region_name='ap-southeast-2')
    )

    service = UserAccountService(default_testing_config, logger)

    service.app.all_users = Mock(return_value=[
        {'gmail': 'user1', 'bitbucket': 'user1'},
        {'gmail': 'user2', 'bitbucket': 'user2'}
    ])

    assert service.profile == 'mr_aws_profile'
    assert len(service.all_users().keys()) == 2


def test_dynamodb_service_off_board(default_testing_config, unit_tests_tmp_dir):
    """Test UserAccountService off_board
    """
    DynamoDBHelper.create_client = Mock(
        return_value=boto3.resource('dynamodb', region_name='ap-southeast-2')
    )

    service = UserAccountService(default_testing_config, logger)

    # Mock functions' outputs
    service.app.table.query = Mock(return_value=SAMPLE_QUERY_OK)
    service.app.table.put_item = Mock(return_value=SAMPLE_UPDATE_STATUS_OK)
    service.app.table.scan = Mock(return_value=SAMPLE_SCAN_OK)

    assert service.off_board(user_data={"gmail": "hello", "status": "suspended"}) is True


def test_dynamodb_service_summary(default_testing_config, unit_tests_tmp_dir):
    """Test UserAccountService summary
    """
    DynamoDBHelper.create_client = Mock(
        return_value=boto3.resource('dynamodb', region_name='ap-southeast-2')
    )

    service = UserAccountService(default_testing_config, logger)

    # Mock functions' outputs
    service.all_users = Mock(return_value={
        'user1': {'gmail': 'user1', 'status': 'active'},
        'user2': {'gmail': 'user2', 'status': 'active'}
    })
    service.users = service.all_users()

    service.summary()

    assert exists(join(unit_tests_tmp_dir, service.output_file))
