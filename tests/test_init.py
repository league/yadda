# test_init ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

from caseutils import *
from yadda.commands.init import opts_to_list
from yadda.main import main
from yadda.models import App
import argparse

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

class OptsTest(unittest.TestCase):
    def setUp(self):
        self.opts = argparse.Namespace(name='foo', qa=None, live=None,
                                       dry_run=False, verbose=0,
                                       database=False, subdir=None)

    def test_subdir_opt(self):
        self.opts.subdir = 'sub'
        self.assertEqual(opts_to_list(self.opts), ['foo', '-C', 'sub'])

    def test_database_opt(self):
        self.opts.database = True
        self.assertEqual(opts_to_list(self.opts), ['foo', '-d'])

class InitNonGitTest(TmpDirCase, AppNameCase):
    def test_init_non_git(self):
        main(['init', self.name])
