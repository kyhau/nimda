import logging
from mock import Mock
from nimda.dynamodb.dynamodb_helper import DynamoDBHelper


test_logger = logging.getLogger(__file__)
test_logger.addHandler(logging.StreamHandler())


SAMPLE_QUERY_OK = {'Count':1, 'ResponseMetadata': {
    'RetryAttempts': 0, 'HTTPStatusCode': 200, 'RequestId': 'xxx', 'HTTPHeaders': {
        'x-amzn-requestid': 'xxx', 'content-length': '2', 'server': 'Server',
        'connection': 'keep-alive', 'x-amz-crc32': '2745614147',
        'date': 'Fri, 10 Feb 2017 10:49:05 GMT', 'content-type': 'application/x-amz-json-1.0'}}}

SAMPLE_UPDATE_STATUS_OK = {'ResponseMetadata': {
    'RetryAttempts': 0, 'HTTPStatusCode': 200, 'RequestId': 'xxx', 'HTTPHeaders': {
        'x-amzn-requestid': 'xxx', 'content-length': '2', 'server': 'Server',
        'connection': 'keep-alive', 'x-amz-crc32': '2745614147',
        'date': 'Fri, 10 Feb 2017 10:49:05 GMT', 'content-type': 'application/x-amz-json-1.0'}}}

SAMPLE_SCAN_OK = {'Items': {
    'RetryAttempts': 0, 'HTTPStatusCode': 200, 'RequestId': 'xxx', 'HTTPHeaders': {
        'x-amzn-requestid': 'xxx', 'content-length': '2', 'server': 'Server',
        'connection': 'keep-alive', 'x-amz-crc32': '2745614147',
        'date': 'Fri, 10 Feb 2017 10:49:05 GMT', 'content-type': 'application/x-amz-json-1.0'}}}


def test_remove_all_team_repo_access():
    """Test DynamoDBHelper remove_all_team_repo_access
    """

    # Test create_client
    assert DynamoDBHelper.create_client(profile_name=None, region="ap-southeast-2")

    # Test DynamoDBHelper
    helper = DynamoDBHelper(
        profile_name=None,
        users_table_name="sample_users",
        users_table_key="gmail",
        logger=test_logger
    )

    # Mock functions' outputs
    helper.table.query = Mock(return_value=SAMPLE_QUERY_OK)
    helper.table.put_item = Mock(return_value=SAMPLE_UPDATE_STATUS_OK)
    helper.table.scan = Mock(return_value=SAMPLE_SCAN_OK)

    assert helper.put_item(input_dict={"gmail": "hello", "status": "active"}) is True
    assert helper.user_exists(user_main_account="hello") is True
    assert helper.all_users()
