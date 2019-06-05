import unittest


class FunctionalTests(unittest.TestCase):
    def setUp(self):
        from registrationcsv import main

        app = main({})
        from webtest import TestApp

        self.testapp = TestApp(app)

    def test_root(self):
        res = self.testapp.get("/", status=200)
        self.assertTrue(b"csv_file" in res.body)
