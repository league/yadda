# caseutils ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

import os
import shutil
import subprocess
import tempfile
import unittest

class TmpDirCase(unittest.TestCase):

    def setUp(self):
        self.dirs = (os.getcwd(), tempfile.mkdtemp())
        os.chdir(self.dirs[1])

    def tearDown(self):
        os.chdir(self.dirs[0])
        shutil.rmtree(self.dirs[1])

class GitWorkDirCase(TmpDirCase):

    def setUp(self):
        super(GitWorkDirCase, self).setUp()
        subprocess.check_call(['git', 'init'])
