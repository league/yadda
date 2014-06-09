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

def init_bare(opts, dir):
    utils.dry_call(opts, ['git', 'init', '--bare', dir])

def list_remotes():
    return subprocess.check_output(['git', 'remote']).split('\n')

def set_remote(opts, name, url):
    if name in list_remotes():
        utils.dry_call(opts, ['git', 'remote', 'set-url', name, url])
    else:
        utils.dry_call(opts, ['git', 'remote', 'add', name, url])
