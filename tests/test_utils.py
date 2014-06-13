# test_utils ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

from __future__ import unicode_literals
from yadda import utils
import argparse
import unittest

class ArgsTest(unittest.TestCase):
    def test_slug_ok(self):
        utils.slug_arg('foo91')

    def test_slug_punct(self):
        self.assertRaises(argparse.ArgumentTypeError, utils.slug_arg, 'boo!')

    def test_slug_caps(self):
        self.assertRaises(argparse.ArgumentTypeError, utils.slug_arg, 'noCaps')

    def test_slug_return(self):
        self.assertEqual(utils.slug_arg('ok'), 'ok')
