# yadda.models

from copy import copy
from datetime import datetime
from yadda import version
import hashlib

class Role(object):
    dev = 'dev'
    qa = 'qa'
    live = 'live'

    @classmethod
    def all(cls):
        return [cls.dev, cls.qa, cls.live]

class App(object):
    def __init__(self, name, role=Role.dev, qa=None, live=None):
        assert(isinstance(name, str))
        assert(role in Role.all())
        self.name = name
        self.role = role
        self.qa = qa
        self.live = live
        self.envs = []
        self.builds = []
        self.releases = []

    def __str__(self):
        return self.name

    @staticmethod
    def next_serial(xs):
        return 1 + max([x.serial for x in xs] or [0])

class AppComponent(object):
    def __init__(self, app, ls=None):
        assert(isinstance(app, App))
        self.app = app
        self.serial = None
        if ls is not None: self.insert_into(ls)

    def insert_into(self, ls):
        self.serial = App.next_serial(ls)
        ls.insert(0, self)

    def version(self):
        return self.app.role + '.' + (str(self.serial) if self.serial else '??')

class Env(AppComponent):
    def __init__(self, app):
        super(Env,self).__init__(app)
        self.frozen = False
        self.serial = None
        self.env = {'YADDA': version.full}

    def __copy__(self):
        assert(self.frozen)
        k = Env(a)
        k.env = copy(self.env)
        return k

    def set(self, k, v):
        assert(not self.frozen)
        self.env[k] = v
        return self

    def rm(self, k):
        assert(not self.frozen)
        del self.env[k]
        return self

    def freeze(self):
        if not self.frozen:
            self.frozen = self.checksum()
            self.timestamp = datetime.now()
            self.insert_into(self.app.envs)
        return self

    def checksum(self):
        h = hashlib.sha1()
        for k in sorted(self.env):
            s = '((%s)(%s))' % (k, self.env[k])
            h.update(s.encode())
        return h.hexdigest()

    def version(self):
        v = super(Env,self).version()
        if self.frozen: return v + '.' + self.frozen[:5]
        else: return v

    def __str__(self):
        buf = 'env ' + self.version()
        if self.frozen:
            buf += ' ' + self.frozen
        w = max([len(k) for k in self.env])
        for k in sorted(self.env):
            buf += '\n  %-*s = %s' % (w, k, self.env[k])
        return buf

class Build(AppComponent):
    def __init__(self, app, git_hash):
        super(Build,self).__init__(app, app.builds)
        self.git_hash = git_hash
        self.image_id = None
        self.build_loc = app.role
        self.build_start = datetime.now()

    def git_abbrev(self):
        return self.git_hash[:5]

    def version(self):
        return '.'.join([self.build_loc, str(self.serial), self.git_abbrev()])

    def tag(self):
        return self.app.name + ':' + self.version()

    def __str__(self):
        buf = self.tag()
        if self.image_id:
            buf += ' »' + self.image_id
        return buf

class Release(AppComponent):
    def __init__(self, app, build, env):
        super(Release, self).__init__(app, app.releases)
        assert(isinstance(build, Build))
        assert(isinstance(env, Env))
        assert(env.frozen)
        self.build = build
        self.env = env

    def __str__(self):
        return 'release %s = build %s + env %s' % (
            self.version(),
            self.build.version(),
            self.env.version()
            )

a = App('suspicious-einstein')
print(str(a))
e = Env(a).freeze()
f = copy(e).set('DATABASE', 'postgresql').freeze()
g = copy(f).set('BLORQ', '11932')
h = copy(f).set('SUPER_SECRET', 'J/2JBzzb^>zWSuKNNJ2"+\'TY]9czMcm)YW9?+2u}') \
    .rm('DATABASE').freeze()
print(e)
print(f)
print(g)
print(h)

b = Build(a, 'fb36c55dec633a2a901cd65f119110aed443abd6')
c = Build(a, '32f3f306b49f728a65583a56e39232a463d90b6b')
c.image_id = 'aaa'
print(b)
print(c)

r1 = Release(a, b, f)
r2 = Release(a, c, f)
r3 = Release(a, c, h)
print(r1)
print(r2)
print(r3)
