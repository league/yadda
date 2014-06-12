# tests/log_setup.py ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

import logging
import unittest

class TestHandler(logging.Handler):
    def __init__(self, level=logging.NOTSET):
        super(TestHandler, self).__init__(level)
        self.records = []

    def emit(self, record):
        self.records.append(record)

handler = TestHandler()
handler.setFormatter(logging.Formatter('TEST-%(levelname)s: %(message)s'))

log = logging.getLogger('yadda')
log.setLevel(logging.DEBUG)
log.addHandler(handler)

class LogSetup(unittest.TestCase):
    def setUp(self):
        super(LogSetup, self).setUp()
        del handler.records[:]

    def assertInLastLog(self, elem):
        r = handler.records[-1]
        self.assertIn(elem, r.msg % r.args)
