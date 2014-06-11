# tests/mock.subprocess ▪ Fake subprocess calls for testing ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

class MockSubprocess(object):
    def __init__(self):
        self.calls = []
        self.results = {}

    class CalledProcessError(BaseException):
        pass

    def check_call(self, cmd, *args, **kwargs):
        self.calls.append((cmd, args, kwargs))

    def check_output(self, cmd, *args, **kwargs):
        cmd = self.commandString(cmd)
        if cmd not in self.results:
            raise self.CalledProcessError()
        return self.results[cmd]

    #----------------------------------------------------------------

    @staticmethod
    def commandString(cmd):
        return ' '.join(cmd) if isinstance(cmd, list) else cmd

    def lastCall(self):
        return self.calls[-1]

    def lastCommand(self):
        return self.commandString(self.lastCall()[0])

    def assertLastCommandStartsWith(self, prefix):
        cmd = self.lastCommand()
        assert cmd.startswith(prefix), \
            "%r does not start with %r" % (cmd, prefix)

    def assertLastCommandContains(self, content):
        cmd = self.lastCommand()
        assert content in cmd, \
            "%r does not contain %r" % (cmd, content)
