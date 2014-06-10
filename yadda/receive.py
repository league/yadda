# yadda.receive ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

from yadda import git
from yadda.utils import die
import os
import subprocess
import sys

def run():
    c = git.receive_master_commit()
    if not c:
        print('Note: No update to master')
        sys.exit(0)
    name, ext = os.path.splitext(os.path.basename(os.getcwd()))
    try:
        app = App.load(name)
    except KeyError:
        die('Warning: app %s not configured, cannot deploy' % name)
    commit = c[:5]
    workdir = os.path.join(os.environ['HOME'], '%s-%s' % (label, commit))
    b = Build(app, c, workdir=workdir)
    app.save()
    print('Starting build ' + b.tag() + ' in ' + workdir)
    if not os.path.isdir(workdir): os.mkdir(workdir)
    subprocess.check_call(
        'git archive "%s" | tar -x -C "%s"' % (commit, workdir),
        shell=True
    )
    os.chdir(workdir)
