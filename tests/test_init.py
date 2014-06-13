# test_init ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

from tests.container import TestContainer
from uuid import uuid4 as uuid
from yadda.commands.init import InitCommand
from yadda.models import Role
import argparse
import unittest

class InitTest(unittest.TestCase):
    def setUp(self):
        container = TestContainer()
        self.filesystem = container['filesystem']
        self.subprocess = container['subprocess']
        self.appfactory = container['appfactory']
        self.init = InitCommand(container)
        self.opts = argparse.Namespace(
            prog = 'yadda',
            verbose = 0,
            dry_run = True,
            name = uuid().hex,
            target = Role.dev,
            qa = None,
            live = None,
            subdir = None,
            database = None,
        )

    def test_run_simple(self):
        self.init.run(self.opts)

    def test_run_with_qa(self):
        self.opts.qa = uuid().hex
        self.init.run(self.opts)

    def test_run_with_qa_verbose(self):
        self.opts.verbose = True
        self.opts.qa = uuid().hex
        self.init.run(self.opts)

    def test_run_with_qa_db(self):
        self.opts.database = True
        self.opts.qa = uuid().hex
        self.init.run(self.opts)

    def test_run_with_qa_subdir(self):
        self.opts.subdir = 'example'
        self.opts.qa = uuid().hex
        self.init.run(self.opts)

    def test_run_on_qa_with_live(self):
        self.opts.target = Role.qa
        self.opts.qa = uuid().hex
        self.opts.live = uuid().hex
        self.init.run(self.opts)

    def test_run_already_exists(self):
        a = self.appfactory.new(self.opts.name)
        self.appfactory.save(a)
        self.init.run(self.opts)

    def test_run_exists_change_role(self):
        self.opts.target = Role.qa
        a = self.appfactory.new(self.opts.name)
        self.appfactory.save(a)
        self.init.run(self.opts)

    def test_run_git_working_dir(self):
        self.filesystem.mkdir('./.git')
        self.filesystem.create_file_containing('./.git/config')
        self.opts.qa = uuid().hex
        self.subprocess.provideResultEq('git remote', 'master\njunk\ntmp\n')
        self.init.run(self.opts)
