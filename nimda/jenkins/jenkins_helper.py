"""
Jenkins helper implements a client to interact the Jenkins REST API
for user management.
"""
from __future__ import print_function
import requests

from nimda.jenkins import service_defs as DEFS


# Define constants
HEADERS = {'content-type': 'application/json'}


class JenkinsHelper(object):

    def __init__(self, username, userpass, server, logger):
        self.username = username
        self.userpass = userpass
        self.server = server
        self.logger = logger

    def active_users(self, users_ids=None):
        """Return a `list` containing active users' ids
        """
        jenkins_users_ids = users_ids

        if jenkins_users_ids is None:
            # Retrieve all Jenkins users (active or `deleted`)
            jenkins_users_ids = self.all_users()

        # Retrieve active users
        active_users_ids = []
        for user_id in jenkins_users_ids:
            if self.is_user_active(user_id) is True:
                active_users_ids.append(user_id)

        return active_users_ids

    def all_users(self):
        """Retrieve all Jenkins users (active or `deleted`)
          Jenkins does not really delete user, but hides it from "views".
        """
        request_data = DEFS.get_users(self.server)
        ret = self.get_request(request_data.service_url, request_data.data)

        jenkins_users_ids = [
            u['user']['absoluteUrl'].replace('{}/user/'.format(self.server), '') \
            for u in ret['users']
        ] if 'users' in ret else []
        return jenkins_users_ids

    def is_user_active(self, user_id):
        """Retrieve details of a user and determine if it is active or 'deleted' (in fact just hidden).
        """
        request_data = DEFS.get_user(self.server, user_id)
        ret = self.get_request(request_data.service_url, request_data.data)

        # If this user has the following property, it means this user is active (not deleted).
        in_view = [
            p for p in ret['property'] \
            if p['_class'] == "hudson.security.HudsonPrivateSecurityRealm$Details"
        ]
        return len(in_view) > 0

    def remove_user(self, user_id):
        """Return `True` if the user with the given `user_id` can be removed
           from the organisation; `False` otherwise
        """
        request_data = DEFS.post_do_delete_user(self.server, user_id)
        try:
            ret = self.post_request(request_data.service_url, request_data.data)
        except requests.exceptions.ConnectionError as e:
            # Because Jenkins API is crap
            if 'Caused by NewConnectionError' not in e.message:
                self.logger.error(e)
                return False

            # Double checking if the user is inactive
            ret = (self.is_user_active(user_id) is False)

        self.logger.info("Checking: Has {} been deactivated? {}".format(user_id, ret))
        return ret

    def get_request(self, service_url, service_data):
        response = requests.get(
            service_url,
            params=service_data,
            auth=(self.username, self.userpass)
        )
        if response.ok is False:
            self.logger.error("{}: {}".format(response.status_code, response.reason))
            return []
        return response.json()

    def post_request(self, service_url, service_data):
        response = requests.post(
            service_url,
            params=service_data,
            headers=HEADERS,
            auth=(self.username, self.userpass)
        )
        if response.ok is False:
            self.logger.error("{}: {}".format(response.status_code, response.reason))
        return response.ok
