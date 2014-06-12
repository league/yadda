# test_subprocess ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

from yadda.subproc import RealSubprocess, NopSubprocess
import unittest

class BaseSubprocessTest(object):
    def test_check_call(self):
        self.sp.check_call('ls >/dev/null', shell=True)

    def test_check_output(self):
        self.sp.check_output('echo hi', shell=True)

    def test_check_popen(self):
        p = self.sp.Popen(['echo', 'hi'])
        if p:
            p.wait()

class NopSubprocessTest(unittest.TestCase, BaseSubprocessTest):
    def setUp(self):
        self.sp = NopSubprocess()

class RealSubprocessTest(unittest.TestCase, BaseSubprocessTest):
    def setUp(self):
        self.sp = RealSubprocess()
