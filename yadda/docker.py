# yadda.docker ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

from yadda.models import Build
from yadda.utils import save_cwd, dry_call
import os
import subprocess

def build(opts, b):
    assert(isinstance(b, Build))
    with save_cwd() as cwd:
        os.chdir(b.workdir)
        if b.app.subdir and os.path.isdir(b.app.subdir):
            os.chdir(b.app.subdir)
        result = dry_call(opts, ['docker', 'build', '-t', b.tag(), '.'],
                          call=subprocess.check_output)
        b.build_log = result
        b.save()
