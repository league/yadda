# yadda.receive ▪ Implement the git pre-receive hook ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

from datetime import datetime
from yadda.settings import HASH_ABBREV
import os.path
import logging

log = logging.getLogger('yadda')

class Receive(object):
    def __init__(self, filesystem, git, docker, appfactory):
        self.filesystem = filesystem
        self.git = git
        self.docker = docker
        self.appfactory = appfactory

    def run(self, stdin):
        # Determine latest commit to master
        commit = self.git.receive_master_commit(stdin)
        if not commit:
            print('Note: no update to master')
            raise SystemExit(0)

        # Use working-dir basename to figure out app name
        cwd = self.filesystem.getcwd()
        name, ext = os.path.splitext(os.path.basename(cwd))
        try:
            app = self.appfactory.load(name)
        except KeyError:
            raise SystemExit('App %s not configured; cannot deploy' % name)

        # Check out into a fresh working dir
        workdir = os.path.join(self.filesystem.home(),
                               name + '-' + commit[:HASH_ABBREV])
        self.filesystem.maybe_mkdir(workdir)
        b = app.newBuild(commit, workdir=workdir)
        app.save()
        log.info('Starting build %s in %s', b.tag(), workdir)
        self.git.export(commit, workdir)

        # Build it with docker
        if b.app.subdir:
            workdir = os.path.join(workdir, b.app.subdir)
        b.build_status, b.build_log = self.docker.build(b.tag(), workdir)
        b.build_finish = datetime.now()
        b.app.save()
        if b.build_status != 0:
            raise SystemExit('docker build failure: %s' % b.build_status)

        # Successful build
        r = b.newRelease()
        b.app.save()
        log.info('Created %s', r)
