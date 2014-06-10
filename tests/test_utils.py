# test_utils ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

from StringIO import StringIO
from argparse import Namespace, ArgumentTypeError
from contextlib import closing
from yadda.utils import *
import caseutils
import os
import unittest

class ArgsTest(unittest.TestCase):
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

    def test_binding_arg_ok(self):
        self.assertEqual(binding_arg("FOO=abc3201"),
                         ("FOO", "abc3201"))

    def test_binding_arg_fail(self):
        self.assertRaises(ArgumentTypeError, binding_arg, "FOO")

class ShowOptsTest(unittest.TestCase):
    def setUp(self):
        self.opts = Namespace(foo='bar', bazzz=True)

    def test_requires_namespace(self):
        self.assertRaises(AssertionError, list, show_opts({}))

    def test_string_gen(self):
        g = show_opts(self.opts)
        self.assertEqual('option bazzz = True', g.next())
        self.assertEqual('option foo   = bar', g.next())
        self.assertRaises(StopIteration, g.next)

class SayTest(unittest.TestCase):

    def setUp(self):
        self.opts = Namespace(verbose=True, target='dev')

    def test_sayf(self):
        sayf(self.opts, "hello %d world", 42)

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

    def test_say_call(self):
        say_call(self.opts, ['echo', '-n', 'call'])

    def test_say_call_not_exist(self):
        self.assertRaises(OSError, say_call, self.opts, ['azeonuaoe'])

    def test_say_call_err_code(self):
        self.assertRaises(SystemExit, say_call, self.opts, ['false'])

class FilesTest(caseutils.TmpDirCase):
    def test_symlink_exists(self):
        open('foo', 'a').close()
        self.assertTrue(os.path.isfile('foo'))
        force_symlink('abc', 'foo')
        self.assertTrue(os.path.islink('foo'))

    def test_save_cwd(self):
        d1 = os.getcwd()
        with save_cwd() as cwd:
            os.chdir('/')
            self.assertNotEqual(d1, os.getcwd())
        self.assertEqual(d1, os.getcwd())
