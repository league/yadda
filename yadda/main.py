# yadda.main ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

from yadda import version
from yadda.models import Role
from yadda.utils import say, show_opts
import argparse
import pkgutil
import sys
import yadda.commands

def run(opts):
    opts.func(opts)

def main(argv=None, run=run):
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument('-n', '--dry-run', action='store_true',
                        help='perform a trial run without making changes')
    common.add_argument('-v', '--verbose', action='store_true',
                        help='increase output about what is happening')
    common.add_argument('-a', '--app', nargs=1, metavar='NAME',
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
            m.args(subparse, common)
    opts = ap.parse_args(sys.argv[1:] if argv is None else argv)
    say(opts, opts, show=show_opts)
    return run(opts)

if __name__ == '__main__': main()
