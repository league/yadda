# yadda.commands.env ▪ Show or adjust app environment ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

from __future__ import unicode_literals
from copy import copy
import argparse
import json
import re
import sys

class EnvCommand(object):
    'show or adjust the application environment'

    FORMATS=['sh', 'csh', 'json', 'human']

    def __init__(self, container):
        self.stdout = container['stdout']
        self.appfactory = container['appfactory']

    def run(self, opts):
        if opts.log:
            return self.run_log(opts)
        if opts.version is None:
            return self.run_ls(opts)
        try:                    # First try to interpret as VAR=VAL
            k, v = binding_arg(opts.version)
            opts.binding.insert(0, (k,v))
            return self.run_set_rm(opts)
        except argparse.ArgumentTypeError:
            return self.run_ls(opts)   # If that fails, must be VERSION

    def run_ls(self, opts):
        'list the values of variables in the environment'
        if opts.version:
            try:
                e = opts.app.envByFlexVersion(opts.version)
            except IndexError:
                raise SystemExit('no such revision: %s' % opts.version)
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

    def run_set_rm(self, opts):
        e = copy(opts.app.envs[-1])
        for k in opts.delete or []:
            e = e.rm(k)
        for k,v in opts.binding:
            e = e.set(k, v)
        e = e.freeze()
        self.appfactory.save(opts.app)
        self.summarize_version(e)

    def run_log(self, opts):
        'list changes to the environment over time'
        for e in opts.app.envs:
            self.summarize_version(e)

def args(cmd, subparse, common):
    p = subparse.add_parser(cmd, parents=[common], help=EnvCommand.__doc__,
                            description=EnvCommand.__doc__.capitalize())
    p.set_defaults(cmd=cmd, ctor=EnvCommand)
    p.add_argument('-l', '--log', action='store_true',
                   help='show history of changes to environment')
    p.add_argument('-d', '--delete', metavar='VAR', action='append',
                   help='remove variable from the environment')
    p.add_argument('-f', '--format', choices=EnvCommand.FORMATS,
                   default='human',
                   help='how to output the environment (default human)')
    p.add_argument('version', metavar='VERSION', nargs='?', type=str,
                   help='version to show')
    p.add_argument('binding', metavar='VAR=VAL', nargs='*', type=binding_arg,
                   help='version to show, or binding to add to environment')
    return p

BINDING_RE = re.compile('^([-_a-zA-Z0-9]+)=(.*)$')

def is_binding(s):
    return bool(BINDING_RE.match(s))

def binding_arg(s):
    m = BINDING_RE.match(s)
    if m:
        return (m.group(1), m.group(2))
    raise argparse.ArgumentTypeError("must match VAR=VALUE pattern")
