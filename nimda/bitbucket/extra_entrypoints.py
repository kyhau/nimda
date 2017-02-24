"""
This file intends to extend bitbucket.org/atlassian/python-bitbucket/pybitbucket/entrypoints.py
which is mix of v1 and v2 routes and are incomplete.

Please check if new routes are being added to the latest original entrypoints.py.
"""
from __future__ import unicode_literals


extra_entrypoints_json = """
{
  "_links": {
    "teamMembers": {
      "href": "https://api.bitbucket.org/2.0/teams{/team}/members"
    }
  }
}
"""


def entrypoint_url_delete_team_access_of_a_user(team, username):
    """Bitbucket internal api route for removing all access of a user in a Bitbucket Team.
    """
    return "https://bitbucket.org/!api/internal/user/{}/access/{}".format(team, username)
