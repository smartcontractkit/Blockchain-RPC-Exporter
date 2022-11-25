from src.collectors.evm import evm_collector


import unittest
from unittest.mock import MagicMock, call, patch, mock_open
from unittest import mock
from src.settings import configuration, logger


class test_evm_collector(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None
        self.collector = configuration("tests/fixtures/test_configuration.yaml",
                                           "tests/fixtures/test_validation.yaml")

if __name__ == '__main__':
    unittest.main()
