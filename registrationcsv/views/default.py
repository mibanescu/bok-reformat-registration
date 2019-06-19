import io
import logging
import os

from pyramid.renderers import render_to_response
from pyramid.response import Response
from pyramid.view import view_config

from ..reformat import Formatter

log = logging.getLogger(__name__)


@view_config(route_name="home", renderer="../templates/home.jinja2")
def home(request):
    return {"project": "registrationcsv"}


@view_config(route_name="process", renderer="")
def process(request):
    encoding = "utf-8"
    field = request.POST["csv_file"]
    ftxt = io.TextIOWrapper(field.file, encoding=encoding)
    if "return_as_table" in request.POST:
        return process_as_table(request, ftxt)
    fout = io.StringIO()
    Formatter.reformat(ftxt, fout)
    data = fout.getvalue()
    basename, extname = os.path.splitext(field.filename)
    fname = "{}-reformatted{}".format(basename, extname)
    return Response(
        content_type="text/csv",
        content_disposition="attachment; filename={}".format(fname),
        content_encoding=encoding,
        content_length=len(data),
        body=data,
    )


def process_as_table(request, fobj):
    rows, fields = Formatter.csv_to_rows(fobj)
    return render_to_response("../templates/as_table.jinja2", dict(fields=fields, rows=rows), request=request)
