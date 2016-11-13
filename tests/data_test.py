# -*- coding: utf-8 -*-
#!/bin/env/python3 

from .context import FlashPy

import unittest

class DataTestSuite(unittest.TestCase):
    """Basic tests for the Data object in FlashPy
    """

    def test_basic(self):
        self.assertEqual(1, 1)
        self.assertTrue(True)

    def test_key(self):
        data = FlashPy.Data('tests/key_test')

        
        self.assertEqual(data.get_keys(), ['ones'])


if __name__ == '__main__':
    unittest.main()
