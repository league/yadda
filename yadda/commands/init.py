# yadda.commands.init ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

from yadda import git
from yadda.models import Role, App, Env
from yadda.utils import *
import os

def pre_run(opts):
    """Run the init command on applicable hosts.

    In this case, the `--target` argument tells us where we ARE, not where to
    run. If we're on dev we'll hop to qa, and from qa to live.

    """
    opts.func(opts)         # Run locally
    if opts.target == Role.dev and opts.qa:
        say_call(opts, ['ssh', opts.qa, 'yadda', 'init', '-t', Role.qa] +
                 opts_to_list(opts))
    elif opts.target == Role.qa and opts.live:
        say_call(opts, ['ssh', opts.qa, 'yadda', 'init', '-t', Role.live] +
                 opts_to_list(opts))

def opts_to_list(opts):
    new_opts = [opts.name]
    if opts.qa:
        new_opts.append(opts.qa)
        if opts.live:
            new_opts.append(opts.live)
    if opts.dry_run: new_opts.append('-n')
    if opts.verbose: new_opts.append('-' + 'v' * opts.verbose)
    return new_opts

def args(cmd, subparse, common):
    p = subparse.add_parser(cmd, parents=[common],
                            help='initialize a new application',
                            description='Initialize a new application')
    p.add_argument('name', metavar='NAME', type=slug_arg,
                   help='name of the app to initialize')
    for r in Role.all[1:]:
        p.add_argument(r, metavar=r.upper()+'-HOST', nargs='?',
                       help='host to configure for '+Role.description[r])
    p.set_defaults(cmd=cmd, func=run)

def run(opts):
    change = False
    try:
        app = App.load(opts.name)
        if opts.target != app.role:
            sayf(opts, 'changing {} role to {}', opts.name, opts.target)
            app.role = opts.target
            change = True
        if opts.qa and opts.qa != app.qa:
            sayf(opts, 'changing {} qa host to {}', opts.name, opts.qa)
            app.qa = opts.qa
            change = True
        if opts.live and opts.live != app.live:
            sayf(opts, 'changing {} live host to {}', opts.name, opts.live)
            app.live = opts.live
            change = True
    except KeyError:
        change = True
        sayf(opts, 'Creating app {} on {}', opts.name, opts.target)
        app = App(opts.name, opts.target, opts.qa, opts.live)
        Env(app).freeze()
    if change:
        dry_guard(opts, 'saving app data', app.save)
