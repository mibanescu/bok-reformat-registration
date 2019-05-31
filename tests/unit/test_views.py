import unittest

from pyramid import testing


class ViewTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_home(self):
        from registrationcsv.views.default import home
        request = testing.DummyRequest()
        info = home(request)
        self.assertEqual(info['project'], 'registrationcsv')
