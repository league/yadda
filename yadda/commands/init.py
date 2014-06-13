# yadda.commands.init ▪ Initialize a new application ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

from yadda import utils
from yadda.models import Role
import os

class InitCommand(object):
    'initialize a new application'

    def __init__(self, container):
        self.appfactory = container['appfactory']
        self.filesystem = container['filesystem']
        self.git        = container['git']
        self.stdout     = container['stdout']
        self.subprocess = container['subprocess']
        self.log        = container['log']

    def run(self, opts):
        self.run_local(opts)
        if opts.target == Role.dev and opts.qa:
            self.subprocess.check_call(
                ['ssh', opts.qa, 'yadda', 'init', '-t', Role.qa] +
                self.opts_list(opts))
        elif opts.target == Role.qa and opts.live:
            self.subprocess.check_call(
                ['ssh', opts.live, 'yadda', 'init', '-t', Role.live] +
                self.opts_list(opts))

    def opts_list(self, opts):
        new_opts = [opts.name]
        if opts.qa:
            new_opts.append(opts.qa)
            if opts.live:
                new_opts.append(opts.live)
        if opts.dry_run:
            new_opts.append('-n')
        if opts.verbose:
            new_opts.append('-' + 'v' * opts.verbose)
        if opts.database:
            new_opts.append('-d')
        if opts.subdir:
            new_opts.append('-C')
            new_opts.append(opts.subdir)
        return new_opts

    def run_local(self, opts):
        self.change = False
        try:
            self.app = self.appfactory.load(opts.name)
            self.detect_changes(opts)
        except KeyError:
            self.change = True
            self.log.info('Creating app %s on %s', opts.name, opts.target)
            self.app = self.appfactory.new(
                opts.name, role=opts.target, qa=opts.qa, live=opts.live,
                subdir=opts.subdir, database=opts.database)
        if self.change:
            self.app.save()
        if opts.target == Role.dev:
            self.set_remote()
        elif opts.target == Role.qa:
            self.init_repo(opts)

    def set_remote(self):
        if self.git.is_working_dir():
            self.git.set_local_config('yadda.app', self.app.name)
            if self.app.qa:
                self.git.set_remote(Role.qa, '%s:%s.git' %
                               (self.app.qa, self.app.name))
        else:
            self.log.warn('could not save app name to .git/config')

    def init_repo(self, opts):
        d = self.app.name + '.git'
        self.git.init_bare(d)
        hook = os.path.join(d, os.path.join('hooks', 'pre-receive'))
        exe = os.path.realpath(opts.prog)
        self.filesystem.force_symlink(exe, hook)

    APP_VARS = {'role': 'target',
                'qa': 'qa',
                'live': 'live',
                'subdir': 'subdir',
                'database': 'database'}

    def detect_changes(self, opts):
        for av, ov in InitCommand.APP_VARS.items():
            if getattr(opts, ov) != getattr(self.app, av):
                txt = av+' host' if av in Role.all else av
                self.log.info('changing %s %s to %s', opts.name, txt,
                              getattr(opts, ov))
                setattr(self.app, av, getattr(opts, ov))
                self.change = True

def args(cmd, subparse, common):
    p = subparse.add_parser(cmd, parents=[common], help=InitCommand.__doc__,
                            description=InitCommand.__doc__.capitalize())
    p.set_defaults(cmd=cmd, ctor=InitCommand)
    p.add_argument('-d', '--database', action='store_true',
                   help='link container with database')
    p.add_argument('-C', '--subdir', metavar='SUBDIR',
                   help='change to SUBDIR before building')
    p.add_argument('name', metavar='NAME', type=utils.slug_arg,
                   help='name of the app to initialize')
    for r in Role.all[1:]:
        p.add_argument(r, metavar=r.upper()+'-HOST', nargs='?',
                       help='host to configure for '+Role.description[r])
