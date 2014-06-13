# yadda.receive ▪ Implement the git pre-receive hook ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

from datetime import datetime
from yadda.settings import HASH_ABBREV
import os.path

def args(cmd, subparse, common):
    p = subparse.add_parser(cmd, help=Receive.__doc__,
                            description=Receive.__doc__.capitalize())
    p.set_defaults(cmd=cmd, ctor=Receive)

class Receive(object):
    'used only for git receive hook'
    def __init__(self, container):
        self.log        = container['log']
        self.filesystem = container['filesystem']
        self.git        = container['git']
        self.docker     = container['docker']
        self.appfactory = container['appfactory']
        self.stdout     = container['stdout']

    def run(self, app, stdin):
        # Determine latest commit to master
        commit = self.git.receive_master_commit(stdin)
        if not commit:
            self.stdout.write('Note: no update to master\n')
            raise SystemExit(0) # Return 0 so it doesn't abort push

        # Check out into a fresh working dir
        workdir = os.path.join(self.filesystem.home(),
                               app.name + '-' + commit[:HASH_ABBREV])
        self.filesystem.maybe_mkdir(workdir)
        b = app.newBuild(commit, workdir=workdir)
        self.log.info('Starting build %s in %s', b.tag(), workdir)
        app.save()
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
        self.log.info('Created %s', r)
