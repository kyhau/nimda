# Nimda #

Some helper functions for on/off boarding automation.

[![Build Status](https://travis-ci.org/kyhau/nimda.svg?branch=master)](https://travis-ci.org/kyhau/nimda)

## Features

#### 1. Reporting

The reporting code is in [nimda/services.py](nimda/services.py). 
The default output folder is `output` and the default log file is `nimda.log`, 
which can be changed in the config file (see example [`config/devops.ini`](config/devops.ini)).

1. DynamoDB **`UserAccounts`**:
    1. Write user accounts' details to `DatabaseUserAccountsSummary.json`.
    1. Write the following summary to `nimda.log`:
        1. Total number of users
        1. Total number of active users
1. Bitbucket:
    1. Write current users of each Team to `BitbucketUsers-team-x.csv`.
    1. Write the following summary to `nimda.log`:
        1. Users not in database
        1. Total number of users
1. Confluence: 
    1. Write current users of all groups to `ConfluenceUsers.csv`.
    1. Write the following summary to `nimda.log`:
        1. Users shall have been off boarded (i.e. status in database is not active)
        1. Users not in database
        1. Total number of users assigned to any group
1. Flowdock: 
    1. Write current users having email address found in database to `FlowdockUsers.csv`.
    1. Write the following summary to `nimda.log`:
        1. Users shall have been off boarded (i.e. status in database is not active)
        1. Users not in database
        1. Total number of users
1. Jenkins: 
    1. Write current users of all groups to `JenkinsUsers.csv`.
    1. Write the following summary to `nimda.log`:
        1. Users shall have been off boarded (i.e. status in database is not active)
        1. Total number of users
1. JIRA: 
    1. Write current users of all groups to `JiraUsers.csv`.
    1. Write the following summary to `nimda.log`:
        1. Users shall have been off boarded (i.e. status in database is not active)
        1. Users not in database
        1. Total number of users assigned to any group

#### 2. Off-boarding

1. **UserAccounts** (DynamoDB):
    1. Set `status` from `active` to `suspended`
    1. Unset `bitbucket` attribute
    1. Unset `confluence` attribute
    1. Unset `flowdock` attribute
    1. Unset `jenkins` attribute
    1. Unset `jira` attribute

1. Bitbucket:
    1. Remove all user access (actual license counts) in the team(s).

1. Confluence:
    1. Remove user from all groups
    1. Revoke (Confluence) application access (actual license counts)
    1. Deactivate user (not deleted)

1. Flow:
    1. Remove user from the organisation

1. Jenkins:
    1. Delete user (Jenkins actually does not delete a user but hides it from all views).
    1. WON'T DO: Not removing user from Role because the api is crap and does not only requires to post all users' permission details.

1. JIRA:
    1. Remove user from all groups
    1. Revoke (JIRA) application access (actual license counts)
    1. Deactivate user (not deleted)

#### 3. Transferring

Similar to Off-boarding (at the moment), except

1. **UserAccounts** (DynamoDB):
    1. Set `status` from `active` to `transferred`
1. No Confluence off boarding (Confluence is shared with all Biarri groups)
1. No Flowdock off boarding (Flowdock is shared with all Biarri groups)

#### 4. On-boarding 

1. `UserAccounts` (DynamoDB):
    1. Set `gmail` with the given user name
    1. Set `active` to `active`
1. (TODO)


## Current Implementation

1. Use `boto3` to interact with DynamoDB.

1. Use [`pybitbucket`](https://bitbucket.org/atlassian/python-bitbucket) to interact with Bitbucket;
 require to write additional functions to support some user management functions.

1. Use `requests` to write a client to interact with [Confluence REST API](https://docs.atlassian.com/atlassian-confluence/REST/latest/). 
 <br> Note that it's the `username` required for `auth`.

1. Use `requests` to write a client to interact with [Flowdock REST API](https://www.flowdock.com/api/rest). 
 <br> Note that it's the `user email address` required for `auth`.

1. Use `requests` to write a client to interact with Jenkins API. 
 <br> Note that it's the `username` required for `auth`.

1. Use [`jira`](https://pypi.python.org/pypi/jira/) to interact with JIRA; 
 require to write additional functions to support some user management functions.
 <br> Note that it's the `user email address` required for `auth`.



## Run

1. Update the config file (see [`config/devops.ini`](config/devops.ini)).

1. `pip install` the latest version of `nimda`.

1. For reporting:

   ```bash
   nimda --config config/devops.ini 
   ```

1. To off board a user:

   ```bash
   nimda --config config/devops.ini --offboard [gmail-acc-name e.g. firstname.lastname]
   ```

1. To transfer a user to other business group:

   ```bash
   nimda --config config/devops.ini --transfer [gmail-acc-name e.g. firstname.lastname]
   ```

1. User `--help` to see all options.

## Build

*Linux*

```bash
virtualenv env
. env/bin/activate
pip install -e .
```

*Windows*
```cmd
virtualenv env
env\Scripts\activate
pip install -e .
```

## Tox Tests and Build the Wheels

*Linux*

```bash
./test.sh
```

*Windows*

```cmd
test.bat
```
