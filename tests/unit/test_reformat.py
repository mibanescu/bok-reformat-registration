import csv
import io
import os
import unittest
from pathlib import Path
from unittest import mock

from registrationcsv.reformat import Formatter, RowCollector

_top = os.path.dirname(__file__)


class Test(unittest.TestCase):
    @classmethod
    def open_file(cls, file_name):
        d = Path(_top) / ".." / "fixtures"
        return open(d / file_name)

    @classmethod
    def read_csv(cls, fin):
        return csv.DictReader(fin)

    def test_sniff(self):
        data_in = """\
name;order_total
foo;1"""
        sio = io.StringIO(data_in)
        sout = io.StringIO()
        Formatter.reformat(sio, sout)
        self.assertEqual(
            """\
name,order_total\r\n\
foo,1\r\n\
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
Finger stick ~ every person starting on the course needs one: Rent ~ I don't own one and will rent
"""
        self.assertEqual({"a": "a1", "b": "b1", "member": "1", "finger stick": "Rent"},
                         RowCollector.parse_options(data))

    def test_multicourse_all(self):
        sout = io.StringIO()
        with self.open_file("example1_all.csv") as f:
            Formatter.reformat(f, sout)
        sout.seek(0, 0)

        exp_courses = ["E", "S2"]
        for i, row in enumerate(self.read_csv(sout)):
            self.assertEqual(row["course"], exp_courses[i])

    def test_multicourse_expanded(self):
        sout = io.StringIO()
        with self.open_file("example1_expanded.csv") as f:
            Formatter.reformat(f, sout)
        sout.seek(0, 0)

        exp_rows = [
            {
                'name': 'Boyse',
                'cell phone': '987',
                'entry': 'Pay',
                'stick': 'Rent',
                'stick number': '87654',
                'receiver': 'Rent',
                'whistles': '2',
                'maps': '2',
                'thumb compass': 'Borrow',
                'other adults': 'Ruth',
                'children': 'Puppies',
                'email address': 'Dog House',
                'car': 'Dog Sled',
                'signature': 'Paw',
                'guardian': 'Kiwi',
                'other signature': '',
                'S2': '3',
                'R': '3',
                'DT': '3',
                'DM': '3',
                'E': '',
                'L1': '',
                'L2': '',
                'S1': '',
            },
            {
               'name': 'Joseph',
               'cell phone': '999-087-8779',
               'entry': 'Pass',
               'stick': 'Have',
               'stick number': '887665',
               'receiver': 'Have',
               'whistles': 'Have',
               'maps': '0',
               'thumb compass': 'Have',
               'other adults': 'Kiwi',
               'children': 'Boyse',
               'email address': 'test@test.com',
               'car': '98uy6',
               'signature': 'JGH',
               'guardian': 'Ruth',
               'other signature': 'KH',
               'S2': '',
               'R': '',
               'DT': '',
               'DM': '',
               'E': '1',
               'L1': '1',
               'L2': '1',
               'S1': '1',
           },
        ]
        for i, row in enumerate(self.read_csv(sout)):
            self.assertEqual(row, exp_rows[i])

    @mock.patch("registrationcsv.reformat.csv")
    def test_parse_data(self, _csv):
        data = [dict(name="event1", options="z:1\nname:elmer\ng:blah")]
        _csv.DictReader.return_value.__iter__.return_value = data
        f_in = io.StringIO("ignore")
        f_out = mock.MagicMock()
        Formatter.reformat(f_in, f_out)

        fields = [x.name for x in Formatter.Field_Order] + ["z", "g"]
        _csv.DictWriter.assert_called_once_with(f_out, fields)
        _csv.DictWriter.return_value.writerows.assert_called_once_with(
            [dict(event="event1", z="1", g="blah", name="elmer")]
        )
