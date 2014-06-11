# yadda.docker ▪ Python interface to docker commands ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

from yadda import utils
import os
import subprocess
import sys
import tempfile

class Docker(object):
    def __init__(self, subprocess, filesystem, stdout=None):
        self.subprocess = subprocess
        self.filesystem = filesystem
        self.stdout = stdout

    def build(self, tag, dir='.'):
        cmd = ' '.join(['docker', 'build', '-t',
                        utils.shell_quote(tag),
                        utils.shell_quote(dir)])
        with self.filesystem.tempname() as tmp:
            p1 = self.subprocess.Popen(cmd + ' 2>&1', # merge stderr with stdout
                                       shell = True,
                                       stdout = self.subprocess.PIPE)
            p2 = self.subprocess.Popen(['tee', tmp],
                                       stdin = p1.stdout,
                                       stdout = self.stdout)
            p1.stdout.close()
            p2.communicate()
            status = p1.wait()
            try:
                with self.filesystem.open(tmp, 'r') as h:
                    return (status, h.read())
            except IOError:
                return (status, '')
