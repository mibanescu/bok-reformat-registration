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
        Field("start", css_class="timefield"),
        Field("finish", css_class="timefield"),
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
    def _strip_after_separator(cls, *, sep="~", value):
        if value is None:
            return None
        return value.partition(sep)[0].strip()

    @classmethod
    def csv_to_rows(cls, fobj):
        reader = cls.open_csv(fobj)
        fields = list(cls.Field_Order)
        fields_set = set(x.name for x in fields)
        rows_out = []
        for row in reader:
            new_row = {x.name: row.get(x.name) for x in fields if row.get(x.name)}
            rows_out.append(new_row)
            new_row["event"] = new_row.pop("name")
            options = cls.parse_options(row.get("options"))
            # Add fields if necessary; hope for an ordered dict
            for opt in options:
                if opt in fields_set:
                    continue
                fields.append(Field(opt))
                fields_set.add(opt)
            new_row.update(options)
        fields = cls.reorder_fields(fields)
        rows_out = cls.reorder_rows(rows_out)
        return rows_out, fields

    @classmethod
    def reorder_fields(cls, fields):
        """
        Return the prescribed field order, as well as any additional fields
        """
        ret = list(cls.Field_Order)
        existing = set(x.name for x in cls.Field_Order)
        for field in fields:
            if field.name in existing:
                continue
            ret.append(field)
            existing.add(field.name)
        return ret

    @classmethod
    def remove_empty_columns(cls, rows_out, fields):
        for fname in fields[:]:
            if any(x.get(fname) for x in rows_out):
                continue
            fields.remove(fname)
            for row in rows_out:
                row.pop(fname, None)

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

    @classmethod
    def reorder_rows(cls, rows_out):
        rows_out = rows_out[:]
        for fname in ["name", "course", "event"]:
            rows_out.sort(key=lambda x: x.get(fname) or "")
        return rows_out


if __name__ == "__main__":
    sys.exit(main())
