"""
App's main
"""
from __future__ import print_function
import datetime
import os
import sys
import traceback

from nimda.services import (
    BitbucketService,
    ConfluenceService,
    FlowdockService,
    JenkinsService,
    JiraService,
    UserAccountService as UserAccs
)
from nimda.utils import (
    prepare_logger,
    read_config_from_argv,
)
from nimda import (
    ATTR_STATUS,
    ATTR_STATUS_SUSPENDED,
    ATTR_STATUS_TRANSFERRED
)

# APP Name
APP_NAME = os.path.basename(__file__).split('.')[0]

###############################################################################
# Define all services currently supported

SERVICES_REPORT = [
    BitbucketService,
    JiraService,
    ConfluenceService,
    FlowdockService,
    JenkinsService,
]

# Services currently supported off boarding automation
SERVICES_OFF_BOARD = SERVICES_REPORT

# Services we need to do off boarding for people transferring to other business group
# E.g. Do not remove Google, Flowdock, Confluence accounts but remove them from certain "groups"
SERVICES_TRANSFER = [
    BitbucketService,
    JiraService,
    JenkinsService,
]


def reporting(user_acc_service, configs, app_logger):
    """Write reports for each service and also the database
    """
    for service in SERVICES_REPORT:
        app_logger.info("############################################################")
        app_logger.info("Reporting {} users ...".format(service.database_attr_name()))
        service(configs, app_logger).summary(user_acc_service.users)

    # Database
    app_logger.info("############################################################")
    app_logger.info("Reporting users in database ...")
    user_acc_service.summary()


def off_board_user(user_acc_service, username, new_status, services, configs, app_logger):
    """Off board user of `username` from these `services`.
       `new_status` can be `suspended` or `transferred`.
    """
    # Retrieve all accounts that the user of `username` currently has
    user_accs_dict = user_acc_service.users[username]

    # Update dynamodb user's status to `new_status` first.
    user_accs_dict[ATTR_STATUS] = new_status

    # Start off boarding user from each service
    updated = False
    for service in services:
        app_logger.info("Checking {} ...".format(service.database_attr_name()))
        if service.database_attr_name() in user_accs_dict.keys():
            service_obj = service(configs, app_logger)

            # Retrieve the corresponding acc name and also remove it from `user_accs_dict`
            acc_name = user_accs_dict.pop(service.database_attr_name())
            service_obj.off_board(acc_name)
            updated = True

    if updated is True:
        # Update database record of this user
        app_logger.info("Updating database record ...")
        user_acc_service.off_board(user_accs_dict)
    else:
        app_logger.info("No change has been made")

def get_action_params(args):
    """Determine what action to do
    """
    if args.offboard is not None:
        return {
            'username': args.offboard,
            'new_status': ATTR_STATUS_SUSPENDED,
            'services': SERVICES_OFF_BOARD
        }
    if args.transfer is not None:
        return {
            'username': args.transfer,
            'new_status': ATTR_STATUS_TRANSFERRED,
            'services': SERVICES_TRANSFER
        }
    return None


def start_process(configs, action_params=None):
    """Off board user from these services if `offboard_username` is specified;
       otherwise just report current status of user accounts
    """
    output_dir = configs.get('app', 'app.output_dir')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    logfile = os.path.join(output_dir, configs.get('app', 'app.logfile'))
    app_logger = prepare_logger(APP_NAME, logfile)
    app_logger.info("Start time: {}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    try:
        # Get all existing users' accounts first
        user_acc_service = UserAccs(configs, app_logger)

        if action_params is None:
            # Do reporting
            reporting(user_acc_service, configs, app_logger)
        else:
            # Do off boarding (or transferring people to other business group)
            username = action_params['username']
            new_status = action_params['new_status']
            services = action_params['services']

            if username not in user_acc_service.users.keys():
                app_logger.error("{} not found in database. Aborted.".format(username))
                return 1

            off_board_user(user_acc_service, username, new_status, services, configs, app_logger)

    except Exception as e:
        app_logger.error(e)
        traceback.print_exc()
        return 1
    app_logger.info("End time: {}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    return 0


def main():
    """Entry point of the app.
    """
    configs, args = read_config_from_argv(sys.argv[1:])
    if configs is None:
        sys.exit(1)

    return start_process(configs, action_params=get_action_params(args))

if __name__ == "__main__":
    sys.exit(main())
