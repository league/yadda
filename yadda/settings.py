# yadda.settings ▪ Global configurable constants ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

from os import environ
from os.path import join

DATA_FILE = join(environ['HOME'], '.yadda.data')

HASH_ABBREV = 5
SSH = 'ssh'
DOCKER = 'docker'
