# yadda.docker ▪ Python interface to docker commands ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

from uuid import uuid4 as uuid
from yadda.models import Build
from yadda.settings import HASH_ABBREV
from yadda.utils import save_cwd, dry_call
import os
import subprocess
import tempfile

def build(opts, b):
    assert(isinstance(b, Build))
    with save_cwd() as cwd:
        os.chdir(b.workdir)
        if b.app.subdir and os.path.isdir(b.app.subdir):
            os.chdir(b.app.subdir)
        t = b.tag()
        log = os.path.join(tempfile.gettempdir(),
                           '%s.%s' % (t, uuid().hex[:HASH_ABBREV]))
        try:
            dry_call(opts, 'docker build -t %s . | tee %s' % (t, log), shell=True)
            with open(log, 'r') as h:
                b.build_log = h.read()
                b.app.save()
        finally:
            os.unlink(log)
