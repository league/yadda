# yadda.receive ▪ Implement the git pre-receive hook ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

from yadda import git, docker
from yadda.models import App, Build, Role
from yadda.settings import HASH_ABBREV
from yadda.utils import die, sayf
import argparse
import os
import subprocess
import sys

def run():
    commit = git.receive_master_commit()
    if not commit:
        print('Note: No update to master')
        sys.exit(0)
    name, ext = os.path.splitext(os.path.basename(os.getcwd()))
    try:
        app = App.load(name)
    except KeyError:
        die('Warning: app %s not configured, cannot deploy' % name)

    opts = argparse.Namespace(verbose=1, dry_run=False, target=app.role)
    workdir = os.path.join(os.environ['HOME'], '%s-%s' %
                           (name, commit[:HASH_ABBREV]))
    if not os.path.isdir(workdir): os.mkdir(workdir)
    b = Build(app, commit, workdir=workdir)
    app.save()                  # checkpoint

    sayf(opts, 'Starting build {} in {}', b.tag(), workdir)
    subprocess.check_call(
        'git archive "%s" | tar -x -C "%s"' % (commit, workdir),
        shell=True
    )
    docker.build(opts, b)
