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
        say_call(opts, ['ssh', opts.live, 'yadda', 'init', '-t', Role.live] +
                 opts_to_list(opts))

def opts_to_list(opts):
    new_opts = [opts.name]
    if opts.qa:
        new_opts.append(opts.qa)
        if opts.live:
            new_opts.append(opts.live)
    if opts.dry_run: new_opts.append('-n')
    if opts.verbose: new_opts.append('-' + 'v' * opts.verbose)
    if opts.database: new_opts.append('-d')
    if opts.subdir:
        new_opts.append('-C')
        new_opts.append(opts.subdir)
    return new_opts

def args(cmd, subparse, common):
    p = subparse.add_parser(cmd, parents=[common],
                            help='initialize a new application',
                            description='Initialize a new application')
    p.add_argument('-d', '--database', action='store_true',
                   help='link container with database')
    p.add_argument('-C', '--subdir', metavar='SUBDIR',
                   help='change to SUBDIR before building')
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
        for av in 'role qa live subdir database'.split():
            ov = 'target' if av == 'role' else av
            if getattr(opts, ov) != getattr(app, av):
                txt = av+' host' if av in Role.all else av
                sayf(opts, 'changing {} {} to {}', opts.name, txt,
                     getattr(opts, ov))
                setattr(app, av, getattr(opts, ov))
                change = True
    except KeyError:
        change = True
        sayf(opts, 'Creating app {} on {}', opts.name, opts.target)
        app = App(opts.name, role=opts.target, qa=opts.qa, live=opts.live,
                  subdir=opts.subdir, database=opts.database)
        Env(app).freeze()
    if change:
        app.maybe_save(opts)
    if opts.target == Role.dev:
        if git.has_dot_git():
            git.set_yadda_app(opts, app.name)
            if opts.qa:
                git.set_remote(opts, Role.qa, '%s:%s.git' % (opts.qa, app.name))
        else:
            print('Note: could not save app name to .git/config')
    elif opts.target == Role.qa:
        d = app.name + '.git'
        git.init_bare(opts, d)
        hook = os.path.join(d, os.path.join('hooks', 'pre-receive'))
        exe = os.path.realpath(sys.argv[0])
        dry_guard(opts, 'symlink %s -> %s' % (hook, exe),
                  force_symlink, exe, hook)
