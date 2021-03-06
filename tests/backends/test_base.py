import os.path

from gwf.exceptions import BackendError
from gwf import Target
from gwf.backends import Backend, PersistableDict
from gwf.backends.testing import TestingBackend

from tests import GWFTestCase


class TestBackendType(GWFTestCase):

    def setUp(self):
        self.backend = TestingBackend()

    def test_inject_target_defaults_into_target_options_on_submit(self):
        target = Target('TestTarget', inputs=[], outputs=[], options={}, working_dir='/some/dir')
        self.backend.submit(target, dependencies=[])
        self.assertEqual(target.options, {'cores': 2, 'memory': '18g'})

        target = Target('TestTarget', inputs=[], outputs=[], options={'cores': 32}, working_dir='/some/dir')
        self.backend.submit(target, dependencies=[])
        self.assertEqual(target.options, {'cores': 32, 'memory': '18g'})

    def test_warn_user_when_submitting_target_with_unsupported_option(self):
        target = Target('TestTarget', inputs=[], outputs=[], options={'foo': 'bar'}, working_dir='/some/dir')
        with self.assertLogs(level='WARNING') as logs:
            self.backend.submit(target, dependencies=[])
            self.assertEqual(logs.output, ['WARNING:gwf.backends.base:Option "foo" used in "TestTarget" is not supported by backend. Ignored.'])

    def test_remove_options_with_none_value(self):
        target = Target('TestTarget', inputs=[], outputs=[], options={}, working_dir='/some/dir')
        self.backend.submit(target, dependencies=[])
        assert target.options == {'cores': 2, 'memory': '18g'}

    def test_raise_exception_if_backend_does_not_implement_all_methods(self):
        with self.assertRaises(BackendError):
            class InvalidTestingBackend(Backend):
                def submit(self, target, dependencies):
                    pass

                def cancel(self, target):
                    pass

                def status(self, target):
                    pass


class TestPersistableDict(GWFTestCase):

    def test_dict_is_empty_if_file_does_not_exist(self):
        d = PersistableDict('test.json')
        self.assertEqual(d, {})

    def test_dict_write_read(self):
        d1 = PersistableDict('/tmp/test.json')
        d1['foo'] = 'bar'
        d1.persist()

        self.assertTrue(os.path.exists('/tmp/test.json'))

        d2 = PersistableDict('/tmp/test.json')
        self.assertEqual(d2, {'foo': 'bar'})

