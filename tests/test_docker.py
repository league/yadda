# test_docker ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

from tests.mock.filesystem import MockFilesystem
from tests.mock.subprocess import MockSubprocess
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
        self.filesystem.create_file_containing(f, 'build transcript')
        return True

    def test_docker_build_success(self):
        tag = uuid().hex
        buildp = lambda c: c.startswith('docker build') and tag in c
        teep = lambda c: c.startswith('tee')
        self.subprocess.provideResult(buildp, 0)
        self.subprocess.provideResult(teep, self.applyTee)
        self.assertEqual(self.docker.build(tag, '.'),
                         (0, 'build transcript'))

    def test_docker_build_no_log(self):
        tag = uuid().hex
        buildp = lambda c: c.startswith('docker build') and tag in c
        self.subprocess.provideResult(buildp, 0)
        self.assertEqual(self.docker.build(tag, '.'), (0, ''))

    def test_docker_build_fail(self):
        tag = uuid().hex
        buildp = lambda c: c.startswith('docker build') and tag in c
        teep = lambda c: c.startswith('tee')
        self.subprocess.provideResult(buildp, 1)
        self.subprocess.provideResult(teep, self.applyTee)
        self.assertEqual(self.docker.build(tag, '.'),
                         (1, 'build transcript'))
