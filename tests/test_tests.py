# test_tests ▪ ensure unittest itself is working ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

import unittest

class TestTestingFramework(unittest.TestCase):
    def setUp(self):
        self.result = 1 + 2

    def no_failure(self):       # rename to test_failure to test failure
        self.assertEqual(self.result, 4)

    def test_ok(self):
        self.assertEqual(self.result, 3)
