from yadda import version

import pkgutil
import argparse
import yadda.commands

def main():
    args = argparse.ArgumentParser(prog='yadda', description='Yet another docker deploy app')
    args.add_argument('-V', '--version', action='version', version=version.full,
                      help='show program version information')
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument('-n', '--dry-run', action='store_true',
                        help='perform a trial run without making changes')
    common.add_argument('-v', '--verbose', action='store_true',
                        help='increase output about what is happening')
    common.add_argument('-C', '--directory', metavar='DIR',
                        help='change to DIR before doing anything else')
    subparse = args.add_subparsers(title='Commands')
    for imp, cmd, pkg in pkgutil.iter_modules(yadda.commands.__path__):
        if not pkg:
            m = imp.find_module(cmd).load_module(cmd)
            p = m.args(lambda **kwargs: subparse.add_parser
                       (cmd, parents=[common], **kwargs))
            p.set_defaults(func=m.run)
    opts = args.parse_args()
    opts.func(opts)

if __name__ == '__main__': main()
