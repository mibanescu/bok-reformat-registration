import csv
import sys


def main():
    if len(sys.argv) < 2:
        sys.stderr.write("Usage: {} <file.csv>\n".format(sys.argv[1]))
        return 1
    fobj = open(sys.argv[1])
    Formatter.reformat(fobj, sys.stdout)


class Formatter:
    Field_Order = [
        "name",
        "course",
        "start",
        "finish",
        "quantity",
        "more maps",
        "add on",
        "order_total",
        "payment_status",
        "member",
        "comments",
        "cell phone",
        "car license & description",
        "event",
        "order_number",
    ]

    @classmethod
    def reformat(cls, fobj, fout):
        rows_out, fields = cls.csv_to_rows(fobj)

        wr = csv.DictWriter(fout, fields)
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
        for attr in ["quotechar", "escapechar", "doublequote", "skipinitialspace", "quoting"]:
            setattr(dialect, attr, getattr(csv.excel, attr))
        reader = csv.DictReader(fobj, dialect=dialect)
        return reader

    @classmethod
    def csv_to_rows(cls, fobj):
        reader = cls.open_csv(fobj)
        fields = list(cls.Field_Order)
        fields_set = set(fields)
        rows_out = []
        for row in reader:
            new_row = {x: row.get(x) for x in fields if row.get(x)}
            rows_out.append(new_row)
            new_row["event"] = new_row.pop("name")
            options = cls.parse_options(row.get("options"))
            # Add fields if necessary; hope for an ordered dict
            for opt in options:
                if opt in fields_set:
                    continue
                fields.append(opt)
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
        existing = set(cls.Field_Order)
        for fname in fields:
            if fname in existing:
                continue
            ret.append(fname)
            existing.add(fname)
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
            k = k.strip().lower()
            v = v.strip()
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
