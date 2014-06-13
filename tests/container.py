# tests.container ▪ configuring dependencies for tests ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

from tests.mock_filesys import MockFilesystem
from tests.mock_subproc import MockSubprocess
from yadda.container import LazyContainer

class TestContainer(LazyContainer):
    def setup_subprocess(self):
        return MockSubprocess()

    def setup_filesystem(self):
        return MockFilesystem()
