#!/bin/bash
echo "TEST_BUILD: Create virtual env and install tox and docker"
# Set to fail script if any command fails.
set -e
rm -rf env
virtualenv env
. env/bin/activate

echo "TEST_BUILD: Install dependencies for running tox, wheel and pytests"
pip install -r requirements-build.txt
# run the python tests
tox -r

echo "TEST_BUILD: Run pylint tests and generate pylint.log for Jenkins"
# and output to console
echo "Need to install dependencies for pylint to validate the usage of packages"
pip install -e .
pylint --rcfile=.pylintcfg module > pylint.log || true

# Leave virtual environment
deactivate
