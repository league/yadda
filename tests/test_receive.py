# test_receive ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

from caseutils import GitWorkDirCase, AppNameCase
from yadda import settings
from yadda.models import App
from yadda.receive import run
import os
import subprocess
import unittest

class ReceiveTest(GitWorkDirCase, AppNameCase):
    def setUp(self):
        super(ReceiveTest, self).setUp()
        os.environ['YADDA_TEST_BAN'] = settings.DOCKER

    def test_non_master(self):
        self.assertRaises(SystemExit, run,
                          input=['123abc 456def refs/heads/foo'],
                          home=os.getcwd())

    def test_no_such_app(self):
        self.assertRaises(SystemExit, run,
                          input=['123abc 456def refs/heads/master'],
                          home=os.getcwd())

    def test_with_app(self):
        os.mkdir(self.name)
        os.chdir(self.name)
        open('readme', 'w').close()
        subprocess.check_call(['git', 'add', 'readme'])
        subprocess.check_call(['git', 'commit', '-m', 'initial'])
        c = subprocess.check_output(['git', 'rev-parse', 'master']).rstrip()
        self.app = App(self.name)
        self.app.save()
        self.assertRaises(SystemExit, run,
                          input=['123abc %s refs/heads/master' % c],
                          home=os.getcwd())
