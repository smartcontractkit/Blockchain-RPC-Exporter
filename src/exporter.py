"""Main module that loads Prometheus registry and starts a web-server."""
from wsgiref.simple_server import make_server
from prometheus_client import REGISTRY, make_wsgi_app
from metrics import PrometheusCustomCollector


def return200(_, start_fn):
    """Wsgi http response function."""
    start_fn('200 OK', [])
    return [b'Service ok.']


def return404(_, start_fn):
    """Wsgi http response function 404."""
    start_fn('404 Not Found', [])
    return [b'Not implemented.']


def exporter(environ, start_fn):  #pylint: disable=inconsistent-return-statements
    """Web-server endpoints routing."""
    if environ['PATH_INFO'] == '/metrics':
        return metrics_app(environ, start_fn)
    if environ['PATH_INFO'] == '/readiness':
        return return200(environ, start_fn)
    if environ['PATH_INFO'] == '/liveness':
        return return200(environ, start_fn)


if __name__ == '__main__':
    REGISTRY.register(PrometheusCustomCollector())
    metrics_app = make_wsgi_app()
    httpd = make_server('', 8000, exporter)
    httpd.serve_forever()
