# yadda.receive ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

from yadda import git
import os
import sys

def run():
    c = git.receive_master_commit()
    if not c:
        print('No update to master')
        sys.exit(0)
    name, ext = os.path.splitext(os.path.basename(os.getcwd()))
    print("THIS IS THE RECEIVE HOOK FOR " + name)
