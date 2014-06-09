# yadda.commands.env ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

def args(cmds, common):
    p = cmds.add_parser('env', parents=[common],
                        help='show or adjust application environment',
                        description='Show or adjust application environment')
    vs = p.add_subparsers(title='Variants')

    show = vs.add_parser('show', parents=[common],
                         help='show the values of variables in environment REV')
    show.add_argument('revision', metavar='REVISION', default=1, nargs='?',
                      type=int)
    show.set_defaults(func=run_show)

    assign = vs.add_parser('set', parents=[common],
                           help='add new bindings to the environment and redeploy')
    assign.add_argument('bindings', metavar='VAR=VALUE', nargs='+')
    assign.set_defaults(func=run_set)

    rm =vs.add_parser('rm', parents=[common],
                      help='remove bindings from the environment and redeploy')
    rm.add_argument('variables', metavar='VAR', nargs='+')
    rm.set_defaults(func=run_rm)

    hist = vs.add_parser('history', parents=[common],
                         help='show changes to the environment over time')
    hist.set_defaults(func=run_history)
    return p

def run_show(opts):
    print("run_show")

def run_history(opts):
    print("run_history")

def run_set(opts):
    print("run_set")

def run_rm(opts):
    print("run_rm")
