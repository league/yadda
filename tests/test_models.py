# test_models ▪ Test the model classes ▪ coding: utf8
# ©2014 Christopher League <league@contrapunctus.net>

from tempfile import mkdtemp
from yadda.models import Role, App, Env, Build, Release
import argparse
import os
import unittest

def mkEnv(app):
    "Standardize the version number, so we can verify checksum."
    return Env(app).set('YADDA', '1.0')

class EnvModelTest(unittest.TestCase):
    def setUp(self):
        self.a = App('testcase', Role.dev)
        self.e = mkEnv(self.a)

    def test_app_str(self):
        str(self.a)
        str(self.e)
        str(self.e.freeze())

    def test_new_env(self):
        self.assertEqual(self.e.version(), 'dev.??')
        self.assertTrue('YADDA' in self.e.env)
        self.assertEqual(self.e.app, self.a)

    def test_set_rm_var(self):
        self.e.set('DATABASE', 'postgres')
        self.assertTrue('YADDA' in self.e.env)
        self.assertTrue('DATABASE' in self.e.env)
        self.e.rm('YADDA')
        self.assertTrue('YADDA' not in self.e.env)
        self.assertTrue('DATABASE' in self.e.env)

    def test_freeze(self):
        self.assertTrue(not self.e.frozen)
        self.e.set('SECRET', 'abc123').freeze()
        self.assertTrue(isinstance(self.e.serial, int))
        self.assertTrue(self.e.timestamp)
        self.assertEqual(1, len(self.a.envs))
        self.assertEqual('dev.1.13308', self.e.version())

    def test_copy(self):
        self.e.freeze()
        self.f = self.e.set('SECRET', 'abc123')
        self.assertTrue('SECRET' not in self.e.env)
        self.assertTrue('SECRET' in self.f.env)

    def test_serial(self):
        self.e.freeze()
        self.f = self.e.set('SECRET', 'boo299').set('ZZA', 'aa').freeze()
        self.assertEqual(2, len(self.a.envs))
        self.assertEqual(1, self.e.serial)
        self.assertEqual(2, self.f.serial)
        self.assertEqual('dev.2.1e880', self.f.version())



class BuildModelTest(unittest.TestCase):
    def setUp(self):
        self.a = App('mytest')
        self.b1 = Build(self.a, 'fb36c55dec633a2a901cd65f119110aed443abd6')

    def test_new_build(self):
        self.assertTrue(self.b1 in self.a.builds)
        self.assertEqual(1, len(self.a.builds))
        self.assertTrue(self.b1.git_hash.startswith(self.b1.git_abbrev()))
        self.assertEqual('dev.1.fb36c', self.b1.version())
        self.assertEqual('mytest:dev.1.fb36c', self.b1.tag())

    def test_build_str(self):
        str(self.b1)
        self.b1.set_image_id('e497c7c1bfbb69ab9fe556cc0bcb35c642c45eeed600ad812fdff0ce719f0610')
        str(self.b1)



class ReleaseTestSetup(unittest.TestCase):
    def setUp(self):
        self.a = App('fooo')
        self.e1 = mkEnv(self.a).freeze()
        self.b1 = Build(self.a, 'ab2320938')
        self.r1 = Release(self.b1, self.e1)
        self.b2 = Build(self.a, 'fc2920383')
        self.r2 = Release(self.b2, self.e1)
        self.e2 = self.e1.set('BAR', 'frites').freeze()
        self.r3 = Release(self.b2, self.e2)

class ReleaseTest(ReleaseTestSetup):
    def test_new_release(self):
        self.assertEqual('dev.1', self.r1.version())
        self.assertEqual('dev.2', self.r2.version())
        self.assertEqual('dev.3', self.r3.version())

    def test_release_str(self):
        str(self.r1)



class PickleModelsTest(ReleaseTestSetup):
    def setUp(self):
        super(PickleModelsTest, self).setUp()
        import pickle
        self.p = pickle.dumps(self.a)
        self.b = pickle.loads(self.p)

    def test_app_dag_preserved(self):
        self.assertNotEqual(self.a, self.b)
        self.assertEqual(len(self.a.envs), len(self.b.envs))
        self.assertEqual(len(self.a.builds), len(self.b.builds))
        self.assertEqual(len(self.a.releases), len(self.b.releases))
        for x in self.b.envs + self.b.builds + self.b.releases:
            self.assertEqual(self.b, x.app)

class SaveLoadTest(ReleaseTestSetup):
    def setUp(self):
        super(SaveLoadTest, self).setUp()
        self.dir = mkdtemp()
        self.file = os.path.join(self.dir, 'mydb')
        self.opts = argparse.Namespace(dry_run=True, verbose=1,
                                       target=Role.dev)

    def tearDown(self):
        super(SaveLoadTest, self).tearDown()
        try:
            os.unlink(self.file)
        except:
            pass
        os.rmdir(self.dir)

#    def test_save_load(self):
#        #self.a.save()
#        self.b = App.load(self.a.name, self.file)
#        self.assertNotEqual(self.a, self.b)
#        self.assertEqual(self.a.name, self.b.name)
#        self.assertEqual(self.a.role, self.b.role)
#        self.assertEqual(len(self.a.envs), len(self.b.envs))
#        self.assertEqual(len(self.a.builds), len(self.b.builds))
#        self.assertEqual(len(self.a.releases), len(self.b.releases))
#        for x in self.b.envs + self.b.builds + self.b.releases:
#            self.assertEqual(self.b, x.app)

    def test_list_apps(self):
        pass
        #self.a.save()
        #self.assertEqual(App.list(self.file), [self.a.name])

    def test_dry_save(self):
        #self.a.save() # TODO: maybe_save
        self.assertFalse(os.path.isfile(self.file))
