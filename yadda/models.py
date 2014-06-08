# yadda.models ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

from contextlib import closing
from copy import copy
from datetime import datetime
from yadda import version, settings
import hashlib
import shelve

class Role(object):
    dev = 'dev'
    qa = 'qa'
    live = 'live'
    all = [dev, qa, live]

class App(object):
    def __init__(self, name, role=Role.dev, qa=None, live=None):
        assert(isinstance(name, str))
        assert(role in Role.all)
        self.name = name
        self.role = role
        self.qa = qa
        self.live = live
        self.envs = []
        self.builds = []
        self.releases = []

    def __str__(self):
        return self.name

    def save(self, file=settings.DATA_FILE):
        with closing(shelve.open(file)) as sh:
            sh[self.name] = self

    @staticmethod
    def next_serial(xs):
        return 1 + max([x.serial for x in xs] or [0])

    @staticmethod
    def load(name, file=settings.DATA_FILE):
        with closing(shelve.open(file)) as sh:
            app = sh[name]
            assert(isinstance(app, App))
            return app

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
        e = Env(self.app)
        e.env = copy(self.env)
        return e

    def set(self, k, v):
        e = copy(self) if self.frozen else self
        e.env[k] = v
        return e

    def rm(self, k):
        e = copy(self) if self.frozen else self
        if k in e.env:
            del e.env[k]
        return e

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

    def set_image_id(self, image_id):
        self.image_id = image_id

    def __str__(self):
        buf = self.tag()
        if self.image_id:
            buf += ' !' + self.image_id
        return buf

class Release(AppComponent):
    def __init__(self, build, env):
        super(Release, self).__init__(env.app, env.app.releases)
        assert(env.app == build.app)
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
