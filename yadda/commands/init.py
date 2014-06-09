# yadda.commands.init ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

from yadda import git
from yadda.models import Role, App, Env
from yadda.utils import *
import os

def args(cmds, common):
    p = cmds.add_parser('init', parents=[common],
                        help='initialize a new application',
                        description='Initialize a new application')
    p.add_argument('name', metavar='NAME', type=slug_arg,
                   help='name of the app to initialize')
    for r in Role.all[1:]:
        p.add_argument(r, metavar=r.upper()+'-HOST', nargs='?',
                       help='host to configure for '+Role.description[r])
    p.set_defaults(func=run)

def run(opts):
    try:
        app = App.load(opts.name)
        if opts.target != app.role:
            sayf(opts, 'Changing {} role to {}', opts.name, opts.target)
            app.role = opts.target
        if opts.qa and opts.qa != app.qa:
            sayf(opts, 'Changing {} qa host to {}', opts.name, opts.qa)
            app.qa = opts.qa
        if opts.live and opts.live != app.live:
            sayf(opts, 'Changing {} live host to {}', opts.name, opts.live)
            app.live = opts.live
    except KeyError:
        sayf(opts, 'Creating app {} on {}', opts.name, opts.target)
        app = App(opts.name, opts.target, opts.qa, opts.live)
        Env(app).freeze()
    app.save()
