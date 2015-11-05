# Very, *very* WIP work on developing a coherent mock for the Tango service.
from httmock import response, urlmatch

from vrfy import settings

NETLOC = settings.TANGO_ADDRESS
HEADERS = {'content-type': 'application/json'}


@urlmatch(netloc=NETLOC + '/open', path='', method='get')
def open(url, request):
    print(url)
    content = 'poot'
    return response(200, content, HEADERS, None, 5, request)
