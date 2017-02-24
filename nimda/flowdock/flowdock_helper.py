"""
Flowdock helper implements a client to interact the Flowdock REST API
for user management.
https://www.flowdock.com/api
"""
from __future__ import print_function
import json
import requests

from nimda.flowdock import service_defs as DEFS


# Define constants
HEADERS = {'content-type': 'application/json'}


class FlowdockHelper(object):

    def __init__(self, email, userpass, organisation, server, logger):
        self.email = email
        self.userpass = userpass
        self.organisation = organisation
        self.server = server
        self.logger = logger

    def users(self, email_list):
        """Return a `list` of user ({'email', 'id', 'avatar', 'name', 'website'})
        """
        request_data = DEFS.get_users(self.server)
        ret = self.get_request(request_data.service_url, request_data.data)
        return [v for v in ret if v['email'] in email_list]

    def remove_user_from_organisation(self, user_id):
        """Return `True` if the user with the given `user_id` can be removed
           from the organisation; `False` otherwise
        """
        request_data = DEFS.delete_user_from_organisation(self.server, self.organisation, user_id)
        return self.delete_request(request_data.service_url, request_data.data)

    def get_request(self, service_url, service_data):
        response = requests.get(
            service_url,
            params=service_data,
            auth=(self.email, self.userpass)
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
            auth=(self.email, self.userpass)
        )
        if response.ok is False:
            self.logger.error("{}: {}".format(response.status_code, response.reason))
        return response.ok

    def delete_request(self, service_url, service_data):
        response = requests.delete(
            service_url,
            params=service_data,
            headers=HEADERS,
            auth=(self.email, self.userpass)
        )
        if response.ok is False:
            self.logger.error("{}: {}".format(response.status_code, response.reason))
        return response.ok

    def print_response(self, r):
        """Print formatted response
        """
        print('{} {}\n'.format(json.dumps(r.json(), sort_keys=True, indent=2, separators=(',', ': ')), r))
