# yadda.utils ▪ Various utility functions ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

import argparse
import errno
import os
import re
import subprocess
import sys

def die(mesg):
    "Write a message to stderr, and exit the program"
    sys.stderr.write('Fatal: ')
    sys.stderr.write(mesg)
    sys.stderr.write("\n")
    exit(1)

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

def say_call(opts, cmd, call=subprocess.check_call, **kwargs):
    mesg = ' '.join(cmd) if type(cmd) == list else cmd
    say(opts, mesg)
    try:
        return call(cmd, **kwargs)
    except subprocess.CalledProcessError as exn:
        die('command returned non-zero exit status: %d' % exn.returncode)

def dry_call(opts, cmd, call=subprocess.check_call, **kwargs):
    mesg = ' '.join(cmd) if type(cmd) == list else cmd
    return dry_guard(opts, mesg, call, cmd, **kwargs)

def dry_guard(opts, mesg, f, *args, **kwargs):
    if opts.dry_run:
        say(opts, '(not) ' + mesg)
    else:
        say(opts, mesg)
        return f(*args, **kwargs)

def force_symlink(file1, file2):
    'Simulate `ln -sf`, replacing `file2` if it exists already.'
    try:
        os.symlink(file1, file2)
    except OSError, e:
        if e.errno == errno.EEXIST:
            os.remove(file2)
            os.symlink(file1, file2)

class save_cwd(object):
    def __enter__(self):
        self.prev = os.getcwd()
    def __exit__(self, type, value, traceback):
        os.chdir(self.prev)
