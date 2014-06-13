# yadda.docker ▪ Python interface to docker commands ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

import re

class Docker(object):
    def __init__(self, subprocess, filesystem, stdout=None):
        self.subprocess = subprocess
        self.filesystem = filesystem
        self.stdout = stdout

    def build(self, tag, dir='.'):
        cmd = ' '.join(['docker', 'build', '-t',
                        shell_quote(tag),
                        shell_quote(dir)])
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

SHELL_QUOTABLE = re.compile('^[ -_0-9a-zA-Z:/]*$')

def shell_quote(word):
    assert SHELL_QUOTABLE.match(word), 'quoting %r not supported' % word
    return "'" + word + "'"
