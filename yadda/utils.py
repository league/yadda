# yadda.utils ▪ Various utility functions ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

from __future__ import unicode_literals
import argparse
import re
import sys

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

def say1(opts, line, out=sys.stdout):
    "Write one-line message to `out`, with newline"
    out.write('%-5s» ' % (opts.dispatch if hasattr(opts,'dispatch')
                          else opts.target))
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
                say1(opts, line, out)
        else:
            say1(opts, mesg, out)
        out.flush()

def sayf(opts, fmt, *args):
    if opts.verbose:
        say1(opts, fmt.format(*args), sys.stdout)
        sys.stdout.flush()

SHELL_QUOTABLE = re.compile('^[ -_0-9a-zA-Z:/]*$')

def shell_quote(word):
    assert SHELL_QUOTABLE.match(word), 'quoting %r not supported' % word
    return "'" + word + "'"
