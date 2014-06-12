# yadda.filesystem ▪ Augmented filesystem interface from os ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

from contextlib import contextmanager
from uuid import uuid4 as uuid
import os.path
import tempfile
import shelve
import logging
import errno

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

    def force_symlink(self, file1, file2):
        'Simulate `ln -sf`, replacing `file2` if it exists already.'
        try:
            self.symlink(file1, file2)
        except OSError as e:
            if e.errno == errno.EEXIST:
                self.unlink(file2)
                self.symlink(file1, file2)

class ReadOnlyFilesystem(AugmentedFilesystem):
    def logSkip(self):
        return '(skip) '        # pragma: no cover

    def logRW(self, fmt, *args, **kwargs):
        log.info(self.logSkip() + fmt, *args, **kwargs)

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

    def symlink(self, f1, f2):
        self.logRW('symlink %s %s', f1, f2)

    def shelve_open(self, f):
        return ReadOnlyShelf(self, f) # pragma: no cover

    def create_file_containing(self, f, content=''):
        self.logRW('create %s', f)

class ReadOnlyShelf(object):
    def __init__(self, fs, file):
        self.fs = fs
        self.file = file
        self.rwshelf = shelve.open(file)

    def __getitem__(self, k):
        return self.rwshelf[k]

    def __setitem__(self, k, v):
        self.fs.logRW('save %s to %s' % (v, self.file))

    def keys(self):
        return self.rwshelf.keys()

    def close(self):
        self.rwshelf.close()

class ReadWriteShelf(ReadOnlyShelf):
    def __init__(self, fs, file):
        super(ReadWriteShelf, self).__init__(fs, file)

    def __setitem__(self, k, v):
        super(ReadWriteShelf, self).__setitem__(k, v)
        self.rwshelf[k] = v

class ReadWriteFilesystem(ReadOnlyFilesystem):
    def logSkip(self):
        return ''

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

    def symlink(self, f1, f2):
        super(ReadWriteFilesystem, self).symlink(f1, f2)
        return os.symlink(f1, f2)

    def shelve_open(self, f):
        # do NOT call super
        return ReadWriteShelf(self, f)

    def create_file_containing(self, f, content=''):
        super(ReadWriteFilesystem, self).create_file_containing(f, content)
        with open(f, 'w') as h:
            h.write(content)
