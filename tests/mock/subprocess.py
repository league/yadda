# tests/mock.subprocess ▪ Fake subprocess calls for testing ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

import subprocess

class Closable(object):
    def close(self):
        pass

class MockPipe(object):
    def __init__(self, result=None):
        self.stdout = Closable()
        self.result = result
    def communicate(self):
        pass
    def wait(self):
        return self.result

class MockSubprocess(object):
    def __init__(self):
        self._calls = []
        self._results = []

    class CalledProcessError(BaseException):
        pass

    def check_call(self, cmd, *args, **kwargs):
        self._calls.append((cmd, args, kwargs))

    def check_output(self, cmd, *args, **kwargs):
        self._calls.append((cmd, args, kwargs))
        cmd = self.commandString(cmd)
        for r in self.getResult(cmd):
            return r
        raise self.CalledProcessError()

    PIPE = 'PIPE'

    def Popen(self, cmd, *args, **kwargs):
        self._calls.append((cmd, args, kwargs))
        for r in self.getResult(cmd):
            return MockPipe(r)
        return MockPipe()

    #----------------------------------------------------------------

    @staticmethod
    def commandString(cmd):
        return ' '.join(cmd) if isinstance(cmd, list) else cmd

    def lastCall(self):
        return self._calls[-1]

    def lastCommand(self):
        return self.commandString(self.lastCall()[0])

    def allCommands(self):
        for call in self._calls:
            yield self.commandString(call[0])

    def assertExistsCommand(self, pred):
        for call in self._calls:
            if pred(self.commandString(call[0])):
                return
        assert False

    def assertLastCommandStartsWith(self, prefix):
        cmd = self.lastCommand()
        assert cmd.startswith(prefix), \
            "%r does not start with %r" % (cmd, prefix)

    def assertLastCommandContains(self, content):
        cmd = self.lastCommand()
        assert content in cmd, \
            "%r does not contain %r" % (cmd, content)

    def provideResult(self, predicate, result):
        self._results.insert(0, (predicate, result))

    def provideResultEq(self, cmd, result):
        self.provideResult(lambda c: c == cmd, result)

    def getResult(self, cmd):
        cmd = self.commandString(cmd)
        for pred, r in self._results:
            if pred(cmd):
                yield r(cmd) if callable(r) else r
