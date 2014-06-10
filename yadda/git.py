# yadda.git ▪ Python interface to git commands ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

from yadda import utils
import os.path
import subprocess
import sys

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

def receive_master_commit():
    '''Parse the standard input for a git receive hook.
Answer the commit hash for an update to master, if any.'''
    # For each ref updated: <old-value> SP <new-value> SP <ref-name> LF
    for line in sys.stdin:
        old, new, ref = line.split()
        if ref == 'refs/heads/master':
            return new
