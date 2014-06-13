# test_main ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

from tests.container import AltLogTestContainer, TestContainer
from tests.log_setup import LogSetup
from uuid import uuid4 as uuid
from yadda import main
import argparse
import logging
import unittest

class MainTest(unittest.TestCase):
    def test_dry_run_verbosity(self):
        opts = main.process_args(['yadda', 'env', 'log', '-n'])
        self.assertEqual(opts.verbose, 1)

    def test_dry_run_verbosity_2(self):
        opts = main.process_args(['yadda', 'env', 'log', '-nv'])
        self.assertEqual(opts.verbose, 2)

    def test_receive_arg(self):
        opts1 = main.process_args(['yadda', 'receive'])
        opts2 = main.process_args(['pre-receive'])
        for k, v in vars(opts1).items():
            if k not in ['prog', 'ctor']:
                self.assertEqual(getattr(opts2, k), v)

class MainRunTest(unittest.TestCase):
    def setUp(self):
        self.container = AltLogTestContainer()
        self.name = uuid().hex
        self.appfactory = self.container['appfactory']
        self.app = self.appfactory.new(self.name, qa='frobnozz')
        self.appfactory.save(self.app)
        self.subprocess = self.container['subprocess']
        self.filesystem = self.container['filesystem']
        self.filesystem.mkdir(self.name)
        self.filesystem.chdir(self.name)

    def test_run_init(self):
        opts = main.process_args(['yadda', 'init', self.name])
        main.run([], self.container, opts)

    def test_run_receive(self):
        self.subprocess.provideResult(lambda c: c.startswith("docker build"), 0)
        self.container.stdin = ["aaaaaaa bbbbbbb refs/heads/master\n"]
        opts = main.process_args(['yadda', 'receive'])
        opts.app = self.name
        main.run(['pre-receive'], self.container, opts)

    def test_run_env_ls(self):
        opts = main.process_args(['yadda', 'env', 'ls', '-a', self.name])
        main.run([], self.container, opts)

    def test_other_target(self):
        opts = main.process_args(['yadda', 'env', 'ls', '-t', 'qa', '-a', self.name])
        main.run([], self.container, opts)

    def test_other_target_unknown(self):
        self.app.qa = None
        self.appfactory.save(self.app)
        opts = main.process_args(['yadda', 'env', 'ls', '-t', 'qa', '-a', self.name])
        self.assertRaises(SystemExit, main.run, [], self.container, opts)

class MainOptsTest(LogSetup):
    def setUp(self):
        container = TestContainer()
        self.log = container['log']

    def test_wrap_opts_omit_func(self):
        opts = argparse.Namespace(foo=3, bar='hi', func='omit')
        main.log_opts_wrapped(self.log, opts)

    def test_wrap_opts_long(self):
        opts = argparse.Namespace(
            foo=3,
            baz='8' * 80,
            bloop=True
            )
        main.log_opts_wrapped(self.log, opts)

class MainDetermineAppTest(unittest.TestCase):
    def setUp(self):
        self.container = TestContainer()
        self.opts = argparse.Namespace(
            app = None
        )
        self.name = uuid().hex
        self.filesystem = self.container['filesystem']
        self.subprocess = self.container['subprocess']
        self.appfactory = self.container['appfactory']
        a = self.appfactory.new(self.name)
        self.appfactory.save(a)

    def test_given(self):
        self.opts.app = self.name
        main.determine_app(self.container, self.opts)
        self.assertEqual(self.opts.app.name, self.name)

    def test_git_config(self):
        self.filesystem.mkdir('./.git')
        self.filesystem.create_file_containing('./.git/config')
        self.subprocess.provideResult(
            lambda c: c.startswith('git config'),
            self.name)
        main.determine_app(self.container, self.opts)
        self.assertEqual(self.opts.app.name, self.name)

    def test_cwd(self):
        d = self.name + '.git'
        self.filesystem.mkdir(d)
        self.filesystem.chdir(d)
        main.determine_app(self.container, self.opts)
        self.assertEqual(self.opts.app.name, self.name)

    def test_not_config(self):
        self.opts.app = uuid().hex
        self.assertRaises(SystemExit, main.determine_app,
                          self.container, self.opts)

class MainDepsTest(unittest.TestCase):
    def setUp(self):
        self.opts = argparse.Namespace(verbose=0, dry_run=False, cmd='receive')
        self.container = AltLogTestContainer()

    def test_deps_v0(self):
        r = main.configure_deps(self.container, self.opts)
        self.assertTrue(isinstance(r, logging.StreamHandler))

    def test_deps_v1(self):
        self.opts.verbose = 1
        main.configure_deps(self.container, self.opts)

    def test_deps_v2(self):
        self.opts.verbose = 2
        main.configure_deps(self.container, self.opts)
