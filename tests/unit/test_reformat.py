import io
import unittest
from unittest import mock

from registrationcsv.reformat import Formatter


class Test(unittest.TestCase):
    def test_sniff(self):
        data_in = """\
name;order_total
foo;1"""
        sio = io.StringIO(data_in)
        sout = io.StringIO()
        Formatter.reformat(sio, sout)
        self.assertEqual(
            """\
name,course,start,finish,quantity,more maps,add on,order_total,payment_status,\
member,comments,cell phone,car license & description,event,order_number\r\n\
,,,,,,,1,,,,,,foo,\r\n\
""",
            sout.getvalue(),
        )

    def test_reorder_rows(self):
        data = [
            dict(name="n1", course="c", event="e1"),
            dict(name="n1", course="c", event="e0"),
            dict(name="n0", course="c", event="e1"),
            dict(name="n0", course="c", event="e0"),
            dict(name="n2", course="b", event="e1"),
            dict(name="n2", course="b", event="e0"),
        ]
        reordered = Formatter.reorder_rows(data)
        self.assertEqual([data[5], data[3], data[1], data[4], data[2], data[0]], reordered)

    def test_parse_options(self):
        data = """\
A: a1
b: b1
BOK members only: sure why not
"""
        self.assertEqual({"a": "a1", "b": "b1", "member": "1"}, Formatter.parse_options(data))

    @mock.patch("registrationcsv.reformat.csv")
    def test_parse_data(self, _csv):
        data = [dict(name="event1", options="z:1\nname:elmer\ng:blah")]
        _csv.DictReader.return_value.__iter__.return_value = data
        f_in = io.StringIO("ignore")
        f_out = mock.MagicMock()
        Formatter.reformat(f_in, f_out)

        fields = Formatter.Field_Order + ["z", "g"]
        _csv.DictWriter.assert_called_once_with(f_out, fields)
        _csv.DictWriter.return_value.writerows.assert_called_once_with(
            [dict(event="event1", z="1", g="blah", name="elmer")]
        )
