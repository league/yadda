# yadda.git ▪ Python interface to git commands ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

from os.path import join
import sys

class Git(object):
    def __init__(self, filesystem, subprocess):
        self.filesystem = filesystem
        self.subprocess = subprocess

    def is_working_dir(self, dir='.'):
        return self.filesystem.isfile(join(dir, join('.git', 'config')))

    def set_local_config(self, key, value):
        self.subprocess.check_call(['git', 'config', '--local', key, value])

    def get_local_config(self, key):
        try:
            return self.subprocess.check_output(
                ['git', 'config', '--local', key]).rstrip()
        except self.subprocess.CalledProcessError:
            raise KeyError

    def init_bare(self, dir='.'):
        self.subprocess.check_call(['git', 'init', '-q', '--bare', dir])

    def list_remotes(self):
        return self.subprocess.check_output(['git', 'remote']).rsplit()

    def set_remote(self, name, url):
        if name in self.list_remotes():
            self.subprocess.check_call(['git', 'remote', 'set-url', name, url])
        else:
            self.subprocess.check_call(['git', 'remote', 'add', name, url])

    def receive_master_commit(self, stdin):
        '''Parse the standard input for a git receive hook.
    Answer the commit hash for an update to master, if any.'''
        # For each ref updated: <old-value> SP <new-value> SP <ref-name> LF
        for line in stdin:
            old, new, ref = line.split()
            if ref == 'refs/heads/master':
                return new

    def export(self, commitish, dest):
        self.subprocess.check_call(
            'git archive "%s" | tar -x -C "%s"' % (commitish, dest),
            shell=True
        )
