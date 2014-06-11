# tests/mock.filesystem ▪ Fake implementation of isfile, isdir ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

class MockFilesystem(object):
    def __init__(self):
        self.files = set()
        self.dirs = set()

    def isfile(self, f):
        return f in self.files

    def isdir(self, d):
        return d in self.dirs
