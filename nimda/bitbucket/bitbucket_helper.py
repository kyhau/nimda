"""
Bitbucket helper
"""
from __future__ import print_function
from json import loads
from pybitbucket.auth import BasicAuthenticator
from pybitbucket.bitbucket import Client, BitbucketBase, entrypoints_json

from nimda.bitbucket.extra_entrypoints import (
    extra_entrypoints_json,
    entrypoint_url_delete_team_access_of_a_user
)


class BitbucketHelper(BitbucketBase):

    def __init__(self, username, userpass, useremail, logger):
        """Get the api routes currently supported by pybitbucket, extend with
           with additional routes we need, then create methods for them,
           which can be retrieved by calling `relationships()`
        """
        self.logger = logger
        data = loads(entrypoints_json)
        extra_data = loads(extra_entrypoints_json)
        data['_links'].update(extra_data['_links'])

        BitbucketBase.__init__(self, data=data)
        self.client = Client(BasicAuthenticator(username, userpass, useremail))

    def remove_all_team_repo_access(self, user_name, team_name):
        """Remove all access of the user of the given username
        """
        try:
            delete_access_url = entrypoint_url_delete_team_access_of_a_user(team=team_name, username=user_name)
            response = self.client.session.delete(url=delete_access_url)
            Client.expect_ok(response, 201)
        except Exception as e:
            self.logger.error(e)
            return False

        return True

    def current_team_members(self, team_name):
        """Return details all members in all Team Groups.
        :return: List of dict with keys ('username', 'website', 'display_name',
                 'uuid', 'links', 'created_on', 'location', 'type')
        """
        return sorted(
            [i for i in self.teamMembers(team=team_name)],
            key=lambda k: k['display_name']
        )
