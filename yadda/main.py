#!/usr/bin/env python
# yadda.main ▪ Main program that dispatches to sub-commands ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

from yadda import utils
from yadda import version, settings
from yadda.commands.init import InitCommand
from yadda.docker import Docker
from yadda.filesystem import ReadWriteFilesystem
from yadda.git import Git
from yadda.models import Role, AppFactory
from yadda.receive import Receive
from yadda.subproc import RealSubprocess
import argparse
import logging
import os
import pkgutil
import sys
import yadda.commands

console = logging.StreamHandler()

log = logging.getLogger('yadda')

def run_git_receive_hook():
    # Receive hook doesn't directly support dry-run, but we do configure it as
    # verbose.
    filesystem = ReadWriteFilesystem()
    setLogLevel(target='git', verbose=1)
    appfactory = AppFactory(filesystem=filesystem, datafile=settings.DATA_FILE)
    # Use working-dir basename to figure out app name.
    cwd = filesystem.getcwd()
    name, ext = os.path.splitext(os.path.basename(cwd))
    try:
        app = appfactory.load(name)
    except KeyError:
        raise SystemExit('App %s not configured; cannot deploy' % name)
    # Now that we have the app info, redo log format
    setLogLevel(target=app.role, verbose=1)
    # Instantiate receive handler
    subprocess = RealSubprocess()
    git = Git(filesystem=filesystem, subprocess=subprocess)
    docker = Docker(filesystem=filesystem, subprocess=subprocess, stdout=sys.stdout)
    r = Receive(filesystem, git, docker, appfactory, stdout=sys.stdout)
    r.run(app, sys.stdin)

filesystem = ReadWriteFilesystem()
subprocess = RealSubprocess()
git = Git(filesystem=filesystem, subprocess=subprocess)
appfactory = AppFactory(filesystem=filesystem, datafile=settings.DATA_FILE)

container = {}
container['filesystem'] = filesystem
container['git'] = git
container['appfactory'] = appfactory
container['stdout'] = sys.stdout
container['subprocess'] = subprocess

def wrap_opts_to_log(opts):
    buf = ''
    i = 0
    for k, v in vars(opts).items():
        if k == 'func':
            continue
        z = '%s=%r ' % (k, v)
        if i > 0 and i+len(z) > 64:
            log.debug(buf)
            buf = ''
            i = 0
        buf += z
        i += len(z)
    if(buf):
        log.debug(buf)

def main(argv=None):
    """Top-level entry point for the yadda program.

    We parse the command-line arguments, load the current app data (if
    available), and then invoke the sub-command or log in to a remote target to
    reinvoke this command.

    """
    log.addHandler(console)
    if sys.argv[0].endswith('receive'):
        return run_git_receive_hook()
    if argv is None:
        argv = sys.argv[1:]
    opts = args().parse_args(argv)
    opts.prog = sys.argv[0]
    if opts.dry_run and not opts.verbose:
        opts.verbose = 1
    setLogLevel(opts.target, opts.verbose)
    assert(hasattr(opts, 'cmd'))  # Verify the sub-command parsers added
    assert(hasattr(opts, 'func')) # the correct attributes

    if log.isEnabledFor(logging.DEBUG):
        wrap_opts_to_log(opts)

    if opts.cmd == 'init':
        return InitCommand(container).run(opts)
    else:
        return dispatch(opts, argv)

def setLogLevel(target, verbose):
    fmt = target + ' » %(levelname)s » %(message)s'
    console.setFormatter(logging.Formatter(fmt))
    if verbose == 0:
        log.setLevel(logging.WARNING)
    elif verbose == 1:
        log.setLevel(logging.INFO)
    else:
        log.setLevel(logging.DEBUG)

def dispatch(opts, argv):
    opts.dispatch = ''
    """Load the app context, and run sub-command on designated target."""
    if not opts.app:            # If not provided on command-line,
        try:                    # Look in .git/config
            utils.say(opts, 'Loading app name from .git/config')
            opts.app = git.get_local_config('yadda.app')
        except KeyError:
            raise SystemExit('app name not specified in .git/config; did you init?')
    try:
        opts.app = appfactory.load(opts.app)
        opts.dispatch = opts.app.role
    except KeyError:
        raise SystemExit('"%s" not found in %s; retry init?' %
                         (opts.app, settings.DATA_FILE))

    if opts.target == opts.app.role: # We're in the right place
        del opts.dispatch
        getattr(opts.ctor(container), opts.func)(opts)
    else:
        host = getattr(opts.app, opts.target)
        if not host:
            raise SystemExit('%s does not specify %s host; try init again?' %
                             (opts.app.name, opts.target))
        argv.append('--app')
        argv.append(opts.app.name)
        utils.say_call(opts, [settings.SSH, host, 'yadda'] + argv)

def args():
    """Specify command-line argument specification for entire program.

    Modules within the `yadda.commands` package add sub-commands by providing a
    function args(CMD, SUBPARSE, COMMON). That function should add a parser to
    SUBPARSE, and set the `cmd` attribute to the sub-command name (CMD) and set
    the `func` attribute to a callback to implement that sub-command.

    """
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument('-n', '--dry-run', action='store_true',
                        help='perform trial run without making changes; implies -v')
    common.add_argument('-v', '--verbose', action='count', default=0,
                        help='increase output about what is happening')
    common.add_argument('-a', '--app', metavar='NAME',
                        help='application on which to operate')
    common.add_argument('-t', '--target', choices=Role.all, default=Role.dev,
                        help='host on which to run this command')
    ap = argparse.ArgumentParser(prog='yadda', parents=[common],
                                 description='Yet another docker deploy app')
    ap.add_argument('-V', '--version', action='version', version=version.full,
                      help='show program version information')
    subparse = ap.add_subparsers(title='Commands')
    for imp, cmd, pkg in pkgutil.iter_modules(yadda.commands.__path__):
        if not pkg:
            m = imp.find_module(cmd).load_module(cmd)
            m.args(cmd, subparse, common)
    return ap

if __name__ == '__main__': main()
