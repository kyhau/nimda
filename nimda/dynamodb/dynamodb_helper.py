import boto3
from boto3.dynamodb.conditions import Key


DEFAULT_REGION = 'ap-southeast-2'


def init_session(profile_name):
    """Return an aws session for the given aws profile
    """
    return boto3.session.Session(profile_name=profile_name)


class DynamoDBHelper(object):
    def __init__(self, profile_name, users_table_name, users_table_key, logger):
        self.logger = logger
        self.client = self.create_client(profile_name=profile_name)
        self.table = self.client.Table(users_table_name)
        self.table_key = users_table_key

    @staticmethod
    def create_client(profile_name=None, region=DEFAULT_REGION):
        """Return a dynamodb client
        """
        if profile_name is None:
            return boto3.resource('dynamodb', region_name=region)
        return init_session(profile_name).resource('dynamodb', region_name=region)

    def user_exists(self, user_main_account):
        """Return True if `user_main_account` does exist in the database; False otherwise.
        """
        response = self.table.query(
            KeyConditionExpression=Key(self.table_key).eq(user_main_account)
        )
        return response['Count']>0

    def put_item(self, input_dict):
        """Put item (add new or override existing item) into the database
        """
        try:
            ret = self.table.put_item(Item=input_dict)
            self.logger.debug(ret)
        except Exception as e:
            self.logger(e)
            return False
        return True

    def all_users(self):
        """Return list of user accounts (dict):
        """
        try:
            return self.table.scan()['Items']
        except Exception as e:
            self.logger.error(e)
        return []
