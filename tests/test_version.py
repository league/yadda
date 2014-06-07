# test_version ▪ Ensure version.py is filled in correctly ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

import unittest

from yadda import version

class VersionTest(unittest.TestCase):
    def test_short_dotted_ints(self):
        self.assertTrue(isinstance(version.short, str))
        for x in version.short.split('.'):
            int(x)

    def test_full_startswith_short(self):
        self.assertTrue(version.full.startswith(version.short))
