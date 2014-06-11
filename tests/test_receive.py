# test_receive ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

from caseutils import GitWorkDirCase, AppNameCase
from mock.filesystem import MockFilesystem
from mock.subprocess import MockSubprocess
from yadda import settings
from yadda.docker import Docker
from yadda.git import Git
from yadda.models import AppFactory
from yadda.receive import Receive
import os
import subprocess
import unittest
from uuid import uuid4 as uuid

class BaseReceiveTest(unittest.TestCase):
    def setUp(self):
        self.filesystem = MockFilesystem()
        self.subprocess = MockSubprocess()
        self.git = Git(filesystem=self.filesystem,
                       subprocess=self.subprocess)
        self.docker = Docker(filesystem=self.filesystem,
                             subprocess=self.subprocess)
        self.appfactory = AppFactory(filesystem=self.filesystem,
                                     datafile=settings.DATA_FILE)
        self.receive = Receive(filesystem=self.filesystem,
                               git=self.git,
                               docker=self.docker,
                               appfactory=self.appfactory)

        self.name = uuid().hex
        cwd = '/home/' + self.name
        self.filesystem.addDir(cwd)
        self.filesystem.chdir(cwd)

    def test_no_master_update(self):
        try:
            self.receive.run(stdin=['123abc 456def refs/heads/foo'])
        except SystemExit as exn:
            self.assertEqual(exn.code, 0)
            return
        assert False, 'expected SystemExit'

    def test_unknown_app(self):
        try:
            self.receive.run(stdin=['123abc 456def refs/heads/master'])
        except SystemExit as exn:
            self.assertIn('not configured', exn.message)
            self.assertIn(self.name, exn.message)
            return
        assert False, 'expected SystemExit'

    def test_known_good_app(self):
        app = self.appfactory.new(self.name).save()
        buildp = lambda c: c.startswith('docker build')
        self.subprocess.provideResult(buildp, 0)
        self.receive.run(stdin=['123abc 456def refs/heads/master'])
        self.filesystem.assertExistsDir(lambda d: self.name in d and '456de' in d)
        self.subprocess.assertExistsCommand(lambda c: c.startswith('git archive'))
        self.subprocess.assertExistsCommand(lambda c: c.startswith('docker build'))

    def test_subdir_app(self):
        app = self.appfactory.new(self.name, subdir='ex/py').save()
        buildp = lambda c: c.startswith('docker build')
        self.subprocess.provideResult(buildp, 0)
        self.receive.run(stdin=['123abc 456def refs/heads/master'])
        self.filesystem.assertExistsDir(lambda d: self.name in d and '456de' in d)

    def test_broken_build(self):
        app = self.appfactory.new(self.name).save()
        buildp = lambda c: c.startswith('docker build')
        self.subprocess.provideResult(buildp, 1)
        try:
            self.receive.run(stdin=['123abc 456def refs/heads/master'])
        except SystemExit as exn:
            self.assertIn('docker build failure', exn.message)
            return
        assert False
