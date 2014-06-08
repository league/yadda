# yadda.main ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

from yadda import version

from yadda.utils import say, show_opts
import argparse
import pkgutil
import sys
import yadda.commands

def main(argv=None):
    ap = argparse.ArgumentParser(prog='yadda', description='Yet another docker deploy app')
    ap.add_argument('-V', '--version', action='version', version=version.full,
                      help='show program version information')
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument('-n', '--dry-run', action='store_true',
                        help='perform a trial run without making changes')
    common.add_argument('-v', '--verbose', action='store_true',
                        help='increase output about what is happening')
    subparse = ap.add_subparsers(title='Commands')
    for imp, cmd, pkg in pkgutil.iter_modules(yadda.commands.__path__):
        if not pkg:
            m = imp.find_module(cmd).load_module(cmd)
            p = m.args(lambda **kwargs: subparse.add_parser
                       (cmd, parents=[common], **kwargs))
            p.set_defaults(func=m.run)
    opts = ap.parse_args(sys.argv[1:] if argv is None else argv)
    say(opts, opts, show=show_opts)
    opts.func(opts)

if __name__ == '__main__': main()
