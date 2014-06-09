# test_env ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

from yadda import utils, main
from yadda.models import Role
import unittest

class EnvOptionsTest(unittest.TestCase):

    def setUp(self):
        self.args = main.args()

    def test_history_ok(self):
        opts = self.args.parse_args(['env', 'history'])
        self.assertEqual(opts.verbose, None)
        self.assertEqual(opts.dry_run, False)
        self.assertEqual(opts.target, Role.dev)
        self.assertEqual(opts.app, None)
        self.assertFalse(hasattr(opts, 'revision'))

    def test_show_version_ok(self):
        opts = self.args.parse_args(['env', 'show', '-v', '3'])
        self.assertTrue(hasattr(opts, 'revision'))
        self.assertEqual(opts.revision, 3)
        self.assertEqual(opts.verbose, True)

    def test_show_ok(self):
        opts = self.args.parse_args(['env', 'show'])
        self.assertEqual(opts.revision, None)

    def test_target_first(self):
        opts = self.args.parse_args(['-t', Role.qa, 'env', 'show'])
        self.assertEqual(opts.target, Role.qa)

    def test_target_middle(self):
        opts = self.args.parse_args(['env', '-t', Role.live, 'show'])
        self.assertEqual(opts.target, Role.live)

    def test_target_last(self):
        self.args.parse_args(['env', 'show', '-t', Role.qa])

    def test_set_ok(self):
        opts = self.args.parse_args(['env', 'set', 'FOO=123', 'BAR=abc'])
        self.assertEqual(opts.bindings, [('FOO', '123'), ('BAR', 'abc')])

    def test_set_needs_binding(self):
        self.assertRaises(SystemExit, main.main, ['env', 'set'])

    def test_rm_ok(self):
        opts = self.args.parse_args(['env', 'rm', 'FOO', 'BAR'])
        self.assertEqual(opts.variables, ['FOO', 'BAR'])

    def test_rm_needs_var(self):
        self.assertRaises(SystemExit, main.main, ['env', 'rm'])
