"""Tests the exporter module"""
from unittest import TestCase, mock

from exporter import return200, return404, exporter, liveness


class TestExporter(TestCase):
    """Tests the exporter without running a server"""

    def setUp(self):
        # Mock the start_fn function as there is no wsgi app created
        self.start_fn_mock = mock.Mock()

    def test_return_200_return(self):
        """Tests the return of the return200 function"""
        self.assertEqual([b'Service ok.'], return200(None, self.start_fn_mock))

    def test_return_200_start_fn_call(self):
        """Tests that return200 starts an HTTP response with correct status code and headers"""
        return200(None, self.start_fn_mock)
        self.start_fn_mock.assert_called_once_with('200 OK', [])

    def test_return_404_return(self):
        """Tests the return of the return404 function"""
        self.assertEqual([b'Not implemented.'],
                         return404(None, self.start_fn_mock))

    def test_return_404_start_fn_call(self):
        """Tests that return404 starts an HTTP response with correct status code and headers"""
        return404(None, self.start_fn_mock)
        self.start_fn_mock.assert_called_once_with('404 Not Found', [])

    def test_exporter_readiness(self):
        """Tests that the readiness path invokes return200
        with the environ and HTTP response callable"""
        environ = {'PATH_INFO': '/readiness'}
        with mock.patch('liveness.return200') as mocked:
            liveness(environ, self.start_fn_mock)
            mocked.assert_called_once_with(environ, self.start_fn_mock)

    def test_exporter_liveness(self):
        """Tests that the liveness path invokes return200
        with the environ and HTTP response callable"""
        environ = {'PATH_INFO': '/liveness'}
        with mock.patch('liveness.return200') as mocked:
            liveness(environ, self.start_fn_mock)
            mocked.assert_called_once_with(environ, self.start_fn_mock)

    def test_exporter_404(self):
        """Tests that an unknown path invokes return404
        with the environ and HTTP response callable"""
        environ = {'PATH_INFO': '/dummypath'}
        with mock.patch('exporter.return404') as mocked:
            exporter(environ, self.start_fn_mock)
            mocked.assert_called_once_with(environ, self.start_fn_mock)

    def test_exporter_metrics_path(self):
        """Tests that the metrics path invokes metrics_app
        with the environ and HTTP response callable"""
        environ = {'PATH_INFO': '/metrics'}
        with mock.patch('exporter.metrics_app', create=True) as mocked:
            exporter(environ, self.start_fn_mock)
            mocked.assert_called_once_with(environ, self.start_fn_mock)
