# yadda.filesystem ▪ Augmented filesystem interface from os ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

from contextlib import contextmanager
from uuid import uuid4 as uuid
import os.path
import tempfile
import shelve

class AugmentedFilesystem(object):
    @contextmanager
    def tempname(self):
        name = os.path.join(tempfile.gettempdir(), uuid().hex)
        yield name
        try:
            self.unlink(name)
        except OSError:
            pass

    def maybe_mkdir(self, d):
        if not self.isdir(d):
            self.mkdir(d)

class RealFilesystem(AugmentedFilesystem):
    def home(self):
        return os.environ['HOME']

    def isfile(self, f):
        return os.path.isfile(f)

    def isdir(self, d):
        return os.path.isdir(d)

    def unlink(self, f):
        return os.unlink(f)

    def open(self, f, mode):
        return open(f, mode)

    def getcwd(self):
        return os.getcwd()

    def chdir(self, d):
        return os.chdir(d)

    def mkdir(self, d):
        return os.mkdir(d)

    def shelve_open(self, f):
        return shelve.open(f)
