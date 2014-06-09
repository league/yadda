# test_utils ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

from StringIO import StringIO
from contextlib import closing
from yadda.utils import *
from argparse import Namespace
import unittest

class MiscUtilTest(unittest.TestCase):
    def test_die(self):
        self.assertRaises(SystemExit, die, "just kidding")

    def test_slug_ok(self):
        slug_arg('foo91')

    def test_slug_punct(self):
        self.assertRaises(argparse.ArgumentTypeError, slug_arg, 'boo!')

    def test_slug_caps(self):
        self.assertRaises(argparse.ArgumentTypeError, slug_arg, 'noCaps')

    def test_slug_return(self):
        self.assertEqual(slug_arg('ok'), 'ok')

class ShowOptsTest(unittest.TestCase):
    def setUp(self):
        self.ns = Namespace(foo='bar', baz=True)

    def test_requires_namespace(self):
        self.assertRaises(AssertionError, list, show_opts({}))

    def test_string_gen(self):
        g = show_opts(self.ns)
        self.assertEqual('option foo = bar', g.next())
        self.assertEqual('option baz = True', g.next())
        self.assertRaises(StopIteration, g.next)

class SayTest(unittest.TestCase):

    def setUp(self):
        self.opts = Namespace(verbose=True, target='dev')

    def test_say1(self):
        with closing(StringIO()) as out:
            say1(self.opts, 'hello', out=out)
            self.assertEqual('dev  » hello\n', out.getvalue())

    def test_quiet_say(self):
        self.opts.verbose = False
        with closing(StringIO()) as out:
            say(Namespace(verbose=False), 'hello', out=out)
            self.assertEqual('', out.getvalue())

    def test_verbose_say(self):
        with closing(StringIO()) as out:
            say(self.opts, 'hello', out=out)
            self.assertEqual('dev  » hello\n', out.getvalue())

    def test_say_generator(self):
        with closing(StringIO()) as out:
            say(self.opts, ['a','b'], lambda x: x, out=out)
            self.assertEqual('dev  » a\ndev  » b\n', out.getvalue())
