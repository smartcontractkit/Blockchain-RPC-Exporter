import unittest
from src.settings import configuration

import logging

class test_configuration(unittest.TestCase):

    def test_evm_config(self):
        self.configuration = configuration( "tests/test_configuration_evm.yaml", "tests/test_validation.yaml")
        self.assertEqual(self.configuration.isEvm(), True)
        self.assertEqual(self.configuration.blockchain, 'Ethereum')
        

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)

if __name__ == '__main__':
    unittest.main()