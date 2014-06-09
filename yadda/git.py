# yadda.git ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

from yadda import utils
import os.path
import subprocess

def has_dot_git(dir='.'):
    g = os.path.join(dir, '.git')
    return os.path.isdir(g)

def set_yadda_app(opts, name):
    assert(utils.is_slug(name))
    utils.dry_call(opts, ['git', 'config', '--local', 'yadda.app', name])

def get_yadda_app():
    try:
        return subprocess.check_output(['git', 'config', '--local',
                                        'yadda.app']).rstrip()
    except subprocess.CalledProcessError:
        raise KeyError
