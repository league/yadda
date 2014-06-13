# test_subprocess ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

from tests.log_setup import LogSetup
from yadda.subproc import RealSubprocess, NopSubprocess

class BaseSubprocessTest(object):
    def test_check_call(self):
        self.sp.check_call('ls >/dev/null', shell=True)
        self.assertInLastLog('ls >/dev/null')

    def test_check_output(self):
        self.sp.check_output('echo hi', shell=True)
        self.assertInLastLog('echo hi')

    def test_check_output_ro(self):
        self.sp.check_output_ro(['echo', 'blah'])
        self.assertInLastLog('echo blah')

    def test_check_popen(self):
        p = self.sp.Popen(['echo', 'blorp'])
        self.assertInLastLog('echo blorp')
        if p:
            p.wait()

class NopSubprocessTest(LogSetup, BaseSubprocessTest):
    def setUp(self):
        self.sp = NopSubprocess()

class RealSubprocessTest(LogSetup, BaseSubprocessTest):
    def setUp(self):
        self.sp = RealSubprocess()
