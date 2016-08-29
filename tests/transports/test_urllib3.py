from urllib3_mock import Responses
from urllib3.exceptions import TimeoutError, MaxRetryError
import pytest
from opbeat.transport.base import TransportException

try:
    import urlparse
except ImportError:
    from urllib import parse as urlparse

from opbeat.transport.http_urllib3 import Urllib3Transport, AsyncUrllib3Transport


responses = Responses('urllib3')

@responses.activate
def test_send():
    transport = Urllib3Transport(urlparse.urlparse('http://localhost'))
    responses.add('POST', '/', status=202,
                  adding_headers={'Location': 'http://example.com/foo'})
    url = transport.send('x', {})
    assert url == 'http://example.com/foo'


@responses.activate
def test_timeout():
    transport = Urllib3Transport(urlparse.urlparse('http://localhost'))
    responses.add('POST', '/', status=202,
                  body=MaxRetryError(None, None, reason=TimeoutError()))
    with pytest.raises(TransportException) as exc_info:
        transport.send('x', {})
    assert 'timeout' in str(exc_info.value)


@responses.activate
def test_http_error():
    url, status, body = (
        'http://localhost:9999', 418, 'Nothing'
    )
    transport = Urllib3Transport(urlparse.urlparse(url))
    responses.add('POST', '/', status=status, body=body)

    with pytest.raises(TransportException) as exc_info:
        transport.send('x', {})
    for val in (status, body):
        assert str(val) in str(exc_info.value)


@responses.activate
def test_generic_error():
    url, status, message, body = (
        'http://localhost:9999', 418, "I'm a teapot", 'Nothing'
    )
    transport = Urllib3Transport(urlparse.urlparse(url))
    responses.add('POST', '/', status=status, body=Exception('Oopsie'))
    with pytest.raises(TransportException) as exc_info:
        transport.send('x', {})
    assert 'Oopsie' in str(exc_info.value)