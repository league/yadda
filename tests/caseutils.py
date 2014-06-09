# caseutils ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

from contextlib import closing
from uuid import uuid4 as uuid
from yadda import settings
import os
import shelve
import shutil
import subprocess
import tempfile
import unittest

class TmpDirCase(unittest.TestCase):

    def setUp(self):
        super(TmpDirCase, self).setUp()
        self.dirs = (os.getcwd(), tempfile.mkdtemp())
        os.chdir(self.dirs[1])

    def tearDown(self):
        super(TmpDirCase, self).tearDown()
        os.chdir(self.dirs[0])
        shutil.rmtree(self.dirs[1])

class GitWorkDirCase(TmpDirCase):

    def setUp(self):
        super(GitWorkDirCase, self).setUp()
        subprocess.check_call(['git', 'init', '-q'])

class AppNameCase(unittest.TestCase):
    def setUp(self):
        super(AppNameCase, self).setUp()
        self.name = uuid().hex

    def tearDown(self):
        super(AppNameCase, self).tearDown()
        with closing(shelve.open(settings.DATA_FILE)) as sh:
            if self.name in sh:
                del sh[self.name]
