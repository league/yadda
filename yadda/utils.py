# yadda.utils ▪ Various utility functions ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

from __future__ import unicode_literals
import argparse
import re

SLUG_CHARS = '-_a-z0-9'
SLUG_RE = re.compile('^['+SLUG_CHARS+']+$')

def is_slug(s):
    return bool(SLUG_RE.match(s))

def slug_arg(s):
    "Type checker for a URL-safe slug"
    if is_slug(s): return s
    raise argparse.ArgumentTypeError\
        ("must contain characters only from -_a-z0-9")
