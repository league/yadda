# test_env ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

from caseutils import *
from yadda import utils, main
from yadda.commands.env import *
from yadda.models import Role, App, Env
import unittest

class EnvOptionsTest(unittest.TestCase):

    def setUp(self):
        self.args = main.args()

    def test_history_ok(self):
        opts = self.args.parse_args(['env', 'log'])
        self.assertEqual(opts.verbose, None)
        self.assertEqual(opts.dry_run, False)
        self.assertEqual(opts.target, Role.dev)
        self.assertEqual(opts.app, None)
        self.assertFalse(hasattr(opts, 'revision'))

    def test_show_version_ok(self):
        opts = self.args.parse_args(['env', 'ls', '-v', '3'])
        self.assertTrue(hasattr(opts, 'revision'))
        self.assertEqual(opts.revision, 3)
        self.assertEqual(opts.verbose, True)

    def test_show_ok(self):
        opts = self.args.parse_args(['env', 'ls'])
        self.assertEqual(opts.revision, None)

    def test_target_first(self):
        opts = self.args.parse_args(['-t', Role.qa, 'env', 'ls'])
        self.assertEqual(opts.target, Role.qa)

    def test_target_middle(self):
        opts = self.args.parse_args(['env', '-t', Role.live, 'ls'])
        self.assertEqual(opts.target, Role.live)

    def test_target_last(self):
        self.args.parse_args(['env', 'ls', '-t', Role.qa])

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

class EnvRunTest(TmpDirCase, AppNameCase):
    def setUp(self):
        super(EnvRunTest, self).setUp()
        self.app = App(self.name)
        Env(self.app).freeze()
        self.app.save()

    def test_env_ls(self):
        main.main(['-a', self.name, 'env', 'ls'])

    def test_env_ls_formats(self):
        for f in FORMATS:
            main.main(['-a', self.name, 'env', 'ls', '-f', f])

    def test_env_log(self):
        main.main(['-a', self.name, 'env', 'log'])

    def test_env_set(self):
        main.main(['-a', self.name, 'env', 'set', '-n', 'BAZ=223'])

    def test_env_rm(self):
        main.main(['-a', self.name, 'env', 'rm', '-n', 'BAZ'])

class EnvGitRunTest(GitWorkDirCase, AppNameCase):

    def setUp(self):
        super(EnvGitRunTest, self).setUp()

    def test_env_app_not_in_git(self):
        self.assertRaises(SystemExit, main.main, ['env', 'ls'])

    def test_env_not_in_file(self):
        self.assertRaises(SystemExit, main.main, ['env', 'ls', '-a', self.name[:8]])

    def test_env_dispatch(self):
        main.main(['init', self.name])
        main.main(['env', 'ls'])
