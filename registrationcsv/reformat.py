import csv
import sys


def main():
    if len(sys.argv) < 2:
        sys.stderr.write("Usage: {} <file.csv>\n".format(sys.argv[1]))
        return 1
    fobj = open(sys.argv[1])
    reformat(fobj, sys.stdout)


def reformat(fobj, fout):
    sniffer = csv.Sniffer()
    dialect = sniffer.sniff(next(iter(fobj)))
    if not dialect:
        raise ValueError("Unable to sniff file")
    fobj.seek(0)

    # Preserve the excel attributes
    for attr in ['quotechar', 'escapechar', 'doublequote', 'skipinitialspace', 'quoting']:
        setattr(dialect, attr, getattr(csv.excel, attr))
    reader = csv.DictReader(fobj, dialect=dialect)
    fields = ["event", "name", "payment_status", "order_total",
              "order_number", "quantity", "email"]
    fields_last = fields[-3:]
    fields_set = set(fields)
    rows_out = []
    for row in reader:
        new_row = {x: row.get(x) for x in fields}
        rows_out.append(new_row)
        new_row['event'] = new_row.pop('name')
        options = parse_options(row.get('options'))
        # Add fields if necessary; hope for an ordered dict
        for opt in options:
            if opt in fields_set:
                continue
            fields.append(opt)
            fields_set.add(opt)
        new_row.update(options)
    # Reorder the fields
    for fname in fields_last:
        fields.remove(fname)
    fields.extend(fields_last)
    rows_out = reorder_rows(rows_out)
    remove_empty_columns(rows_out, fields)

    wr = csv.DictWriter(fout, fields)
    wr.writeheader()
    wr.writerows(rows_out)


def remove_empty_columns(rows_out, fields):
    for fname in fields[:]:
        if any(x.get(fname) for x in rows_out):
            continue
        fields.remove(fname)
        for row in rows_out:
            row.pop(fname, None)


def parse_options(strobj):
    kv = {}
    if not strobj:
        return kv
    arr = [x.strip() for x in strobj.split('\n')]
    for row in arr:
        k, sep, v = row.partition(':')
        if not v:
            continue
        k = k.strip().lower()
        v = v.strip()
        if 'members only' in k:
            k = 'member'
            v = "1" if v else None
        kv[k] = v
    return kv


def reorder_rows(rows_out):
    rows_out = rows_out[:]
    for fname in ["name", "course", "event"]:
        rows_out.sort(key=lambda x: x.get(fname) or '')
    return rows_out


if __name__ == '__main__':
    sys.exit(main())
