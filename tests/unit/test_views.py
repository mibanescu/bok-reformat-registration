import unittest
from unittest import mock

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
        self.assertEqual(info["project"], "registrationcsv")

    @mock.patch("registrationcsv.views.default.io")
    @mock.patch("registrationcsv.views.default.Formatter")
    def test_process(self, _Formatter, _io):
        from registrationcsv.views.default import process

        request = testing.DummyRequest()
        field = mock.MagicMock(filename="foo.csv")
        request.POST["csv_file"] = field
        resp = process(request)
        self.assertEqual("text/csv", resp.content_type)
        self.assertEqual("attachment; filename=foo-reformatted.csv", resp.content_disposition)
        self.assertEqual("utf-8", resp.content_encoding)
        self.assertEqual(0, resp.content_length)
        self.assertEqual(_io.StringIO.return_value.getvalue.return_value, resp.body)

        _Formatter.reformat.assert_called_once_with(_io.TextIOWrapper.return_value, _io.StringIO.return_value)
        _io.TextIOWrapper.assert_called_once_with(field.file, encoding="utf-8")
