# test_git ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

from mock.filesystem import MockFilesystem
from mock.subprocess import MockSubprocess
from uuid import uuid4 as uuid
from yadda.git import Git
import argparse
import caseutils
import os
import unittest

class NewGitTest(unittest.TestCase):
    def setUp(self):
        self.filesystem = MockFilesystem()
        self.subprocess = MockSubprocess()
        self.git = Git(filesystem = self.filesystem,
                       subprocess = self.subprocess)
        self.filesystem.dirs.add('not-git')
        self.filesystem.dirs.add('yes-git')
        self.filesystem.dirs.add('yes-git/.git')
        self.filesystem.files.add('yes-git/.git/config')

    def test_not_working_dir(self):
        self.assertFalse(self.git.is_working_dir('not-git'))

    def test_is_working_dir(self):
        self.assertTrue(self.git.is_working_dir('yes-git'))

    def test_local_config(self):
        k = uuid().hex
        v = uuid().hex
        self.git.set_local_config(k, v)
        self.subprocess.assertLastCommandStartsWith('git config')
        self.subprocess.assertLastCommandContains(k)
        self.subprocess.results['git config --local '+k] = v
        self.assertEqual(v, self.git.get_local_config(k))

    def test_missing_config(self):
        k = uuid().hex
        self.assertRaises(KeyError, self.git.get_local_config, k)

    def test_init_bare(self):
        self.git.init_bare('florpid')
        self.subprocess.assertLastCommandStartsWith('git init')
        self.subprocess.assertLastCommandContains('--bare')
        self.subprocess.assertLastCommandContains('florpid')

    def test_list_remotes(self):
        self.subprocess.results['git remote'] = 'master\njunk\ntmp\n'
        self.assertEqual(['master', 'junk', 'tmp'], self.git.list_remotes())

    def test_set_remote_new(self):
        self.subprocess.results['git remote'] = 'master\n'
        self.git.set_remote('qa', 'localhost:zz.git')
        self.subprocess.assertLastCommandStartsWith('git remote add')
        self.subprocess.assertLastCommandContains('qa')
        self.subprocess.assertLastCommandContains('localhost:zz.git')

    def test_set_remote_existing(self):
        self.subprocess.results['git remote'] = 'master\nqa\n'
        self.git.set_remote('qa', 'localhost:zz.git')
        self.subprocess.assertLastCommandStartsWith('git remote set-url')
        self.subprocess.assertLastCommandContains('qa')
        self.subprocess.assertLastCommandContains('localhost:zz.git')

    def test_receive_commit(self):
        self.assertEqual(None, self.git.receive_master_commit([]))
        self.assertEqual(None, self.git.receive_master_commit(
            ['123abc 456def refs/heads/foo\n']))
        self.assertEqual('456def', self.git.receive_master_commit(
            ['123abc 456def refs/heads/master\n']))
