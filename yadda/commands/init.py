# yadda.commands.init ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

def args(cmd):
    p = cmd(help='inithelp', description='initdesc')
    p.add_argument('label', help='label help')
    return p

def run(opts):
    print("INIT!")
