# tests/mock.filesystem ▪ Fake implementation of isfile, isdir ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

from contextlib import contextmanager, closing
from subprocess import Closable
from uuid import uuid4 as uuid
from yadda.filesystem import AugmentedFilesystem
import os.path
import tempfile

class MockFileHandle(Closable):
    def __init__(self, content):
        self.content = content

    def read(self):
        return self.content

class MockShelf(Closable):
    def __init__(self, dict):
        self.dict = dict

    def __getitem__(self, k):
        return self.dict[k]

    def __setitem__(self, k, v):
        self.dict[k] = v

class MockFilesystem(AugmentedFilesystem):
    def __init__(self):
        self._files = {}
        self._cwd = '/home'
        self._dirs = set([self._cwd])
        self._apps = {}

    def home(self):
        return '/home'

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

    def getcwd(self):
        return self._cwd

    def chdir(self, d):
        if self.isdir(d):
            self._cwd = d
        else:
            raise OSError

    def mkdir(self, d):
        self.addDir(d)

    def shelve_open(self, f):
        return MockShelf(self._apps)

    #------------------------------------------------------------

    def addFile(self, f, content=''):
        self._files[f] = content

    def addDir(self, d):
        self._dirs.add(d)

    def assertExistsDir(self, pred):
        for d in self._dirs:
            if pred(d):
                return
        assert False
