# test_utils ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

from __future__ import unicode_literals
from contextlib import closing
from io import StringIO
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

    def test_binding_arg_ok(self):
        self.assertEqual(utils.binding_arg("FOO=abc3201"),
                         ("FOO", "abc3201"))

    def test_binding_arg_fail(self):
        self.assertRaises(argparse.ArgumentTypeError, utils.binding_arg, "FOO")

class SayTest(unittest.TestCase):

    def setUp(self):
        self.opts = argparse.Namespace(verbose=1, target='dev')

    def test_sayf(self):
        utils.sayf(self.opts, "hello %d world", 42)

    def test_say1(self):
        with closing(StringIO()) as out:
            utils.say1(self.opts, 'hello', out=out)
            self.assertEqual('dev  » hello\n', out.getvalue())

    def test_quiet_say(self):
        self.opts.verbose = 0
        with closing(StringIO()) as out:
            utils.say(argparse.Namespace(verbose=0), 'hello', out=out)
            self.assertEqual('', out.getvalue())

    def test_verbose_say(self):
        with closing(StringIO()) as out:
            utils.say(self.opts, 'hello', out=out)
            self.assertEqual('dev  » hello\n', out.getvalue())

    def test_say_generator(self):
        with closing(StringIO()) as out:
            utils.say(self.opts, ['a','b'], lambda x: x, out=out)
            self.assertEqual('dev  » a\ndev  » b\n', out.getvalue())
