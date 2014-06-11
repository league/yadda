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

class RealFilesystem(AugmentedFilesystem):
    def open(self, f, mode):
        return open(f, mode)

    def unlink(self, f):
        return os.unlink(f)

    def shelve_open(self, f):
        return shelve.open(f)

    def isfile(self, f):
        return os.path.isfile(f)
