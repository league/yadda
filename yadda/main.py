#!/usr/bin/env python
# yadda.main ▪ Main program that dispatches to sub-commands ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

from yadda import utils
from yadda import version, settings, receive
from yadda.commands import init
from yadda.filesystem import RealFilesystem
from yadda.git import Git
from yadda.models import Role, App, AppFactory
from yadda.receive import Receive
import argparse
import os.path
import pkgutil
import subprocess
import sys
import yadda.commands

filesystem = RealFilesystem()
git = Git(filesystem=filesystem, subprocess=subprocess)
appfactory = AppFactory(filesystem=filesystem, datafile=settings.DATA_FILE)

def main(argv=None):
    """Top-level entry point for the yadda program.

    We parse the command-line arguments, load the current app data (if
    available), and then invoke the sub-command or log in to a remote target to
    reinvoke this command.

    """
    if sys.argv[0].endswith('receive'):
        return Receive().run()
    if argv is None:
        argv = sys.argv[1:]
    opts = args().parse_args(argv)
    if opts.dry_run and not opts.verbose:
        opts.verbose = 1
    assert(hasattr(opts, 'cmd'))  # Verify the sub-command parsers added
    assert(hasattr(opts, 'func')) # the correct attributes
    utils.say(opts, opts, show=utils.show_opts, level=2)

    if opts.cmd == 'init':
        return init.pre_run(opts)
    else:
        return dispatch(opts, argv)

def dispatch(opts, argv):
    opts.dispatch = ''
    """Load the app context, and run sub-command on designated target."""
    if not opts.app:            # If not provided on command-line,
        try:                    # Look in .git/config
            utils.say(opts, 'Loading app name from .git/config')
            opts.app = git.get_local_config('yadda.app')
        except KeyError:
            utils.die('app name not specified in .git/config; did you init?')
    try:
        opts.app = appfactory.load(opts.app)
        opts.dispatch = opts.app.role
    except KeyError:
        utils.die('"%s" not found in %s; retry init?' %
                  (opts.app, settings.DATA_FILE))

    if opts.target == opts.app.role: # We're in the right place
        del opts.dispatch
        opts.func(opts)
    else:
        host = getattr(opts.app, opts.target)
        if not host:
            die('%s does not specify %s host; try init again?' %
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
    common.add_argument('-v', '--verbose', action='count',
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
