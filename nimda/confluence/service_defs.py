"""
Specify the required Confluence REST urls for user management
See https://docs.atlassian.com/atlassian-confluence/REST/latest/
"""
from __future__ import print_function
from collections import namedtuple


RequestData = namedtuple('RequestData', 'service_url data')

# Public API route
API_URL = "{}/wiki/rest/api/{}"

# Admin API route
ADMIN_API_URL = "{}/admin/rest/um/1/user/{}"


def delete_member_from_group(server, username, groupname):
    """DELETE request for removing a member from a group
    """
    return RequestData(
        service_url= ADMIN_API_URL.format(server, 'group/direct'),
        data={
            "username": username,
            "groupname": groupname
        }
    )


def delete_app_access(server, username):
    """DELETE request for removing all confluence access of a user
    """
    return RequestData(
        service_url=ADMIN_API_URL.format(server, 'access'),
        data={
            "username": username,
            "productId": "product:confluence:conf"
        }
    )


def post_deactivate_user(server, username):
    """POST request for deactivate a user
    """
    return RequestData(
        service_url=ADMIN_API_URL.format(server, 'deactivate'),
        data={
            "username": username,
        }
    )


def get_member_groups(server, username):
    """GET request for retrieving all groups that a member is in
    """
    return RequestData(
        service_url=API_URL.format(server, 'user/memberof'),
        data={
            "username": username,
        }
    )


def get_groups(server):
    """GET request for retrieving all groups that are visiable to the auth user.
    """
    return RequestData(
        service_url= API_URL.format(server, 'group'),
        data={}
    )


def get_group_members(server, group_name):
    """GET request for retrieving all members of a group
    """
    return RequestData(
        service_url= API_URL.format(server, 'group/{}/member'.format(group_name)),
        data={}
    )
