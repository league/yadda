#!/usr/bin/env python
# yadda.main ▪ Main program that dispatches to sub-commands ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

from yadda import version
from yadda.container import LazyContainer, DryRunContainer
from yadda.models import Role
import argparse
import logging
import os
import pkgutil
import sys
import yadda.commands

def main(argv=sys.argv):
    opts = process_args(argv)
    container, console = configure_deps(opts)
    if opts.cmd == 'init':
        opts.ctor(container).run(opts)
    else:
        determine_app(container, opts)
        if opts.cmd == 'receive':
            set_formatter(console, opts.app.role)
        elif opts.target == opts.app.role: # We're in the right place
            opts.ctor(container).run(opts)
        else:
            host = getattr(opts.app, opts.target)
            if not host:
                raise SystemExit('%s does not specify %s host; try init again?' %
                                 (opts.app.name, opts.target))
            argv.append('--app')
            argv.append(opts.app.name)
            print("TODO: ssh %s %s " + argv)

def process_args(argv):
    opts = args().parse_args(argv[1:])
    opts.prog = argv[0]
    if opts.cmd == 'receive' or opts.dry_run:
        opts.verbose += 1
    return opts

def configure_deps(opts):
    container = DryRunContainer() if opts.dry_run else LazyContainer()
    console = logging.StreamHandler()
    set_formatter(console, None if opts.cmd == 'receive' else opts.target)
    log = container['log']
    log.addHandler(console)
    if opts.verbose >= 2:
        log.setLevel(logging.DEBUG)
        log_opts_wrapped(log, opts)
    elif opts.verbose == 1:
        log.setLevel(logging.INFO)
    else:
        log.setLevel(logging.WARNING)
    return container, console

def set_formatter(console, target):
    prefix = target + ' » ' if target else ''
    fmt = logging.Formatter(prefix + '%(levelname)s » %(message)s')
    console.setFormatter(fmt)

def log_opts_wrapped(log, opts):
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

def determine_app(container, opts):
    if not opts.app:
        opts.app = container['git'].get_local_config('yadda.app')
    if not opts.app:
        cwd = container['filesystem'].getcwd()
        opts.app, ext = os.path.splitext(os.path.basename(cwd))
    try:
        opts.app = container['appfactory'].load(opts.app)
    except KeyError:
        raise SystemExit("app '%s' not configured" % opts.app)

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
