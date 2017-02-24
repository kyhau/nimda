"""
JIRA helper
"""
from __future__ import print_function
from jira.client import JIRA


class JiraHelper(JIRA):

    def __init__(self, useremail, userpass, server, logger):
        self.logger = logger
        JIRA.__init__(
            self, basic_auth=(useremail, userpass),
            options={'server': server}
        )

    def on_board(self):
        #TODO
        # self.client.add_user(...)
        # self.client.add_user_to_group(...)
        # self.client.email_user(...)
        pass

    def remove_all_access(self, username):
        """Remove all JIRA related access
        """
        err_cnt = 0

        # 1. Remove user of username from all groups
        group_list = self.groups()
        for groupname in group_list:
            if username in self.group_members(groupname).keys():
                self.logger.info("Removing {} from group {} ...".format(username, groupname))
                if self.remove_user_from_group(username, groupname) is not True:
                    self.logger.error("Failed to remove user {} from group {}".format(username, groupname))
                    err_cnt += 1

        # 2. Revoking application access
        self.logger.info("Revoking application access (actual license count)...")
        if self.revoke_application_access(username) is False:
            err_cnt +=1

        # 3. Deactivate user (not deleting user)
        self.logger.info("Deactivating user ...")
        if self.deactivate_user(username) is False:
            self.logger.error("Failed to deactivate user")
            err_cnt += 1

        return err_cnt == 0

    def revoke_application_access(self, username):
        """Extend `JIRA` to support also revoke application access (the actual license count)
        """
        url = self._options['server'] + '/admin/rest/um/1/user/access'
        x = { "username": username, "productId": "product:jira:jira-software" }
        ret = self._session.delete(url, params=x)
        if ret.status_code != 204:
            self.logger.error("Failed to revoke application access")
            return False
        return True

    def members_in_all_groups(self):
        """Return members in all groups
        """
        all_users = {}
        for group in self.groups():
            for k, v in self.group_members(group).items():
                if k not in all_users.keys():
                    v.update({'group': [group]})
                    all_users[k] = v
                else:
                    all_users[k]['group'].append(group)
        return all_users
