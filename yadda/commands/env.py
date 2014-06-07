# yadda.commands.env ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

def args(cmd):
    p = cmd(help='envhelp', description='envdesc')
    return p

def run(opts):
    print("ENV")
    print(opts)
