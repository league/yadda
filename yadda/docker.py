# yadda.docker ▪ Python interface to docker commands ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

from datetime import datetime
from uuid import uuid4 as uuid
from yadda.models import Build
from yadda.settings import HASH_ABBREV, DOCKER
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
        b.build_log = ''
        try:
            dry_call(opts, '%s build -t %s . | tee %s' %
                     (DOCKER, t, log), shell=True)
            with open(log, 'r') as h:
                b.build_log = h.read()
        except IOError:         # log was probably not written
            pass
        finally:
            b.build_finish = datetime.now()
            b.app.save()
            try:
                os.unlink(log)
            except OSError:
                pass
