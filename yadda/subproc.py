# yadda.subproc ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

import logging
import subprocess

log = logging.getLogger('yadda')

class BaseSubprocess(object):
    def logCmd(self, cmd, skip=False):
        if log.isEnabledFor(logging.INFO):
            mesg = '(skip) ' if skip else ''
            mesg += ' '.join(cmd) if isinstance(cmd, list) else cmd
            log.info(mesg)

    PIPE = subprocess.PIPE
    CalledProcessError = subprocess.CalledProcessError

class NopSubprocess(BaseSubprocess):
    def check_call(self, cmd, *args, **kwargs):
        self.logCmd(cmd, skip=True)

    def check_output(self, cmd, *args, **kwargs):
        self.logCmd(cmd, skip=True)

    def check_output_ro(self, cmd, *args, **kwargs):
        self.logCmd(cmd)
        return subprocess.check_output(cmd, *args, **kwargs)

    def Popen(self, cmd, *args, **kwargs):
        self.logCmd(cmd, skip=True)

class RealSubprocess(BaseSubprocess):

    def check_call(self, cmd, *args, **kwargs):
        self.logCmd(cmd)
        return subprocess.check_call(cmd, *args, **kwargs)

    def check_output(self, cmd, *args, **kwargs):
        self.logCmd(cmd)
        return subprocess.check_output(cmd, *args, **kwargs)

    def check_output_ro(self, cmd, *args, **kwargs):
        self.logCmd(cmd)
        return subprocess.check_output(cmd, *args, **kwargs)

    def Popen(self, cmd, *args, **kwargs):
        self.logCmd(cmd)
        return subprocess.Popen(cmd, *args, **kwargs)
