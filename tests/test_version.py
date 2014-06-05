import unittest

from yadda import version

class VersionTest(unittest.TestCase):
    def test_short_dotted_ints(self):
        self.assert_(isinstance(version.short, str))
        for x in version.short.split('.'):
            int(x)

    def test_full_startswith_short(self):
        self.assert_(version.full.startswith(version.short))
