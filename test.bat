@ECHO OFF
:: All commands halt the build and throw an error value.
echo "TEST_BUILD: Create virtual env and install tox and docker"
virtualenv env || exit /b 1
CALL env\Scripts\activate.bat || exit /b 2

echo "TEST_BUILD: Install deps for running tox, wheel and pytests"
python -m pip install -r requirements-build.txt --upgrade || exit /b 3
echo "Run tests and coverage"
tox -r || exit /b 4

echo "TEST_BUILD: Run pylint tests and generate pylint.log for Jenkins"
:: and output to console
echo "Need to install deps for pylint to validate the usage of packages"
pip install -e .

pylint --rcfile=.pylintcfg module > pylint.log

:: Leave build venv
deactivate || exit /b 5

EXIT /B 0
