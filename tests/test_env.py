# test_env ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

from io import StringIO
from tests.mock.filesystem import MockFilesystem
from uuid import uuid4 as uuid
from yadda import main
from yadda import settings
from yadda.commands.env import EnvCommand
from yadda.models import Role, AppFactory
import argparse
import json
import unittest

class NewEnvTest(unittest.TestCase):
    def setUp(self):
        self.filesystem = MockFilesystem()
        self.appfactory = AppFactory(filesystem=self.filesystem,
                                     datafile=settings.DATA_FILE)
        self.stdout = StringIO()
        self.container = {'stdout': self.stdout}
        self.env = EnvCommand(self.container)
        self.opts = argparse.Namespace()
        self.opts.revision = None
        self.opts.app = self.appfactory.new(uuid().hex)
        self.opts.app.newEnv().set('SECRET', '19293').freeze()

    def test_ls_latest_json(self):
        self.opts.format = 'json'
        self.env.run_ls(self.opts)
        r = json.loads(self.stdout.getvalue())
        self.assertIn('YADDA_VERSION', r)

    def test_ls_latest_human(self):
        self.opts.format = 'human'
        self.env.run_ls(self.opts)
        buf = self.stdout.getvalue()
        self.assertIn('YADDA_VERSION', buf)

    def test_ls_latest_csh(self):
        self.opts.format = 'csh'
        self.env.run_ls(self.opts)
        buf = self.stdout.getvalue()
        self.assertIn('setenv', buf)

    def test_ls_latest_sh(self):
        self.opts.format = 'sh'
        self.env.run_ls(self.opts)
        buf = self.stdout.getvalue()
        self.assertIn('export', buf)

    def test_ls_nonexisent_revision(self):
        self.opts.revision = 24
        self.opts.format = 'json'
        self.assertRaises(SystemExit, self.env.run_ls, self.opts)

    def test_set(self):
        u = uuid().hex
        k1, v1 = u[0:6], u[6:12]
        k2, v2 = u[12:18], u[18:24]
        self.opts.bindings = [(k1,v1),(k2,v2)]
        self.env.run_set(self.opts)
        e = self.opts.app.envs[-1].env
        self.assertIn(k1, e)
        self.assertIn(k2, e)
        self.assertEqual(e[k1], v1)
        self.assertEqual(e[k2], v2)

    def test_rm(self):
        self.assertIn('SECRET', self.opts.app.envs[-1].env)
        self.opts.variables = ['SECRET']
        self.env.run_rm(self.opts)
        self.assertNotIn('SECRET', self.opts.app.envs[-1].env)

    def test_log(self):
        self.env.run_log(self.opts)


class EnvOptionsTest(unittest.TestCase):

    def setUp(self):
        self.args = main.args()

    def test_history_ok(self):
        opts = self.args.parse_args(['env', 'log'])
        self.assertEqual(opts.verbose, 0)
        self.assertEqual(opts.dry_run, False)
        self.assertEqual(opts.target, Role.dev)
        self.assertEqual(opts.app, None)
        self.assertFalse(hasattr(opts, 'revision'))

    def test_show_version_ok(self):
        opts = self.args.parse_args(['env', 'ls', '-v', '3'])
        self.assertTrue(hasattr(opts, 'revision'))
        self.assertEqual(opts.revision, 3)
        self.assertEqual(opts.verbose, 1)

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

#    def test_set_needs_binding(self):
#        self.assertRaises(SystemExit, main.main, ['env', 'set'])

    def test_rm_ok(self):
        opts = self.args.parse_args(['env', 'rm', 'FOO', 'BAR'])
        self.assertEqual(opts.variables, ['FOO', 'BAR'])

#    def test_rm_needs_var(self):
#        self.assertRaises(SystemExit, main.main, ['env', 'rm'])
