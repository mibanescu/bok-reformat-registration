import csv
import sys

import attr


def main():
    if len(sys.argv) < 2:
        sys.stderr.write("Usage: {} <file.csv>\n".format(sys.argv[1]))
        return 1
    fobj = open(sys.argv[1])
    Formatter.reformat(fobj, sys.stdout)


@attr.s
class Field:
    name = attr.ib()
    display = attr.ib(default=None)
    css_class = attr.ib(default=None)


class Formatter:
    Field_Order = [
        Field("name"),
        Field("course"),
        Field("quantity"),
        Field("more maps"),
        Field("add on"),
        Field("order_total", display="order total"),
        Field("payment_status", display="payment status"),
        Field("member"),
        Field("comments"),
        Field("cell phone"),
        Field("car license & description"),
        Field("event"),
        Field("order_number", display="order#"),
        Field("email"),
    ]

    @classmethod
    def reformat(cls, fobj, fout):
        rows_out, fields = cls.csv_to_rows(fobj)

        wr = csv.DictWriter(fout, [x.name for x in fields])
        wr.writeheader()
        wr.writerows(rows_out)

    @classmethod
    def open_csv(cls, fobj):
        sniffer = csv.Sniffer()
        dialect = sniffer.sniff(next(iter(fobj)))
        if not dialect:
            raise ValueError("Unable to sniff file")
        fobj.seek(0)

        # Preserve the excel attributes
        for attr_name in ["quotechar", "escapechar", "doublequote", "skipinitialspace", "quoting"]:
            setattr(dialect, attr_name, getattr(csv.excel, attr_name))
        reader = csv.DictReader(fobj, dialect=dialect)
        return reader

    @classmethod
    def csv_to_rows(cls, fobj):
        reader = cls.open_csv(fobj)
        coll = RowCollector(list(cls.Field_Order))
        for row in reader:
            coll.process(row)
        fields = cls.reorder_fields(coll.fields)
        rows_out = cls.reorder_rows(coll.rows)
        return rows_out, fields

    @classmethod
    def reorder_fields(cls, fields):
        """
        Return the prescribed field order, as well as any additional fields
        """
        predef_order = {x.name: i for i, x in enumerate(cls.Field_Order)}

        actual_order = {}
        for field in fields:
            rank = predef_order.get(field.name, None)
            if rank is None:
                rank = len(predef_order)
                predef_order[field.name] = rank
            actual_order[rank] = field
        l = sorted(actual_order.items(), key=lambda x: x[0])
        return [x[1] for x in l]

    @classmethod
    def remove_empty_columns(cls, rows_out, fields):
        for fname in fields[:]:
            if any(x.get(fname) for x in rows_out):
                continue
            fields.remove(fname)
            for row in rows_out:
                row.pop(fname, None)

    @classmethod
    def reorder_rows(cls, rows_out):
        rows_out = rows_out[:]
        for fname in ["name", "course", "event"]:
            rows_out.sort(key=lambda x: x.get(fname) or "")
        return rows_out


class RowCollector:
    def __init__(self, fields):
        self.fields = fields
        self.fields_set = set(x.name for x in fields)
        self.rows = []

    def process(self, row):
        if "options" in row:
            return self._process_unexpanded(row)
        self._process_expanded(row)

    def _process_unexpanded(self, row):
        new_row = {x.name: row.get(x.name) for x in self.fields if row.get(x.name)}
        new_row["event"] = new_row.pop("name")
        options = self.parse_options(row.get("options"))
        # Add fields if necessary; hope for an ordered dict
        for opt in options:
            self._record_field(opt)
        new_row.update(options)
        self.rows.append(new_row)

    @classmethod
    def parse_options(cls, strobj):
        kv = {}
        if not strobj:
            return kv
        arr = [x.strip() for x in strobj.split("\n")]
        for row in arr:
            k, sep, v = row.partition(":")
            if not v:
                continue
            k = cls._strip_after_separator(value=k).lower()
            v = cls._strip_after_separator(value=v)
            if "members only" in k:
                k = "member"
                v = "1" if v else None
            kv[k] = v
        return kv

    def reset(self):
        self.fields = []
        self.fields_set.clear()

    def _process_expanded(self, row):
        if len(self.rows) == 0:
            self.reset()
        new_row = {}
        courses = ""
        for k, v in row.items():
            k = self._strip_after_separator(value=k).lower()
            if k == "course":
                courses = v
                continue
            v = self._strip_after_separator(value=v)
            new_row[k] = v
            self._record_field(k)

        map_count = self._get_map_count(new_row)
        courses = (self._strip_after_separator(value=x.strip())
                   for x in courses.split(","))
        for course in courses:
            if course == "":
                continue
            new_row[course] = map_count
            self._record_field(course)

        self.rows.append(new_row)

    def _get_map_count(self, row):
        map_count = row.get("maps", "")
        if map_count == "":
            return 1

        try:
            map_count = int(map_count)
        except ValueError:
            return 1
        return 1 + map_count

    def _record_field(self, f):
        if f in self.fields_set:
            return
        self.fields.append(Field(f))
        self.fields_set.add(f)

    @classmethod
    def _strip_after_separator(cls, *, sep="~", value):
        if value is None:
            return None
        return value.partition(sep)[0].strip()


if __name__ == "__main__":
    sys.exit(main())
