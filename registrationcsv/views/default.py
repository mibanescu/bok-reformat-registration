from pyramid.response import Response
from pyramid.view import view_config
import logging

log = logging.getLogger(__name__)


@view_config(route_name='home', renderer='../templates/home.jinja2')
def home(request):
    return {'project': 'registrationcsv'}


@view_config(route_name='process', renderer='')
def process(request):
    fstg = request.POST['csv_file']
    data = fstg.file.read()
    return Response(
        content_type="text/csv",
        content_disposition="attachment; filename=bar.csv",
        content_encoding="binary",
        content_length=len(data),
        body=data)
