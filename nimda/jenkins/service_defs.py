"""
Specify the required Jenkins REST urls for user management
"""
from __future__ import print_function
from collections import namedtuple


RequestData = namedtuple('RequestData', 'service_url data')


def get_user(server, user_id):
    """GET request for retrieving details of a user.
    """
    return RequestData(
        service_url= "{}/user/{}/api/json".format(server, user_id),
        data={}
    )


def get_users(server):
    """GET request for retrieving all users.
    """
    return RequestData(
        service_url= "{}/asynchPeople/api/json".format(server),
        data={}
    )


def post_do_delete_user(server, user_id):
    """POST request for deleting an user from Jenkins.

    Note: Jenkins does not delete user, but hides user from Views.
    """
    # return 302
    return RequestData(
        service_url= "{}/user/{}/doDelete".format(server, user_id),
        data={}
    )
