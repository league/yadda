# yadda.commands.env ▪ Show or adjust app environment ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

from __future__ import unicode_literals
from copy import copy
from yadda import utils
import json
import sys

class EnvCommand(object):
    'show or adjust the application environment'

    FORMATS=['sh', 'csh', 'json', 'human']

    def __init__(self, container):
        self.stdout = container['stdout']

    def run(self, opts):
        getattr(self, opts.func)(opts)

    def run_ls(self, opts):
        'list the values of variables in the environment'
        if opts.revision:
            try:
                e = opts.app.envBySerial(opts.revision)
            except IndexError:
                raise SystemExit('no such revision: %d' % opts.revision)
        else:
            e = opts.app.envs[-1]
        if opts.format == 'json':
            self.show_json(e.env)
        else:
            self.stdout.write('\n'.join(getattr(self, 'gen_' + opts.format)(e.env)))
        self.stdout.write('\n')

    def show_json(self, env):
        # Grr, can't find a way to please both
        if sys.version_info.major == 3:
            self.stdout.write(json.dumps(env, ensure_ascii=False)) # pragma: no cover
        else:
            self.stdout.write(unicode(json.dumps(env))) # pragma: no cover

    def gen_csh(self, env):
        for k, v in env.items():
            yield "setenv %s '%s';" % (k, v)

    def gen_sh(self, env):
        for k, v in env.items():
            yield "%s='%s'; export %s;" % (k, v, k)

    def gen_human(self, env):
        w = max([len(k) for k in env])
        for k in sorted(env):
            yield '%-*s = %s' % (w, k, env[k])

    def summarize_version(self, e):
        self.stdout.write(e.version() + ': ' + e.history + '\n')

    def modify(self, opts, func):
        e = func(opts, copy(opts.app.envs[-1])).freeze()
        opts.app.save()
        self.summarize_version(e)

    def func_set(self, opts, e):
        for b in opts.bindings:
            e = e.set(b[0], b[1])
        return e

    def run_set(self, opts):
        'add new bindings to the environment and redeploy'
        self.modify(opts, self.func_set)

    def func_rm(self, opts, e):
        for v in opts.variables:
            e = e.rm(v)
        return e

    def run_rm(self, opts):
        'remove bindings from the environment and redeploy'
        self.modify(opts, self.func_rm)

    def run_log(self, opts):
        'list changes to the environment over time'
        for e in opts.app.envs:
            self.summarize_version(e)

def parser_for(variant, vs, common, *args, **kwargs):
    method = getattr(EnvCommand, 'run_' + variant)
    p = vs.add_parser(variant, parents=[common], help=method.__doc__,
                      description=method.__doc__.capitalize())
    p.set_defaults(func=method.__name__)
    return p

def args(cmd, subparse, common):
    p = subparse.add_parser(cmd, parents=[common], help=EnvCommand.__doc__,
                            description=EnvCommand.__doc__.capitalize())
    p.set_defaults(cmd=cmd, ctor=EnvCommand)
    vs = p.add_subparsers(title='Variants')

    ls = parser_for('ls', vs, common)
    ls.add_argument('-f', '--format', choices=EnvCommand.FORMATS,
                    default='human',
                    help='how to output the environment (default human)')
    ls.add_argument('revision', metavar='REVISION', nargs='?', type=int,
                    help='version of the environment (default latest)')

    set = parser_for('set', vs, common)
    set.add_argument('bindings', metavar='VAR=VALUE', nargs='+',
                     type=utils.binding_arg,
                     help='bindings to add to environment')

    rm = parser_for('rm', vs, common)
    rm.add_argument('variables', metavar='VAR', nargs='+',
                    help='variables to remove from environment')

    log = parser_for('log', vs, common)

    return p
