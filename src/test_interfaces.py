#pylint: disable=protected-access,invalid-name

"""Module for testing interfaces"""

from unittest import TestCase
from interfaces import HttpsInterface
import requests_mock


class TestConfiguration(TestCase):
    """Tests HttpsInterface interface."""

    def setUp(self):
        """Set up dummy interface for us."""
        self.maxDiff = None
        self.url = "mock://test.com"
        self.interface = HttpsInterface(self.url, 1, 2)

    @requests_mock.Mocker()
    def test(self, m):
        response_text  = '{"result":{"chain":"main","blocks":767217,"headers":767217,"bestblockhash":"000000000000000000003a0f6d9ef90eddb69bf8790f2b36175f271623d5ef13","difficulty":34244331613176.18,"time":1670937930,"mediantime":1670935650,"verificationprogress":0.9999995228987372,"initialblockdownload":false,"chainwork":"00000000000000000000000000000000000000003b7286459d348b523901a694","size_on_disk":503489280915,"pruned":false,"warnings":""},"error":null,"id":"exporter"}'
        m.post(self.url, text=response_text)

        final_result = {'chain': 'main', 'blocks': 767217, 'headers': 767217, 'bestblockhash': '000000000000000000003a0f6d9ef90eddb69bf8790f2b36175f271623d5ef13', 'difficulty': 34244331613176.18, 'time': 1670937930, 'mediantime': 1670935650, 'verificationprogress': 0.9999995228987372, 'initialblockdownload': False, 'chainwork': '00000000000000000000000000000000000000003b7286459d348b523901a694', 'size_on_disk': 503489280915, 'pruned': False, 'warnings': ''}
        self.assertEqual(self.interface.json_rpc_post('demo'), final_result)
