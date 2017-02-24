"""
Confluence helper implements a client to interact the Confluence REST API
for user management.
See also https://docs.atlassian.com/atlassian-confluence/REST/latest/
"""
from __future__ import print_function
import json
import requests

from nimda.confluence import service_defs as DEFS


# Define constants
HEADERS = {'content-type': 'application/json'}


class ConfluenceHelper(object):

    def __init__(self, username, userpass, server, logger):
        self.username = username
        self.userpass = userpass
        self.server = server
        self.logger = logger

    def groups(self):
        """Return a `list` containing names of groups
        """
        request_data = DEFS.get_groups(self.server)
        return [g['name'] for g in self.get_request(request_data.service_url, request_data.data)]

    def group_members(self, groupname):
        """Return a `list` of members of a group (in `dict` with keys `username`, `displayName` and `userKey`)
        """
        request_data = DEFS.get_group_members(self.server, groupname)
        return self.get_request(request_data.service_url, request_data.data)

    def member_groups(self, username):
        """Return a `list` of group names of a member
        """
        request_data = DEFS.get_member_groups(self.server, username)
        return [g['name'] for g in self.get_request(request_data.service_url, request_data.data)]

    def remove_member_from_group(self, username, groupname):
        """Return `True` if the member can be removed from the group; `False` otherwise
        """
        request_data = DEFS.delete_member_from_group(self.server, username, groupname)
        return self.delete_request(request_data.service_url, request_data.data)

    def revoke_application_access(self, username):
        """Return `True` if succeeded; `False` otherwise
        """
        request_data = DEFS.delete_app_access(self.server, username)
        return self.delete_request(request_data.service_url, request_data.data)

    def deactivate_user(self, username):
        """Return `True` if succeeded; `False` otherwise
        """
        request_data = DEFS.post_deactivate_user(self.server, username)
        return self.post_request(request_data.service_url, request_data.data)

    def remove_all_access(self, username):
        """Remove all Confluence access
        """
        err_cnt = 0

        # 1. Remove user of username from all groups
        for groupname in self.member_groups(username):
            self.logger.info("Removing {} from group {} ...".format(username, groupname))
            if self.remove_member_from_group(username, groupname) is not True:
                self.logger.error("Failed to remove user {} from group {}".format(username, groupname))
                err_cnt += 1

        # 2. Revoking application access
        self.logger.info("Revoking application access (actual license count)...")
        if self.revoke_application_access(username) is False:
            err_cnt += 1

        # 3. Deactivate user (not deleting user)
        self.logger.info("Deactivating user ...")
        if self.deactivate_user(username) is False:
            self.logger.error("Failed to deactivate user")
            err_cnt += 1

        return err_cnt == 0

    def members_in_all_groups(self):
        """Return members in all groups
        """
        users = {}
        group_names = self.groups()
        for group_name in group_names:
            self.logger.info('Checking group {} ...'.format(group_name))
            for user in self.group_members(group_name):
                if user['username'] in users.keys():
                    users[user['username']]['groups'].append(group_name)
                else:
                    users[user['username']] = {'displayName': user['displayName'], 'groups': [group_name]}
        return users

    def get_request(self, service_url, service_data):
        response = requests.get(
            service_url,
            params=service_data,
            auth=(self.username, self.userpass)
        )
        if response.ok is False:
            self.logger.error("{}: {}".format(response.status_code, response.reason))
            return []
        return response.json()['results']

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

    def delete_request(self, service_url, service_data):
        response = requests.delete(
            service_url,
            params=service_data,
            headers=HEADERS,
            auth=(self.username, self.userpass)
        )
        if response.ok is False:
            self.logger.error("{}: {}".format(response.status_code, response.reason))
        return response.ok

    def print_response(self, r):
        """Print formatted response
        """
        print('{} {}\n'.format(json.dumps(r.json(), sort_keys=True, indent=2, separators=(',', ': ')), r))


