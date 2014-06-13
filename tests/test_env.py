# test_env ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

from tests.container import TestContainer
from uuid import uuid4 as uuid
from yadda import main
from yadda.commands.env import EnvCommand
from yadda.models import Role
import argparse
import json
import unittest

class NewEnvTest(unittest.TestCase):
    def setUp(self):
        container = TestContainer()
        self.stdout = container['stdout']
        self.env = EnvCommand(container)
        self.opts = argparse.Namespace(log=False, version=None, binding=[],
                                       delete=None, format='human')
        self.opts.app = container['appfactory'].new(uuid().hex)
        self.opts.app.newEnv().set('SECRET', '19293').freeze()

    def test_run_log(self):
        self.opts.log = True
        self.env.run(self.opts)

    def test_run_add_remove(self):
        self.opts.delete = ['SECRET']
        self.opts.version = 'ANOTHER=223852'
        self.env.run(self.opts)

    def test_run_full_version(self):
        self.opts.version = self.opts.app.envs[-1].version()
        self.env.run(self.opts)

    def test_run_serial_version(self):
        self.opts.version = str(self.opts.app.envs[-1].serial)
        self.env.run(self.opts)

    def test_run_hash_version(self):
        self.opts.version = self.opts.app.envs[-1].checksum()
        self.env.run(self.opts)

    def test_run_latest(self):
        self.env.run(self.opts)

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

    def test_set(self):
        u = uuid().hex
        k1, v1 = u[0:6], u[6:12]
        k2, v2 = u[12:18], u[18:24]
        self.opts.version = k1+'='+v1
        self.opts.binding = [(k1,v1), (k2,v2)]
        self.env.run_set_rm(self.opts)
        e = self.opts.app.envs[-1].env
        self.assertIn(k1, e)
        self.assertIn(k2, e)
        self.assertEqual(e[k1], v1)
        self.assertEqual(e[k2], v2)

    def test_rm(self):
        self.assertIn('SECRET', self.opts.app.envs[-1].env)
        self.opts.delete = ['SECRET']
        self.env.run_set_rm(self.opts)
        self.assertNotIn('SECRET', self.opts.app.envs[-1].env)

    def test_log(self):
        self.env.run_log(self.opts)


class EnvOptionsTest(unittest.TestCase):

    def test_history_ok(self):
        opts = main.process_args(['yadda', 'env', '-l'])
        self.assertEqual(opts.verbose, 0)
        self.assertEqual(opts.dry_run, False)
        self.assertEqual(opts.target, Role.dev)
        self.assertEqual(opts.app, None)
        self.assertFalse(hasattr(opts, 'revision'))
        self.assertTrue(opts.log)

    def test_show_version_ok(self):
        opts = main.process_args(['yadda', 'env', '-v', '3'])
        self.assertEqual(opts.version, '3')
        self.assertEqual(opts.binding, [])
        self.assertEqual(opts.verbose, 1)

    def test_show_ok(self):
        opts = main.process_args(['yadda', 'env'])
        self.assertEqual(opts.binding, [])
        self.assertFalse(opts.log)

    def test_target_first(self):
        opts = main.process_args(['yadda', '-t', Role.qa, 'env'])
        self.assertEqual(opts.target, Role.qa)

    def test_target_middle(self):
        opts = main.process_args(['yadda', 'env', '-t', Role.live])
        self.assertEqual(opts.target, Role.live)

    def test_target_last(self):
        main.process_args(['yadda', 'env', '-t', Role.qa])

    def test_set_ok(self):
        opts = main.process_args(['yadda', 'env', 'FOO=123', 'BAR=abc'])
        self.assertEqual(opts.version, 'FOO=123')
        self.assertEqual(opts.binding, [('BAR', 'abc')])

    def test_bad_set(self):
        self.assertRaises(SystemExit, main.process_args,
                          ['yadda', 'env', 'FOO=3399', 'BAD'])

    def test_rm_ok(self):
        opts = main.process_args(['yadda', 'env', '-d', 'FOO', '-d', 'BAR'])
        self.assertEqual(opts.binding, [])
        self.assertEqual(opts.version, None)
        self.assertEqual(opts.delete, ['FOO', 'BAR'])

    def test_rm_needs_var(self):
        self.assertRaises(SystemExit, main.process_args, ['yadda', 'env', '-d'])
