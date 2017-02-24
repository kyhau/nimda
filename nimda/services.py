"""
Define all current supported off/on boarding services
"""
from __future__ import print_function
import os
from collections import defaultdict

from nimda.bitbucket.bitbucket_helper import BitbucketHelper
from nimda.confluence.confluence_helper import ConfluenceHelper
from nimda.dynamodb.dynamodb_helper import DynamoDBHelper
from nimda.flowdock.flowdock_helper import FlowdockHelper
from nimda.jenkins.jenkins_helper import JenkinsHelper
from nimda.jira_client.jira_helper import JiraHelper
from nimda.service_abc import ServiceABC
from nimda.utils import read_multi_lines_config, write_to_json_file
from nimda import (
    ATTR_STATUS,
    ATTR_STATUS_ACTIVE,
)


################################################################################
# DynamoDB and management of user accounts' objects
class UserAccountService(ServiceABC):
    TABLE_NAME = "UserAccounts"
    TABLE_KEY = "gmail"

    @staticmethod
    def database_attr_name():
        """Database attribute name
        """
        return UserAccountService.TABLE_KEY

    def _init_with_config(self, config):
        """Read configurations from `config`
        """
        self.profile = config.get("dynamodb", "dynamodb.aws_profile_name")
        self.app = DynamoDBHelper(self.profile, self.TABLE_NAME, self.TABLE_KEY, self.logger)
        self.output_file = "DatabaseUserAccountsSummary.json"

        # Retrieve user details the first time
        self.users = self.all_users(input_dict=None)

    def on_board(self, input_dict):
        """Start on boarding and return True if succeeded; False otherwise
        """
        return self.app.put_item({
            self.TABLE_KEY: input_dict[self.TABLE_KEY],
            ATTR_STATUS: ATTR_STATUS_ACTIVE
        })

    def off_board(self, user_data):
        """Update database with the given `user_data` (dict) and return True if
           succeeded; False otherwise
        """
        return self.app.put_item(user_data)

    def all_users(self, input_dict=None):
        """Retrieve current user in {TABLE_KEY: { attr1: account_name1, etc}}
        """
        users = defaultdict(dict)
        for user_accounts_dict in self.app.all_users():
            users[user_accounts_dict[self.TABLE_KEY]] = user_accounts_dict
        return users

    def summary(self, db_user_dict=None):
        """Write latest users' accounts details to json file
        """
        self.write_users_to_file(self.users, self.output_file)

        active_users = [
            u for u in self.users.values() \
            if u[ATTR_STATUS] == ATTR_STATUS_ACTIVE
        ]
        self.logger.info("Summary:")
        self.logger.info("Total users: {}".format(len(self.users.keys())))
        self.logger.info("Active users: {}".format(len(active_users)))

    def write_users_to_file(self, users, output_file):
        """Write current users to file
        """
        filename = os.path.join(self.output_dir, output_file)
        self.logger.info("Writing {} ...".format(filename))
        write_to_json_file(data=users, filename=filename)


################################################################################
# Bitbucket
class BitbucketService(ServiceABC):

    @staticmethod
    def database_attr_name():
        """Database attribute name
        """
        return "bitbucket"

    def _init_with_config(self, config):
        """Read configurations from `config`
        """
        self.bitbucket_teams = read_multi_lines_config(config, "bitbucket", "bitbucket.teams", logger=self.logger)
        self.username = config.get("bitbucket", "bitbucket.username")
        self.userpass = config.get("bitbucket", "bitbucket.password")
        self.useremail = config.get("bitbucket", "bitbucket.email")
        self.app = BitbucketHelper(self.username, self.userpass, self.useremail, self.logger)

    def on_board(self, input_dict):
        """Start on boarding and return True if succeeded; False otherwise
        """
        # TODO
        self.logger.debug("TODO: BitbucketService.on_board")
        pass

    def off_board(self, user_data):
        """Start off boarding and return True if succeeded; False otherwise
        """
        user_name = user_data

        err_cnt = 0
        for team_name in self.bitbucket_teams:
            self.logger.debug("Removing {} 's access of team {} repos ...".format(user_name, team_name))
            if self.app.remove_all_team_repo_access(user_name, team_name) is False:
                err_cnt += 1
        return err_cnt==0

    def summary(self, db_users_dict=None):
        """Retrieve current user details and compare against the database users' details.
        """
        db_bitbucket_users = None
        if db_users_dict is not None:
            # Find all db users who has bitbucket account
            db_bitbucket_users = [
                v[self.database_attr_name()] for v in db_users_dict.values() if self.database_attr_name() in v.keys()
            ]

        for team_name in self.bitbucket_teams:
            user_list = self.app.current_team_members(team_name)

            # Write current users to a file
            self.write_users_to_file(user_list, "BitbucketUsers-{}.csv".format(team_name))

            # Identify bitbucket users not in our database
            not_in_db_cnt = self.report_users_not_in_database(db_bitbucket_users, user_list, team_name)

            self.logger.info("Summary:")
            self.logger.info("{}: Total users: {}".format(team_name, len(user_list)))
            self.logger.info("{}: Total users not in DB: {}".format(team_name, not_in_db_cnt))

    def report_users_not_in_database(self, db_bitbucket_users, user_list, team_name):
        not_in_db_cnt = 0
        if db_bitbucket_users is not None:
            for bb_username in [user["username"] for user in user_list]:
                if bb_username not in db_bitbucket_users:
                    not_in_db_cnt += 1
                    self.logger.warning("Bitbucket team {} user {} not in database".format(team_name, bb_username))
        return not_in_db_cnt

    def write_users_to_file(self, users, output_file):
        """Write current users to file
        """
        filename = os.path.join(self.output_dir, output_file)
        with open(filename, "w") as text_file:
            self.logger.info("Writing {} ...".format(filename))
            for user in users:
                text_file.write(",".join(
                    [user["display_name"], user["username"], user["created_on"], user["uuid"]]
                ) + "\n")


################################################################################
# JIRA
class JiraService(ServiceABC):

    @staticmethod
    def database_attr_name():
        """Database attribute name
        """
        return "jira"

    def _init_with_config(self, config):
        """Read configurations from `config`
        """
        self.useremail = config.get("jira", "jira.email")
        self.userpass = config.get("jira", "jira.password")
        self.server = config.get("jira", "jira.server")
        self.app = JiraHelper(self.useremail, self.userpass, self.server, self.logger)
        self.output_file = "JiraUsers.csv"

    def on_board(self, input_dict):
        """Start on boarding and return True if succeeded; False otherwise
        """
        # TODO
        self.logger.debug("TODO: JiraService.on_board")
        pass

    def off_board(self, user_data):
        """Start off boarding and return True if succeeded; False otherwise
        """
        username = user_data
        self.logger.debug("Off boarding {} user {} ...".format(JiraService.database_attr_name(), username))
        return self.app.remove_all_access(username)

    def summary(self, db_users_dict):
        """Retrieve current user details and compare against the database users' details.
        """
        all_users = self.app.members_in_all_groups()

        self.write_users_to_file(all_users, self.output_file)

        # Identify inactive users still have jira access
        off_board_cnt = self.report_inactive_users_still_have_access(db_users_dict)

        # Identify jira users not in our database
        db_jira_users = [v for v in db_users_dict.values() if self.database_attr_name() in v.keys() ]
        not_in_db_cnt = self.report_users_not_in_database(db_jira_users, all_users)

        self.logger.info("Summary:")
        self.logger.info("Total users: {}".format(len(all_users.keys())))
        self.logger.info("Total users should be off boarded: {}".format(off_board_cnt))
        self.logger.info("Total users not in DB: {}".format(not_in_db_cnt))

    def report_users_not_in_database(self, db_jira_users, all_jira_users):
        not_in_db_cnt = 0
        db_jira_usernames = [v[self.database_attr_name()] for v in db_jira_users]
        for username in all_jira_users.keys():
            if username not in db_jira_usernames:
                not_in_db_cnt += 1
                self.logger.warning("JIRA user {} not in database".format(username))
        return not_in_db_cnt


################################################################################
# Confluence
class ConfluenceService(ServiceABC):

    @staticmethod
    def database_attr_name():
        """Database attribute name
        """
        return "confluence"

    def _init_with_config(self, config):
        """Read configurations from `config`
        """
        self.username = config.get("confluence", "confluence.username")
        self.userpass = config.get("confluence", "confluence.password")
        self.server = config.get("confluence", "confluence.server")
        self.app = ConfluenceHelper(self.username, self.userpass, self.server, self.logger)
        self.output_file = "ConfluenceUsers.csv"

    def on_board(self, input_dict):
        """Start on boarding and return True if succeeded; False otherwise
        """
        # TODO
        self.logger.debug("TODO: ConfluenceService.on_board")
        pass

    def off_board(self, user_data):
        """Start off boarding and return True if succeeded; False otherwise
        """
        username = user_data
        self.logger.debug("Off boarding {} user {} ...".format(ConfluenceService.database_attr_name(), username))
        return self.app.remove_all_access(username)

    def summary(self, db_users_dict):
        """Retrieve current user details and compare against the database users' details.
        """
        # Write current users to a file
        all_users = self.app.members_in_all_groups()
        self.write_users_to_file(all_users, self.output_file)

        # Identify inactive users still have confluence access
        off_board_cnt = self.report_inactive_users_still_have_access(db_users_dict)

        self.logger.info("Summary:")
        self.logger.info("Total users: {}".format(len(all_users.keys())))
        self.logger.info("Total users should be off boarded: {}".format(off_board_cnt))


################################################################################
# Flowdock
class FlowdockService(ServiceABC):

    @staticmethod
    def database_attr_name():
        """Database attribute name
        """
        return "flowdock"

    def _init_with_config(self, config):
        """Read configurations from `config`
        """
        self.email = config.get("flowdock", "flowdock.email")
        self.userpass = config.get("flowdock", "flowdock.password")
        self.server = config.get("flowdock", "flowdock.server")
        self.organisation = config.get("flowdock", "flowdock.organisation")
        self.app = FlowdockHelper(self.email, self.userpass, self.organisation, self.server, self.logger)
        self.output_file = "FlowdockUsers.csv"

    def on_board(self, input_dict):
        """Start on boarding and return True if succeeded; False otherwise
        """
        # TODO
        self.logger.debug("TODO: FlowdockService.on_board")
        pass

    def off_board(self, user_data):
        """Start off boarding and return True if succeeded; False otherwise
        """
        user_id = user_data
        self.logger.debug("Off boarding {} user {} ...".format(FlowdockService.database_attr_name(), user_data))
        return self.app.remove_user_from_organisation(user_id)

    def summary(self, db_users_dict):
        """Retrieve current user details and compare against the database users' details.
        """
        # Write current users to a file
        db_users_emails = ['{}@{}.com'.format(
            v[UserAccountService.TABLE_KEY], self.organisation) for v in db_users_dict.values()]
        all_users = self.app.users(db_users_emails)
        self.write_users_to_file(all_users, self.output_file)

        # Identify inactive users still have flowdock access
        off_board_cnt = self.report_inactive_users_still_have_access(db_users_dict)

        self.logger.info("Summary:")
        self.logger.info("Total users: {}".format(len(all_users)))
        self.logger.info("Total users should be off boarded: {}".format(off_board_cnt))


################################################################################
# Jenkins
class JenkinsService(ServiceABC):

    @staticmethod
    def database_attr_name():
        """Database attribute name
        """
        return "jenkins"

    def _init_with_config(self, config):
        """Read configurations from `config`
        """
        self.username = config.get("jenkins", "jenkins.username")
        self.userpass = config.get("jenkins", "jenkins.password")
        self.server = config.get("jenkins", "jenkins.server")
        self.app = JenkinsHelper(self.username, self.userpass, self.server, self.logger)
        self.output_file = "JenkinsUsers.csv"

    def on_board(self, input_dict):
        """Start on boarding and return True if succeeded; False otherwise
        """
        # TODO
        self.logger.debug("TODO: JenkinsService.on_board")
        pass

    def off_board(self, user_data):
        """Start off boarding and return True if succeeded; False otherwise
        """
        user_id = user_data
        self.logger.debug("Off boarding {} user {} ...".format(JenkinsService.database_attr_name(), user_data))
        return self.app.remove_user(user_id)

    def summary(self, db_users_dict):
        """Retrieve current user details and compare against the database users' details.
        """
        # Write current users to a file
        all_users = self.app.active_users()
        self.write_users_to_file(all_users, self.output_file)

        # Identify inactive users still have jenkins access
        off_board_cnt = self.report_inactive_users_still_have_access(db_users_dict)

        self.logger.info("Summary:")
        self.logger.info("Total users: {}".format(len(all_users)))
        self.logger.info("Total users should be off boarded: {}".format(off_board_cnt))
