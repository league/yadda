# yadda.commands.env ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

from copy import copy
from yadda import git, utils
from yadda.models import App
import json
import sys

def args(cmd, subparse, common):
    'show or adjust the application environment'
    p = subparse.add_parser(cmd, parents=[common], help=args.__doc__,
                            description=args.__doc__.capitalize())
    p.set_defaults(cmd=cmd)
    vs = p.add_subparsers(title='Variants')

    ls = vs.add_parser('ls', parents=[common], help=run_ls.__doc__,
                       description=run_ls.__doc__.capitalize())
    ls.add_argument('-f', '--format', choices=sorted(FORMATS),
                    default='human',
                    help='how to output the environment (default human)')
    ls.add_argument('revision', metavar='REVISION', nargs='?', type=int,
                    help='version of the environment (default latest)')
    ls.set_defaults(func=run_ls)

    set = vs.add_parser('set', parents=[common], help=run_set.__doc__,
                           description=run_set.__doc__.capitalize())
    set.add_argument('bindings', metavar='VAR=VALUE', nargs='+',
                     type=utils.binding_arg,
                     help='bindings to add to environment')
    set.set_defaults(func=run_set)

    rm =vs.add_parser('rm', parents=[common], help=run_rm.__doc__,
                      description=run_rm.__doc__.capitalize())
    rm.add_argument('variables', metavar='VAR', nargs='+',
                    help='variables to remove from environment')
    rm.set_defaults(func=run_rm)

    log = vs.add_parser('log', parents=[common],
                         help='list changes to the environment over time')
    log.set_defaults(func=run_log)

    return p

def run_ls(opts):
    'list the values of variables in the environment'
    i = opts.revision-1 if opts.revision else -1
    FORMATS[opts.format](opts.app.envs[i].env)

def show_sh(e):
    for k, v in e.iteritems():
        print("%s='%s'; export %s;" % (k, v, k))

def show_csh(e):
    for k, v in e.iteritems():
        print("setenv %s '%s';" % (k, v))

def show_json(e):
    print(json.dumps(e))

def show_human(e):
    w = max([len(k) for k in e])
    for k in sorted(e):
        print('%-*s = %s' % (w, k, e[k]))

FORMATS={'sh': show_sh,
         'csh': show_csh,
         'json': show_json,
         'human': show_human}

def run_log(opts):
    if not opts.app.envs:
        print('No environments')
    else:
        for e in opts.app.envs:
            print(e.version() + ': ' + e.history)

def run_set(opts):
    'add new bindings to the environment and redeploy'
    e = copy(opts.app.envs[-1])
    for b in opts.bindings:
        e = e.set(b[0], b[1])
    e.freeze()
    opts.app.maybe_save(opts)
    print(e.version() + ': ' + e.history)

def run_rm(opts):
    'remove bindings from the environment and redeploy'
    e = copy(opts.app.envs[-1])
    for v in opts.variables:
        e = e.rm(v)
    e.freeze()
    opts.app.maybe_save(opts)
    print(e.version() + ': ' + e.history)
