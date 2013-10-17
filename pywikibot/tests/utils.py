try:
    # Unittest2 is a backport of python 2.7s unittest module to python 2.6
    # Trying to import unittest2 has to happen first because 2.6 does have a
    # unittest module in the standard library but that doesn't support all the
    # features of the one found in python 2.7, so importing unittest first and
    # then trying to figure out if it supports the features used would mean
    # checking the module contents etc. Just catching an ImportError once is
    # much easier.
    import unittest2 as unittest
except ImportError:
    import unittest


def collector():
    # This test collector loads tests from the `tests` directory in files
    # matching the pattern `*tests.py`. This gets used by `setup.py test` when
    # running on Python 2.6 to use the unittest2 test runner instead of the
    # unittest one.
    return unittest.loader.defaultTestLoader.discover("tests", "*tests.py")

from tests import patch_request, unpatch_request


class PywikibotTestCase(unittest.TestCase):
    def assertType(self, obj, cls):
        """Assert that obj is an instance of type cls"""
        return self.assertTrue(isinstance(obj, cls))

    def setUp(self):
        patch_request()

    def tearDown(self):
        unpatch_request()
