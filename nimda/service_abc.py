"""
Define abstract class for implementing supported off/on boarding services.
"""
import abc
import os
import six

from nimda import (
    ATTR_STATUS,
    ATTR_STATUS_ACTIVE,
    ATTR_STATUS_TRANSFERRED
)


@six.add_metaclass(abc.ABCMeta)
class ServiceABC():
    def __init__(self, config, logger):
        """Read configurations from `config`
        """
        self.logger = logger
        self.output_dir = config.get('app', 'app.output_dir')
        self._init_with_config(config=config)

    @staticmethod
    def database_attr_name():
        """Database attribute name
        """
        pass

    @abc.abstractmethod
    def _init_with_config(self, config):
        """Read configurations from `config`
        """
        pass

    @abc.abstractmethod
    def on_board(self, input_dict):
        """Start on boarding and return True if succeeded; False otherwise
        """
        pass

    @abc.abstractmethod
    def off_board(self, user_data):
        """Start off boarding and return True if succeeded; False otherwise
        """
        pass

    @abc.abstractmethod
    def summary(self, db_users_dict):
        """Retrieve current user details and compare against the database users' details.
        """
        pass

    def report_inactive_users_still_have_access(self, db_users_dict):
        """ Identify inactive (i.e. not active or transferred) users still have access
        """
        off_board_cnt = 0
        db_service_users = [v for v in db_users_dict.values() if self.database_attr_name() in v.keys() ]
        for v in db_service_users:
            if v[ATTR_STATUS] not in [
                ATTR_STATUS_ACTIVE,
                ATTR_STATUS_TRANSFERRED
            ]:
                off_board_cnt += 1
                self.logger.warning("{} user {} should be off boarded".format(
                    self.database_attr_name(), v[self.database_attr_name()]))
        return off_board_cnt

    def write_users_to_file(self, users, output_file):
        """Write current users to file
        """
        filename = os.path.join(self.output_dir, output_file)

        self.logger.info("Writing {} ...".format(filename))

        with open(filename, "w") as text_file:

            if type(users) is dict:
                for k, v in users.items():
                    v.update({'username': k})
                    text_file.write('{}\n'.format(v))
            else:
                for user in users:
                    text_file.write('{}\n'.format(user))
