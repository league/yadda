#!/usr/bin/env python

from os.path import join, dirname
from setuptools import setup, find_packages
from subprocess import check_output

# http://blogs.nopcode.org/brainstorm/2013/05/20/pragmatic-python-versioning-via-setuptools-and-git-tags/
# Fetch version from git tags, and write to version.py.
# Also, when git is not available (PyPi package), use stored version.py.
version_py = join(dirname(__file__), join('yadda', 'version.py'))

try:
    full_cmd = 'git describe --tags --match v* --dirty=+'.split(' ')
    full_version = check_output(full_cmd).decode().rstrip()[1:]
    short_version = full_version.split('-')[0]
except:
    try:
        execfile(version_py)
        short_version = short
        full_version = full
    except:
        short_version = '99.99'
        full_version = short_version

with open(version_py, 'w') as fh:
    fh.write("""# Do not edit; generated by setup.py and git
short='%s'
full='%s'
""" % (short_version, full_version))

setup(
    name = "yadda",
    version = short_version,
    packages = find_packages(),
    test_suite = 'tests',
    tests_require = ['nose', 'coverage', 'coveralls'],
    entry_points = {
        'console_scripts': [
            'yadda = yadda.main:main',
            ],
        },
)
