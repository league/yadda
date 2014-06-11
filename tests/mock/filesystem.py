# tests/mock.filesystem ▪ Fake implementation of isfile, isdir ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

from contextlib import contextmanager, closing
from uuid import uuid4 as uuid
from yadda.filesystem import AugmentedFilesystem
import os.path
import tempfile

class MockFileHandle(object):
    def __init__(self, content):
        self.content = content

    def read(self):
        return self.content

    def close(self):
        pass

class MockFilesystem(AugmentedFilesystem):
    def __init__(self):
        self._files = {}
        self._dirs = set()

    def isfile(self, f):
        return f in self._files

    def isdir(self, d):
        return d in self._dirs

    def unlink(self, f):
        try:
            del self._files[f]
        except KeyError:
            raise OSError

    def open(self, f, mode):
        assert mode == 'r'
        try:
            return closing(MockFileHandle(self._files[f]))
        except KeyError:
            raise IOError

    #------------------------------------------------------------

    def addFile(self, f, content=''):
        self._files[f] = content

    def addDir(self, d):
        self._dirs.add(d)
