# tests/container.py ▪ configuring dependencies for tests ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

from tests.mock.filesystem import MockFilesystem
from tests.mock.subprocess import MockSubprocess
from yadda.container import LazyContainer

class TestContainer(LazyContainer):
    def setup_subprocess(self):
        return MockSubprocess()

    def setup_filesystem(self):
        return MockFilesystem()
