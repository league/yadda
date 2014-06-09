# test_git ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

from uuid import uuid4 as uuid
from yadda import git
import argparse
import caseutils
import os
import unittest

class NonGitTest(caseutils.TmpDirCase):
    def setUp(self):
        super(NonGitTest, self).setUp()
        self.opts = argparse.Namespace(verbose=False, dry_run=False)

    def test_has_dot_git(self):
        self.assertFalse(git.has_dot_git())

    def test_init_bare(self):
        d = uuid().hex[:6] + '.git'
        git.init_bare(self.opts, d)
        self.assertTrue(os.path.isdir(d))
        self.assertTrue(os.path.isfile(os.path.join(d, 'config')))
        self.assertTrue(os.path.isdir(os.path.join(d, 'hooks')))

class GitTest(caseutils.GitWorkDirCase):
    def setUp(self):
        super(GitTest, self).setUp()
        self.opts = argparse.Namespace(verbose=False, dry_run=False)
        self.name = uuid().hex

    def test_has_dot_git(self):
        self.assertTrue(git.has_dot_git())

    def test_yadda_app_config(self):
        git.set_yadda_app(self.opts, self.name)
        self.assertEqual(git.get_yadda_app(), self.name)

    def test_get_app_key_error(self):
        self.assertRaises(KeyError, git.get_yadda_app)
