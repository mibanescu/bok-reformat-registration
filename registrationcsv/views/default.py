import io
import logging
import os

from pyramid.response import Response
from pyramid.view import view_config

from .. import reformat

log = logging.getLogger(__name__)


@view_config(route_name="home", renderer="../templates/home.jinja2")
def home(request):
    return {"project": "registrationcsv"}


@view_config(route_name="process", renderer="")
def process(request):
    encoding = "utf-8"
    field = request.POST["csv_file"]
    ftxt = io.TextIOWrapper(field.file, encoding=encoding)
    fout = io.StringIO()
    reformat.reformat(ftxt, fout)
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
