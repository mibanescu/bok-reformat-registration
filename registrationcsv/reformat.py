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
    fields = ["event", "email", "name", "order_total"]
    fields_set = set(fields)
    ret = []
    for row in reader:
        new_row = {x: row.get(x) for x in fields}
        ret.append(new_row)
        new_row['event'] = new_row.pop('name')
        options = parse_options(row['options'])
        # Add fields if necessary
        for opt in set(options).difference(fields_set):
            fields.append(opt)
            fields_set.add(opt)
        new_row.update(options)
    wr = csv.DictWriter(fout, fields)
    wr.writeheader()
    wr.writerows(ret)


def parse_options(strobj):
    arr = [x.strip() for x in strobj.split('\n')]
    kv = {}
    for row in arr:
        k, sep, v = row.partition(':')
        if not v:
            continue
        k = k.lower()
        if 'members only' in k:
            k = 'member'
            v = "1" if v else None
        kv[k] = v
    return kv


if __name__ == '__main__':
    sys.exit(main())
