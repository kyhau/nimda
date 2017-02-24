"""
Specify the required Flowdock REST urls for user management
See https://www.flowdock.com/api/rest
"""
from __future__ import print_function
from collections import namedtuple


RequestData = namedtuple('RequestData', 'service_url data')


def get_users(server):
    """GET request for retrieving all users.
    """
    return RequestData(
        service_url= "{}/users".format(server),
        data={}
    )


def delete_user_from_organisation(server, organisation, userid):
    """DELETE request for removing a user from the organisation.
    """
    return RequestData(
        service_url= "{}/organizations/{}/users/{}".format(server, organisation, userid),
        data={}
    )
