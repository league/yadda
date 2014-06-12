# yadda.container.py ▪ configuring dependencies for injection ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

from yadda.docker import Docker
from yadda.filesystem import ReadWriteFilesystem, ReadOnlyFilesystem
from yadda.git import Git
from yadda.models import AppFactory
from yadda.subproc import RealSubprocess, NopSubprocess
import logging
import os.path
import sys

class LazyContainer(object):

    def __init__(self):
        self.d = {}

    def __getitem__(self, name):
        if name not in self.d:
            self.d[name] = getattr(self, 'setup_' + name)()
        return self.d[name]

    def setup_log(self):
        return logging.getLogger('yadda')

    def setup_stdout(self):
        return sys.stdout

    def setup_datafile(self):
        return os.path.join(self['filesystem'].home(), '.yadda.data')

    def setup_subprocess(self):
        return RealSubprocess()

    def setup_filesystem(self):
        return ReadWriteFilesystem() # pragma: no cover

    def setup_appfactory(self):
        return AppFactory(self)

    def setup_git(self):
        return Git(filesystem=self['filesystem'],
                   subprocess=self['subprocess'])

    def setup_docker(self):
        return Docker(filesystem=self['filesystem'],
                      subprocess=self['subprocess'],
                      stdout=self['stdout'])

class DryRunContainer(LazyContainer):
    def setup_subprocess(self):
        return NopSubprocess()

    def setup_filesystem(self):
        return ReadOnlyFilesystem()
