# yadda.receive ▪ Implement the git pre-receive hook ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

from yadda.docker import Docker
from yadda.git import Git
from yadda.filesystem import RealFilesystem
from yadda.models import App, Build, Role, Release
from yadda.settings import HASH_ABBREV
from yadda.utils import die, sayf
import argparse
import os
import subprocess
import sys

filesystem = RealFilesystem()
git = Git(filesystem=filesystem, subprocess=subprocess)
docker = Docker(filesystem=filesystem, subprocess=subprocess)

def run(home=os.environ['HOME'], input=sys.stdin):
    commit = git.receive_master_commit(input)
    if not commit:
        print('Note: No update to master')
        sys.exit(0)
    name, ext = os.path.splitext(os.path.basename(os.getcwd()))
    try:
        app = App.load(name)
    except KeyError:
        die('Warning: app %s not configured, cannot deploy' % name)

    opts = argparse.Namespace(verbose=1, dry_run=False, target=app.role)
    workdir = os.path.join(home, '%s-%s' %
                           (name, commit[:HASH_ABBREV]))
    if not os.path.isdir(workdir): os.mkdir(workdir)
    b = Build(app, commit, workdir=workdir)
    app.save()                  # checkpoint

    sayf(opts, 'Starting build {} in {}', b.tag(), workdir)
    subprocess.check_call(
        'git archive "%s" | tar -x -C "%s"' % (commit, workdir),
        shell=True
    )
    if b.app.subdir:
        workdir = os.path.join(workdir, b.app.subdir)
    b.build_status, b.build_log = docker.build(b.tag(), workdir)
    b.build_finish = datetime.now()
    b.app.save()
    if b.build_status != 0:
        die('docker build failure: ' + str(b.build_status))

    r = Release(b, b.app.envs[-1])
    b.app.save()
    sayf(opts, 'Created %s' % r)
