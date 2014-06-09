# test_env ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

from yadda import utils
from yadda.main import main
from yadda.models import Role
import unittest

class EnvOptionsTest(unittest.TestCase):

    def test_history_ok(self):
        opts = main(['env', 'history'], utils.id)
        self.assertEqual(opts.verbose, False)
        self.assertEqual(opts.dry_run, False)
        self.assertEqual(opts.target, Role.dev)
        self.assertEqual(opts.app, None)
        self.assertFalse(hasattr(opts, 'revision'))

    def test_show_version_ok(self):
        opts = main(['env', 'show', '-v', '3'], utils.id)
        self.assertTrue(hasattr(opts, 'revision'))
        self.assertEqual(opts.revision, 3)
        self.assertEqual(opts.verbose, True)

    def test_show_ok(self):
        opts = main(['env', 'show'], utils.id)
        self.assertEqual(opts.revision, 1)

    def test_target_first(self):
        opts = main(['-t', Role.qa, 'env', 'show'], utils.id)
        self.assertEqual(opts.target, Role.qa)

    def test_target_middle(self):
        opts = main(['env', '-t', Role.live, 'show'], utils.id)
        self.assertEqual(opts.target, Role.live)

    def test_target_last(self):
        main(['env', 'show', '-t', Role.qa], utils.id)

    def test_set_ok(self):
        opts = main(['env', 'set', 'FOO=123', 'BAR=abc'], utils.id)
        self.assertEqual(opts.bindings, ['FOO=123', 'BAR=abc'])

    def test_set_needs_binding(self):
        self.assertRaises(SystemExit, main, ['env', 'set'], utils.id)

    def test_rm_ok(self):
        opts = main(['env', 'rm', 'FOO', 'BAR'], utils.id)
        self.assertEqual(opts.variables, ['FOO', 'BAR'])

    def test_rm_needs_var(self):
        self.assertRaises(SystemExit, main, ['env', 'rm'], utils.id)
