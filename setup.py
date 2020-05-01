from __future__ import absolute_import, division, print_function
from setuptools import setup, find_packages
import os

base_dir = os.path.dirname(__file__)
__title__ = "nimda"
__version__ = "0.1.0"
__summary__ = "Admin task helper"
__author__ = "Kay Hau"
__requirements__ = [
    'boto3==1.4.4',         # dynamodb
    'jira==1.0.10',         # jira
    'pybitbucket==0.12.0',  # bitbucket
    'requests-oauthlib==0.8.0', # pybitbucket dependency
    'six==1.14.0',
]

entry_points = {
    'console_scripts': [
        'offboard = nimda.offboard_main:main',
    ]
}

setup(
    name=__title__,
    version=__version__,
    description=__summary__,
    packages=find_packages(exclude=['tests']),
    author=__author__,
    zip_safe=False,
    install_requires=__requirements__,
    entry_points=entry_points,
)
