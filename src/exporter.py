"""Main module that loads Prometheus registry and starts a web-server."""
import threading
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


def exporter(environ, start_fn):  # pylint: disable=inconsistent-return-statements
    """Web-server endpoints routing."""
    match environ['PATH_INFO']:
        case '/metrics':
            return metrics_app(environ, start_fn)
        case _:
            return return404(environ, start_fn)

def liveness(environ, start_fn):
    """Liveness endpoint function"""
    match environ['PATH_INFO']:
        case '/readiness':
            return return200(environ, start_fn)
        case '/liveness':
            return return200(environ, start_fn)

def start_liveness():
    """Liveness thread function"""
    httpd_liveness = make_server('', 8001, liveness)
    httpd_liveness.serve_forever()

if __name__ == '__main__':
    REGISTRY.register(PrometheusCustomCollector())
    metrics_app = make_wsgi_app()
    liveness_thread = threading.Thread(target=start_liveness)
    liveness_thread.start()
    httpd = make_server('', 8000, exporter)
    httpd.serve_forever()
