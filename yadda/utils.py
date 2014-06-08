# yadda.utils ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

import sys
import re
import argparse

def die(mesg):
    "Write a message to stderr, and exit the program"
    sys.stderr.write('Fatal: ')
    sys.stderr.write(mesg)
    sys.stderr.write("\n")
    exit(1)

SLUG_CHARS = '-_a-z0-9'
SLUG_RE = re.compile('^['+SLUG_CHARS+']+$')

def slug_arg(s):
    "Type checker for a URL-safe slug"
    if SLUG_RE.match(s): return s
    import argparse
    raise argparse.ArgumentTypeError\
        ("must contain characters only from -_a-z0-9")

def show_opts(opts):
    "Output generator for an options namespace"
    assert(isinstance(opts, argparse.Namespace))
    d = vars(opts)
    w = max([len(k) for k in d])
    for k, v in d.items():
        if not str(v).startswith('<'):
            yield 'option %-*s = %s' % (w, k, v)

def say1(line, out=sys.stdout):
    "Write one-line message to `out`, with newline"
    out.write('» ')
    out.write(line)
    out.write('\n')

def say(opts, mesg, show=None, out=sys.stdout):
    """Write `mesg` to `out`, if verbose option is set

    Mesg can be a one-line string, or an arbitrary object if `show` is provided.
    The show function is expected to generate a sequence of one-line strings,
    when applied to the `mesg` object."""
    if opts.verbose:
        if show:
            for line in show(mesg):
                say1(line, out)
        else:
            say1(mesg, out)
        out.flush()
