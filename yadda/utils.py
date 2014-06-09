# yadda.utils ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

import argparse
import re
import subprocess
import sys

def die(mesg):
    "Write a message to stderr, and exit the program"
    sys.stderr.write('Fatal: ')
    sys.stderr.write(mesg)
    sys.stderr.write("\n")
    exit(1)

def id(x):
    return x

SLUG_CHARS = '-_a-z0-9'
SLUG_RE = re.compile('^['+SLUG_CHARS+']+$')

def is_slug(s):
    return bool(SLUG_RE.match(s))

def slug_arg(s):
    "Type checker for a URL-safe slug"
    if is_slug(s): return s
    raise argparse.ArgumentTypeError\
        ("must contain characters only from -_a-z0-9")

BINDING_RE = re.compile('^([-_a-zA-Z0-9]+)=(.*)$')

def binding_arg(s):
    m = BINDING_RE.match(s)
    if m:
        return (m.group(1), m.group(2))
    raise argparse.ArgumentTypeError("must match VAR=VALUE pattern")


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

def say(opts, mesg, show=None, out=sys.stdout, level=1):
    """Write `mesg` to `out`, if verbose option is set

    Mesg can be a one-line string, or an arbitrary object if `show` is provided.
    The show function is expected to generate a sequence of one-line strings,
    when applied to the `mesg` object."""
    if opts.verbose >= level:
        if show:
            for line in show(mesg):
                say1(line, out)
        else:
            say1(mesg, out)
        out.flush()

def sayf(opts, fmt, *args):
    if opts.verbose:
        say1(fmt.format(*args), sys.stdout)
        sys.stdout.flush()

def say_call(opts, cmd, call=subprocess.check_call, **kwargs):
    mesg = ' '.join(cmd) if type(cmd) == list else cmd
    say(opts, mesg)
    return call(cmd, **kwargs)

def dry_call(opts, cmd, call=subprocess.check_call, **kwargs):
    mesg = ' '.join(cmd) if type(cmd) == list else cmd
    return dry_guard(opts, mesg, call, cmd, **kwargs)

def dry_guard(opts, mesg, f, *args, **kwargs):
    if opts.dry_run:
        say(opts, '(not) ' + mesg)
    else:
        say(opts, mesg)
        return f(*args, **kwargs)