# tests/mock.filesystem ▪ Fake implementation of isfile, isdir ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

from contextlib import closing
from copy import copy
from tests.mock.subprocess import Closable
from yadda.filesystem import ReadOnlyFilesystem
import tempfile

class MockFileHandle(Closable):
    def __init__(self, fs, f, mode):
        self.fs = fs
        self.f = f
        if mode == 'w':
            fs._files[f] = ''

    def read(self):
        return self.fs._files[self.f]

    def write(self, s):
        self.fs._files[self.f] += s

class MockShelf(Closable):
    def __init__(self, dict):
        self.dict = dict

    def __getitem__(self, k):
        return copy(self.dict[k])

    def __setitem__(self, k, v):
        self.dict[k] = v

    def keys(self):
        return self.dict.keys()

class MockFilesystem(ReadOnlyFilesystem):
    def __init__(self):
        self._files = {}
        self._cwd = '/home'
        self._dirs = set([self._cwd, tempfile.gettempdir()])
        self._links = {}
        self._apps = {}

    def home(self):
        return '/home'

    def isfile(self, f):
        return f in self._files

    def isdir(self, d):
        return d in self._dirs

    def unlink(self, f):
        super(MockFilesystem, self).unlink(f)
        try:
            del self._files[f]
        except KeyError:
            raise OSError

    def symlink(self, f1, f2):
        super(MockFilesystem, self).symlink(f1, f2)
        self._links[f1] = f2

    def create_file_containing(self, f, content=''):
        super(MockFilesystem, self).create_file_containing(f, content)
        self._files[f] = content

    def open(self, f, mode):
        assert mode in ['r', 'w']
        if mode == 'r' and f not in self._files:
            raise IOError
        return closing(MockFileHandle(self, f, mode))

    def getcwd(self):
        return self._cwd

    def chdir(self, d):
        if self.isdir(d):
            self._cwd = d
        else:
            raise OSError("No such file or directory: %r" % d)

    def mkdir(self, d):
        super(MockFilesystem, self).mkdir(d)
        self._dirs.add(d)

    def shelve_open(self, f):
        return MockShelf(self._apps)

    #------------------------------------------------------------

    def assertExistsDir(self, pred):
        for d in self._dirs:
            if pred(d):
                return
        assert False
