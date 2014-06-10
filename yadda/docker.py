# yadda.docker ▪ Python interface to docker commands ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

from datetime import datetime
from uuid import uuid4 as uuid
from yadda.models import Build
from yadda.settings import HASH_ABBREV, DOCKER
from yadda.utils import save_cwd, dry_call, die
import os
import subprocess
import sys
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
        b.build_status = None
        try:
            # Hook to avoid executing docker during unit tests
            if os.environ.get('YADDA_TEST_BAN') == DOCKER: return
            p1 = subprocess.Popen('%s build -t %s . 2>&1' % (DOCKER, t),
                                  shell=True,
                                  stdout=subprocess.PIPE)
            p2 = subprocess.Popen(['tee', log],
                                  stdin=p1.stdout,
                                  stdout=sys.stdout)
            p1.stdout.close()
            p2.communicate()
            b.build_status = p1.wait()
            with open(log, 'r') as h:
                b.build_log = h.read()
        except IOError:         # log was probably not written; ignore
            pass
        finally:
            b.build_finish = datetime.now()
            b.app.save()
            try:
                os.unlink(log)
            except OSError:
                pass
            if b.build_status != 0:
                die('docker build failure: ' + str(b.build_status))
