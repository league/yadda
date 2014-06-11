# test_docker ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

from mock.filesystem import MockFilesystem
from mock.subprocess import MockSubprocess
from uuid import uuid4 as uuid
from yadda import utils
from yadda.docker import Docker
import sys
import unittest

class DockerTest(unittest.TestCase):
    def setUp(self):
        self.subprocess = MockSubprocess()
        self.filesystem = MockFilesystem()
        self.docker = Docker(subprocess = self.subprocess,
                             filesystem = self.filesystem,
                             stdout = sys.stdout)

    def applyTee(self, cmd):
        tee, f = cmd.split()
        self.filesystem.addFile(f, 'build transcript')
        return True

    def test_docker_build_success(self):
        tag = uuid().hex
        buildp = lambda c: c.startswith('docker build') and tag in c
        teep = lambda c: c.startswith('tee')
        self.subprocess.provideResult(buildp, True)
        self.subprocess.provideResult(teep, self.applyTee)
        self.assertEqual(self.docker.build(tag, '.'),
                         (True, 'build transcript'))

    def test_docker_build_no_log(self):
        tag = uuid().hex
        buildp = lambda c: c.startswith('docker build') and tag in c
        self.subprocess.provideResult(buildp, True)
        self.assertEqual(self.docker.build(tag, '.'), (True, ''))

    def test_docker_build_fail(self):
        tag = uuid().hex
        buildp = lambda c: c.startswith('docker build') and tag in c
        teep = lambda c: c.startswith('tee')
        self.subprocess.provideResult(buildp, False)
        self.subprocess.provideResult(teep, self.applyTee)
        self.assertEqual(self.docker.build(tag, '.'),
                         (False, 'build transcript'))
