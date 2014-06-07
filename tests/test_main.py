import unittest
from yadda.main import main

class MainTest(unittest.TestCase):
    def test_main(self):
        self.assertRaises(SystemExit, main, ['-h'])
