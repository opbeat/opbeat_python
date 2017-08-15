from opbeat.utils import get_url_dict
from opbeat.utils.wsgi import get_environ, get_headers


def get_data_from_request(request):
    result = {
        'body': request.data,
        'env': dict(get_environ(request.environ)),
        'headers': dict(
            get_headers(request.environ),
        ),
        'method': request.method,
        'socket': {
            'remote_address': request.environ.get('REMOTE_ADDR'),
            'encrypted': request.is_secure()
        },
        'cookies': request.cookies,
    }

    result['url'] = get_url_dict(request.url)

    return result
