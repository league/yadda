# yadda.docker ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

import os
from yadda.utils import save_cwd, dry_call

def build(opts, b):
    with save_cwd() as cwd:
        os.chdir(b.workdir)
        if b.app.subdir and os.path.isdir(b.app.subdir):
            os.chdir(b.app.subdir)
        err = dry_call(opts, ['docker', 'build', '-t', b.tag(), '.'])
