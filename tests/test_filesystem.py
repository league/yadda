# test_filesystem ▪ Ensure filesystem methods are implemented ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

import unittest

from contextlib import closing
from tests.mock.filesystem import MockFilesystem
from uuid import uuid4 as uuid
from yadda.filesystem import RealFilesystem
import os.path

class BaseFilesystemTest(object):
    def test_home_isdir(self):
        self.fs.isdir(self.fs.home())

    def test_create_isfile_unlink(self):
        with self.fs.tempname() as tmp:
            self.assertFalse(self.fs.isfile(tmp))
            self.fs.create_file_containing(tmp, '')
            self.assertTrue(self.fs.isfile(tmp))

    def test_create_open(self):
        with self.fs.tempname() as tmp:
            self.fs.create_file_containing(tmp, 'blargh')
            with self.fs.open(tmp, 'r') as h:
                self.assertEqual(h.read(), 'blargh')

    def test_chdir(self):
        d = self.fs.home()
        self.fs.chdir(d)
        self.assertEqual(self.fs.getcwd(), d)
        with self.fs.tempname() as tmp:
            d = os.path.dirname(tmp)
            self.fs.chdir(d)
            self.assertEqual(self.fs.getcwd(), d)

    def test_mkdir(self):
        with self.fs.tempname() as tmp:
            self.assertFalse(self.fs.isdir(tmp))
            self.fs.mkdir(tmp)
            self.assertTrue(self.fs.isdir(tmp))

    def test_shelve(self):
        with self.fs.tempname() as tmp:
            u = uuid().hex
            k, v = u[0:8], u[8:16]
            with closing(self.fs.shelve_open(tmp)) as sh:
                sh[k] = v
            with closing(self.fs.shelve_open(tmp)) as sh:
                self.assertEqual(sh[k], v)

class MockFilesystemTest(unittest.TestCase, BaseFilesystemTest):
    def setUp(self):
        super(MockFilesystemTest, self).setUp()
        self.fs = MockFilesystem()

class RealFilesystemTest(unittest.TestCase, BaseFilesystemTest):
    def setUp(self):
        super(RealFilesystemTest, self).setUp()
        self.fs = RealFilesystem()
