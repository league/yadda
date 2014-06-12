# yadda.subproc ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

import logging
import subprocess

log = logging.getLogger('yadda')

class BaseSubprocess(object):
    def logCmd(self, cmd):
        if log.isEnabledFor(logging.INFO):
            log.info(self.logSkip() +
                     ' '.join(cmd) if isinstance(cmd, list) else cmd)

    def check_call(self, cmd, *args, **kwargs):
        self.logCmd(cmd)

    def check_output(self, cmd, *args, **kwargs):
        self.logCmd(cmd)

    def Popen(self, cmd, *args, **kwargs):
        self.logCmd(cmd)

class NopSubprocess(BaseSubprocess):
    def logSkip(self):
        return '(skip) '

class RealSubprocess(BaseSubprocess):
    def logSkip(self):
        return ''

    def check_call(self, cmd, *args, **kwargs):
        self.logCmd(cmd)
        return subprocess.check_call(cmd, *args, **kwargs)

    def check_output(self, cmd, *args, **kwargs):
        self.logCmd(cmd)
        return subprocess.check_output(cmd, *args, **kwargs)

    def Popen(self, cmd, *args, **kwargs):
        self.logCmd(cmd)
        return subprocess.Popen(cmd, *args, **kwargs)
