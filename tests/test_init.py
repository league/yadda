# test_init ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

from yadda.main import main
from yadda.models import App
from caseutils import *

class InitTest(GitWorkDirCase, AppNameCase):

    def test_basic_init(self):
        main(['init', '-n', self.name])

    def test_init_qa(self):
        main(['init', '-n', self.name, 'localhost'])

    def test_init_qa_remote(self):
        main(['init', self.name, 'localhost'])
        out = subprocess.check_output('git remote -v'.split())
        url = 'localhost:%s.git' % self.name
        ok = False
        for line in out.split('\n'):
            if line.startswith('qa'):
                self.assertTrue(url in line)
                ok = True
        self.assertTrue(ok)

    def test_init_live(self):
        main(['init', '-n', '-t', 'qa', self.name, 'localhost', 'localhost'])

    def test_reinit_existing(self):
        main(['init', '-t', 'live', self.name, 'host1', 'host2'])
        main(['init', '-t', 'live', self.name, 'host3', 'host4'])

    def test_change_role(self):
        main(['init', '-t', 'live', self.name, 'localhost'])
        main(['init', '-t', 'qa', self.name])

class InitNonGitTest(TmpDirCase, AppNameCase):
    def test_init_non_git(self):
        main(['init', self.name])
