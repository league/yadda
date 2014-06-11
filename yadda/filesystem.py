# yadda.filesystem ▪ Augmented filesystem interface from os ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

from contextlib import contextmanager
from uuid import uuid4 as uuid
import os.path
import tempfile
import shelve
import logging

log = logging.getLogger('yadda')

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

class ReadOnlyFilesystem(AugmentedFilesystem):
    def logRW(self, fmt, *args, **kwargs):
        log.info('(skip) ' + fmt, *args, **kwargs)

    def home(self):
        return os.environ['HOME']

    def isfile(self, f):
        return os.path.isfile(f)

    def isdir(self, d):
        return os.path.isdir(d)

    def getcwd(self):
        return os.getcwd()

    def chdir(self, d):
        return os.chdir(d)

    def unlink(self, f):
        self.logRW('unlink %s', f)

    def open(self, f, mode):
        if mode == 'r':
            return open(f, mode)
        else:
            self.logRW('open %s for writing', f)

    def mkdir(self, d):
        self.logRW('mkdir %s', d)

    def shelve_open(self, f):
        self.logRW('open %s', f)
        return ReadOnlyShelf(self, shelve.open(f))

    def create_file_containing(self, f, content=''):
        self.logRW('create %s', f)

class ReadOnlyShelf(object):
    def __init__(self, fs, rwshelf):
        self.fs = fs
        self.rwshelf = rwshelf

    def __getitem__(self, k):
        return self.rwshelf[k]

    def __setitem__(self, k, v):
        self.fs.logRW('save %s' % v)

    def close(self):
        self.rwshelf.close()

class ReadWriteShelf(ReadOnlyShelf):
    def __init__(self, fs, rwshelf):
        super(ReadWriteShelf, self).__init__(fs, rwshelf)

    def __setitem__(self, k, v):
        super(ReadWriteShelf, self).__setitem__(k, v)
        self.rwshelf[k] = v

class ReadWriteFilesystem(ReadOnlyFilesystem):
    def logRW(self, fmt, *args, **kwargs):
        # do NOT call super
        log.info(fmt, *args, **kwargs)

    def unlink(self, f):
        super(ReadWriteFilesystem, self).unlink(f)
        return os.unlink(f)

    def open(self, f, mode):
        h = super(ReadWriteFilesystem, self).open(f, mode)
        if h:
            return h
        else:
            return open(f, mode)

    def mkdir(self, d):
        super(ReadWriteFilesystem, self).mkdir(d)
        return os.mkdir(d)

    def shelve_open(self, f):
        rosh = super(ReadWriteFilesystem, self).shelve_open(f)
        return ReadWriteShelf(self, rosh.rwshelf)

    def create_file_containing(self, f, content=''):
        super(ReadWriteFilesystem, self).create_file_containing(f, content)
        with open(f, 'w') as h:
            h.write(content)
